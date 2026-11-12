"""Assegna un paper candidato a un filone esistente, o lo marca come ambiguo."""
import re

CARTELLA_AMBIGUI = "Da categorizzare"


def _punteggio(testo: str, parole_chiave: list[str]) -> int:
    """Conta le parole chiave trovate come parola intera (confini di parola),
    non come semplice sottostringa: altrimenti "RAN" matcherebbe dentro
    "warranted", "MAC" dentro "format", eccetera."""
    testo = testo.lower()
    return sum(1 for p in parole_chiave if re.search(rf"\b{re.escape(p.lower())}\b", testo))


def e_in_tema(titolo: str, abstract: str | None, parole_forti: list[str], parole_ambigue: list[str], parole_contesto: list[str]) -> bool:
    """Un paper è in tema se contiene una parola forte (inequivocabile), oppure
    una parola ambigua (corta/generica, es. "satellite") confermata da una
    parola di contesto telecom/networking: evita falsi positivi come un paper
    di biologia che contiene "satellite" ma nulla legato a reti o comunicazioni.
    """
    testo = f"{titolo} {abstract or ''}"
    if _punteggio(testo, parole_forti) > 0:
        return True
    return _punteggio(testo, parole_ambigue) > 0 and _punteggio(testo, parole_contesto) > 0


def classifica(titolo: str, abstract: str | None, filoni: dict[str, list[str]], cartella_ambigui: str = CARTELLA_AMBIGUI) -> str:
    testo = f"{titolo} {abstract or ''}"
    punteggi = {nome: _punteggio(testo, parole) for nome, parole in filoni.items()}
    ordinati = sorted(punteggi.items(), key=lambda kv: kv[1], reverse=True)

    migliore, punteggio_migliore = ordinati[0]
    secondo_punteggio = ordinati[1][1] if len(ordinati) > 1 else 0

    if punteggio_migliore == 0:
        return cartella_ambigui
    if secondo_punteggio >= punteggio_migliore:
        return cartella_ambigui
    return migliore
