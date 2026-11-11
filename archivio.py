"""Legge e aggiorna l'archivio esistente (cartelle PDF + Excel), con le stesse
convenzioni già usate da controlla_excel_e_cartelle.py: colonna Filone = nome
della cartella, colonna File = percorso relativo "Filone/nome.pdf" con link
URL-encoded.
"""
from pathlib import Path
from urllib.parse import quote

import openpyxl
from openpyxl.styles import Font

from util import normalizza_titolo

CARTELLA_PAPER_SCIENTIFICI = Path(__file__).resolve().parent.parent
XLSX = CARTELLA_PAPER_SCIENTIFICI / "Confronto_paper_vs_tesi.xlsx"
LOCK = CARTELLA_PAPER_SCIENTIFICI / ".~lock.Confronto_paper_vs_tesi.xlsx#"

FOGLIO_LETTERATURA = "Tabella letteratura"
FOGLIO_PRO_CONTRO = "Pro-Contro per paper"
FOGLIO_DA_RECUPERARE = "Da recuperare"


def excel_bloccato() -> bool:
    return LOCK.exists()


class Archivio:
    """Indice di ciò che è già presente, per il dedup, più le operazioni di
    scrittura di nuove righe. Non tocca l'Excel finché non si chiama save()."""

    def __init__(self):
        self.wb = openpyxl.load_workbook(XLSX)
        # Nei fogli esistenti il titolo è scritto in formati diversi e non isolato
        # (prima riga di una cella multi-riga, oppure tra virgolette dentro una
        # citazione completa): il confronto è per sottostringa normalizzata, non
        # per uguaglianza esatta.
        self.testi_noti: list[str] = []
        self._carica_noti()

    def _carica_noti(self) -> None:
        for nome_foglio, col_titolo in (
            (FOGLIO_LETTERATURA, "D"),
            (FOGLIO_PRO_CONTRO, "C"),
            (FOGLIO_DA_RECUPERARE, "A"),
        ):
            if nome_foglio not in self.wb.sheetnames:
                continue
            ws = self.wb[nome_foglio]
            for riga in ws.iter_rows(min_row=1, max_col=ord(col_titolo) - ord("A") + 1):
                v = riga[ord(col_titolo) - ord("A")].value
                if not isinstance(v, str):
                    continue
                t = normalizza_titolo(v)
                # scarta intestazioni di colonna e altri testi troppo corti per
                # essere un titolo vero (es. "Paper", "Filone"): altrimenti
                # qualunque candidato che contenga quella parola risulterebbe
                # un falso duplicato.
                if len(t) >= 20:
                    self.testi_noti.append(t)

    def gia_presente(self, titolo: str) -> bool:
        t = normalizza_titolo(titolo)
        if len(t) < 20:
            return False
        return any(t in testo for testo in self.testi_noti)

    def registra_titolo(self, titolo: str) -> None:
        self.testi_noti.append(normalizza_titolo(titolo))

    def aggiungi_a_tabella_letteratura(self, filone: str, autore_anno: str, titolo_sede: str, file_rel: str) -> None:
        ws = self.wb[FOGLIO_LETTERATURA]
        riga = ws.max_row + 1
        ws[f"B{riga}"] = filone
        ws[f"C{riga}"] = autore_anno
        ws[f"D{riga}"] = titolo_sede
        cella_file = ws[f"I{riga}"]
        cella_file.value = file_rel
        cella_file.hyperlink = quote(file_rel)
        cella_file.font = Font(color="0563C1", underline="single")
        self.registra_titolo(titolo_sede)

    def aggiungi_a_da_recuperare(self, titolo: str, link: str, motivo: str) -> None:
        if FOGLIO_DA_RECUPERARE not in self.wb.sheetnames:
            self.wb.create_sheet(FOGLIO_DA_RECUPERARE)
            ws = self.wb[FOGLIO_DA_RECUPERARE]
            ws["A1"], ws["B1"], ws["C1"] = "Paper", "Perché è pertinente", "Stato"
        ws = self.wb[FOGLIO_DA_RECUPERARE]
        riga = ws.max_row + 1
        ws[f"A{riga}"] = titolo
        ws[f"B{riga}"] = link
        ws[f"C{riga}"] = motivo
        self.registra_titolo(titolo)

    def save(self) -> None:
        self.wb.save(XLSX)
