"""Funzioni di supporto condivise tra i moduli dello scanner."""
import re
import unicodedata


def normalizza_titolo(titolo: str) -> str:
    """Riduce un titolo a una forma confrontabile: minuscolo, senza accenti/punteggiatura."""
    t = unicodedata.normalize("NFKD", titolo).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-z0-9]+", " ", t.lower())
    return " ".join(t.split())


def indovina_editore(doi: str | None) -> str | None:
    if not doi:
        return None
    prefisso = doi.split("/")[0]
    if prefisso == "10.1109":
        return "ieee"
    if prefisso == "10.1016":
        return "elsevier"
    return None


def cognome_primo_autore(autori: list[str]) -> str:
    if not autori:
        return "sconosciuto"
    primo = autori[0].strip()
    cognome = primo.split()[-1] if " " in primo else primo
    cognome = re.sub(r"[^A-Za-zÀ-ÿ'-]", "", cognome)
    return cognome.lower() or "sconosciuto"


def nome_file_pdf(autori: list[str], anno: int | None, titolo: str) -> str:
    """Nome file nello stesso stile usato nell'archivio esistente: autoreAnno,
    per esempio "volk2024.pdf" (il titolo non entra nel nome del file)."""
    anno_s = str(anno) if anno else "sd"
    return f"{cognome_primo_autore(autori)}{anno_s}.pdf"
