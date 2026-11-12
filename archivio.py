"""Due modi di tenere traccia di cosa è già in archivio e di cosa viene
trovato: con l'Excel specifico di chi scrive questo tool (ArchivioExcel), o
con un semplice file JSON per chiunque non abbia quell'Excel (ArchivioSemplice).
scan_paper.py usa sempre la stessa interfaccia, qualunque sia il caso:
gia_presente, registra_scaricato, registra_da_recuperare, salva, bloccato.
"""
import json
from pathlib import Path
from urllib.parse import quote

from util import normalizza_titolo

LUNGHEZZA_MINIMA_TITOLO = 20  # sotto questa soglia è quasi certo un'intestazione di colonna, non un titolo vero


def crea_archivio(cartella_archivio: Path, percorso_excel: Path | None):
    if percorso_excel and percorso_excel.exists():
        return ArchivioExcel(percorso_excel)
    return ArchivioSemplice(cartella_archivio)


class ArchivioSemplice:
    """Nessun Excel richiesto: un file JSON nascosto nella cartella
    dell'archivio tiene i titoli già visti, e un file Markdown leggibile
    elenca i paper trovati ma non scaricati."""

    def __init__(self, cartella_archivio: Path):
        self.file_json = cartella_archivio / ".archivio_scanner.json"
        self.file_da_recuperare = cartella_archivio / "Da recuperare.md"
        dati = json.loads(self.file_json.read_text(encoding="utf-8")) if self.file_json.exists() else {}
        self.testi_noti: list[str] = dati.get("titoli_noti", [])
        self.da_recuperare: list[dict] = dati.get("da_recuperare", [])

    def gia_presente(self, titolo: str) -> bool:
        t = normalizza_titolo(titolo)
        if len(t) < LUNGHEZZA_MINIMA_TITOLO:
            return False
        return any(t in testo for testo in self.testi_noti)

    def registra_scaricato(self, filone: str, autore_anno: str, titolo_sede: str, file_rel: str) -> None:
        self.testi_noti.append(normalizza_titolo(titolo_sede))

    def registra_da_recuperare(self, titolo: str, link: str, motivo: str) -> None:
        self.testi_noti.append(normalizza_titolo(titolo))
        self.da_recuperare.append({"titolo": titolo, "link": link, "motivo": motivo})

    def salva(self) -> None:
        self.file_json.write_text(
            json.dumps({"titoli_noti": self.testi_noti, "da_recuperare": self.da_recuperare}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        righe = ["# Da recuperare\n", "Paper trovati pertinenti ma non scaricati automaticamente.\n"]
        for p in self.da_recuperare:
            righe.append(f"\n- **{p['titolo']}**\n  - link: {p['link']}\n  - motivo: {p['motivo']}\n")
        self.file_da_recuperare.write_text("".join(righe), encoding="utf-8")

    def bloccato(self) -> bool:
        return False


class ArchivioExcel:
    """Per chi usa (come l'autore) un Excel di tracciamento con i fogli
    "Tabella letteratura", "Pro-Contro per paper" e "Da recuperare". Stessa
    convenzione già usata da controlla_excel_e_cartelle.py: colonna Filone =
    nome della cartella, colonna File = percorso relativo "Filone/nome.pdf"
    con link URL-encoded.
    """

    FOGLIO_LETTERATURA = "Tabella letteratura"
    FOGLIO_PRO_CONTRO = "Pro-Contro per paper"
    FOGLIO_DA_RECUPERARE = "Da recuperare"

    def __init__(self, percorso_excel: Path):
        import openpyxl

        self.percorso = percorso_excel
        self.lock = percorso_excel.parent / f".~lock.{percorso_excel.name}#"
        self.wb = openpyxl.load_workbook(percorso_excel)
        # Nei fogli esistenti il titolo è scritto in formati diversi e non isolato
        # (prima riga di una cella multi-riga, oppure tra virgolette dentro una
        # citazione completa): il confronto è per sottostringa normalizzata, non
        # per uguaglianza esatta.
        self.testi_noti: list[str] = []
        self._carica_noti()

    def _carica_noti(self) -> None:
        for nome_foglio, col_titolo in (
            (self.FOGLIO_LETTERATURA, "D"),
            (self.FOGLIO_PRO_CONTRO, "C"),
            (self.FOGLIO_DA_RECUPERARE, "A"),
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
                if len(t) >= LUNGHEZZA_MINIMA_TITOLO:
                    self.testi_noti.append(t)

    def gia_presente(self, titolo: str) -> bool:
        t = normalizza_titolo(titolo)
        if len(t) < LUNGHEZZA_MINIMA_TITOLO:
            return False
        return any(t in testo for testo in self.testi_noti)

    def registra_scaricato(self, filone: str, autore_anno: str, titolo_sede: str, file_rel: str) -> None:
        from openpyxl.styles import Font

        ws = self.wb[self.FOGLIO_LETTERATURA]
        riga = ws.max_row + 1
        ws[f"B{riga}"] = filone
        ws[f"C{riga}"] = autore_anno
        ws[f"D{riga}"] = titolo_sede
        cella_file = ws[f"I{riga}"]
        cella_file.value = file_rel
        cella_file.hyperlink = quote(file_rel)
        cella_file.font = Font(color="0563C1", underline="single")
        self.testi_noti.append(normalizza_titolo(titolo_sede))

    def registra_da_recuperare(self, titolo: str, link: str, motivo: str) -> None:
        if self.FOGLIO_DA_RECUPERARE not in self.wb.sheetnames:
            self.wb.create_sheet(self.FOGLIO_DA_RECUPERARE)
            ws = self.wb[self.FOGLIO_DA_RECUPERARE]
            ws["A1"], ws["B1"], ws["C1"] = "Paper", "Perché è pertinente", "Stato"
        ws = self.wb[self.FOGLIO_DA_RECUPERARE]
        riga = ws.max_row + 1
        ws[f"A{riga}"] = titolo
        ws[f"B{riga}"] = link
        ws[f"C{riga}"] = motivo
        self.testi_noti.append(normalizza_titolo(titolo))

    def salva(self) -> None:
        self.wb.save(self.percorso)

    def bloccato(self) -> bool:
        return self.lock.exists()
