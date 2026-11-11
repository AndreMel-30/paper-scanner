"""Assegna un paper candidato a un filone esistente, o lo marca come ambiguo."""

CARTELLA_AMBIGUI = "Da categorizzare"


def _punteggio(testo: str, parole_chiave: list[str]) -> int:
    testo = testo.lower()
    return sum(1 for p in parole_chiave if p.lower() in testo)


def e_in_tema(titolo: str, abstract: str | None, parole_chiave_generali: list[str]) -> bool:
    testo = f"{titolo} {abstract or ''}"
    return _punteggio(testo, parole_chiave_generali) > 0


def classifica(titolo: str, abstract: str | None, filoni: dict[str, list[str]]) -> str:
    testo = f"{titolo} {abstract or ''}"
    punteggi = {nome: _punteggio(testo, parole) for nome, parole in filoni.items()}
    ordinati = sorted(punteggi.items(), key=lambda kv: kv[1], reverse=True)

    migliore, punteggio_migliore = ordinati[0]
    secondo_punteggio = ordinati[1][1] if len(ordinati) > 1 else 0

    if punteggio_migliore == 0:
        return CARTELLA_AMBIGUI
    if secondo_punteggio >= punteggio_migliore:
        return CARTELLA_AMBIGUI
    return migliore
