#!/usr/bin/env python3
"""Scansiona le fonti web configurate per nuovi paper pertinenti alla ricerca
su NTN/5G satellitare/O-RAN, li scarica quando possibile e li integra
nell'archivio in Paper scientifici/. Vedi README.md per l'uso.

IEEE Xplore e ScienceDirect (Elsevier) non vengono MAI scaricati in automatico:
i contratti di licenza istituzionali vietano quasi sempre il download
sistematico, anche con credenziali valide. Quando un paper pertinente è
disponibile solo lì, il tool apre la pagina nel browser predefinito perché
l'utente lo scarichi a mano con un clic, come farebbe comunque.
"""
import argparse
import subprocess
import sys
import webbrowser
from pathlib import Path

import yaml

import archivio
import classificatore
import downloader
import recap
from sources import arxiv, crossref, semantic_scholar, unpaywall
from util import indovina_editore, nome_file_pdf, normalizza_titolo

QUI = Path(__file__).resolve().parent
CARTELLA_PAPER_SCIENTIFICI = QUI.parent


def carica_config() -> dict:
    with open(QUI / "config.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    locale = QUI / "config.locale.yaml"
    if locale.exists():
        with open(locale, encoding="utf-8") as f:
            cfg.update(yaml.safe_load(f) or {})
    return cfg


def autore_anno(autori: list[str], anno) -> str:
    if not autori:
        return str(anno) if anno else "n.d."
    primo = autori[0]
    suffisso = " et al." if len(autori) > 1 else ""
    return f"{primo}{suffisso}, {anno}" if anno else f"{primo}{suffisso}"


def raccogli_candidati(cfg: dict, giorni: int) -> list[dict]:
    email = cfg["contatto_email"]
    tutte_le_venue = [v for gruppo in cfg["venues"].values() for v in gruppo]
    parole_generali = cfg["parole_chiave_generali"]

    candidati = []

    print(f"Interrogo Crossref su {len(tutte_le_venue)} venue...")
    for venue in tutte_le_venue:
        candidati += crossref.cerca(venue, giorni, email)

    print(f"Interrogo Semantic Scholar su {len(parole_generali)} parole chiave...")
    chiave_ss = cfg.get("semantic_scholar_api_key")
    for parola in parole_generali:
        candidati += semantic_scholar.cerca(parola, api_key=chiave_ss)

    print("Interrogo arXiv...")
    parole = " OR ".join(f'all:"{p}"' for p in parole_generali)
    categorie = " OR ".join(f"cat:{c}" for c in cfg.get("arxiv_categorie", []))
    query_arxiv = f"({parole}) AND ({categorie})" if categorie else parole
    candidati += arxiv.cerca(query_arxiv, giorni)

    # dedup all'interno del lotto appena raccolto, per DOI poi per titolo
    visti_doi, visti_titolo, unici = set(), set(), []
    for c in candidati:
        chiave_doi = (c.get("doi") or "").lower()
        if chiave_doi and chiave_doi in visti_doi:
            continue
        chiave_titolo = normalizza_titolo(c["titolo"])
        if chiave_titolo in visti_titolo:
            continue
        if chiave_doi:
            visti_doi.add(chiave_doi)
        visti_titolo.add(chiave_titolo)
        unici.append(c)
    return unici


def trova_copia_aperta(c: dict, dest_path: Path, email: str) -> bool:
    """Prova solo le fonti ad accesso aperto (mai IEEE/ScienceDirect)."""
    pdf_oa = c.get("pdf_oa_url")
    if pdf_oa and downloader.scarica_url(pdf_oa, dest_path):
        return True

    link_unpaywall = unpaywall.trova_pdf_oa(c.get("doi"), email)
    if link_unpaywall and downloader.scarica_url(link_unpaywall, dest_path):
        return True

    if c.get("arxiv_id"):
        if downloader.scarica_url(f"https://arxiv.org/pdf/{c['arxiv_id']}.pdf", dest_path):
            return True

    return False


def esegui_scansione(cfg: dict, giorni: int, dry_run: bool) -> None:
    email = cfg["contatto_email"]
    max_browser = cfg.get("max_pagine_aperte_nel_browser", 5)
    candidati = raccogli_candidati(cfg, giorni)

    arch = archivio.Archivio()
    scaricati, da_recuperare = [], []
    scartati_duplicati = 0
    pagine_aperte = 0

    for c in candidati:
        if not classificatore.e_in_tema(c["titolo"], c.get("abstract"), cfg["parole_chiave_generali"]):
            continue
        if arch.gia_presente(c["titolo"]):
            scartati_duplicati += 1
            continue

        filone = classificatore.classifica(c["titolo"], c.get("abstract"), cfg["filoni"])
        nome_file = nome_file_pdf(c["autori"], c["anno"], c["titolo"])
        dest_path = CARTELLA_PAPER_SCIENTIFICI / filone / nome_file
        if dest_path.exists():
            base, suffisso = nome_file[:-4], 2
            while dest_path.exists():
                nome_file = f"{base}-{suffisso}.pdf"
                dest_path = CARTELLA_PAPER_SCIENTIFICI / filone / nome_file
                suffisso += 1
        file_rel = f"{filone}/{nome_file}"

        if dry_run:
            scaricati.append({
                "titolo": c["titolo"], "autore_anno": autore_anno(c["autori"], c["anno"]),
                "fonte": c["fonte"], "filone": filone, "file_rel": file_rel + " (dry-run, non scaricato)",
            })
            continue

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        riuscito = trova_copia_aperta(c, dest_path, email)

        if riuscito:
            aa = autore_anno(c["autori"], c["anno"])
            titolo_sede = f"{c['titolo']} ({c.get('venue') or 'n.d.'})"
            arch.aggiungi_a_tabella_letteratura(filone, aa, titolo_sede, file_rel)
            scaricati.append({
                "titolo": c["titolo"], "autore_anno": aa, "fonte": c["fonte"],
                "filone": filone, "file_rel": file_rel,
            })
            continue

        link = c.get("url") or (f"https://doi.org/{c['doi']}" if c.get("doi") else None)
        editore = indovina_editore(c.get("doi"))
        if editore in ("ieee", "elsevier") and link:
            if pagine_aperte < max_browser:
                webbrowser.open(link)
                pagine_aperte += 1
                motivo = f"solo su {editore} (paywall): pagina aperta nel browser, scaricalo a mano"
            else:
                motivo = f"solo su {editore} (paywall): limite di pagine auto-aperte raggiunto, apri il link a mano"
        else:
            motivo = "nessuna copia open-access trovata"

        arch.aggiungi_a_da_recuperare(c["titolo"], link or "n.d.", motivo)
        da_recuperare.append({"titolo": c["titolo"], "link": link, "motivo": motivo})

    if not dry_run:
        if archivio.excel_bloccato():
            print("\nATTENZIONE: il foglio Excel è aperto (lock file presente).")
            print("I PDF scaricati sono salvati, ma l'Excel NON è stato aggiornato.")
            print("Chiudi il foglio e rilancia per registrare le nuove righe.")
        else:
            arch.save()
            print("\nExcel aggiornato. Eseguo la verifica di coerenza cartelle/Excel...")
            risultato = subprocess.run(
                [sys.executable, "controlla_excel_e_cartelle.py", "--correggi"],
                cwd=CARTELLA_PAPER_SCIENTIFICI,
            )
            if risultato.returncode != 0:
                print("Attenzione: controlla_excel_e_cartelle.py ha segnalato un problema (vedi sopra).")

    recap.stampa(scaricati, da_recuperare, scartati_duplicati, len(candidati), dry_run=dry_run)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="mostra cosa farebbe senza scaricare né modificare l'Excel")
    ap.add_argument("--since-days", type=int, default=None, help="finestra temporale in giorni (sovrascrive config.yaml)")
    args = ap.parse_args()

    cfg = carica_config()
    giorni = args.since_days or cfg["finestra_giorni"]
    esegui_scansione(cfg, giorni, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
