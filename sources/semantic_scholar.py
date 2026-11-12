"""Ricerca su Semantic Scholar: arricchisce Crossref con abstract e link al PDF
open-access quando esiste, oltre all'ID arXiv se il paper ha anche un preprint.

Anche con una API key dedicata il rate limit ufficiale è di 1 richiesta al
secondo cumulativa su tutti gli endpoint, e nella pratica una key appena
emessa può restituire ancora qualche 429 (rate limit) per un po' prima di
funzionare a regime: tra una chiamata e l'altra si aspetta un po', e se
scatta comunque il limite si riprova con pause via via più lunghe
(exponential backoff) prima di rinunciare a quella parola chiave.
"""
import time

import requests

API = "https://api.semanticscholar.org/graph/v1/paper/search"
CAMPI = "title,abstract,year,venue,externalIds,openAccessPdf,url,authors"
PAUSA_TRA_CHIAMATE_S = 3
PAUSE_RETRY_429_S = (10, 30, 60)


def cerca(parola_chiave: str, righe: int = 50, api_key: str | None = None) -> list[dict]:
    parametri = {"query": parola_chiave, "limit": righe, "fields": CAMPI}
    headers = {"x-api-key": api_key} if api_key else {}
    try:
        r = requests.get(API, params=parametri, headers=headers, timeout=20)
        for pausa in PAUSE_RETRY_429_S:
            if r.status_code != 429:
                break
            time.sleep(pausa)
            r = requests.get(API, params=parametri, headers=headers, timeout=20)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"  [semantic scholar] errore su '{parola_chiave}': {e}")
        return []
    finally:
        time.sleep(PAUSA_TRA_CHIAMATE_S)

    risultati = []
    for item in r.json().get("data", []):
        titolo = item.get("title")
        if not titolo:
            continue
        esterni = item.get("externalIds") or {}
        oa = item.get("openAccessPdf") or {}
        autori = [a["name"] for a in (item.get("authors") or []) if a.get("name")]
        risultati.append({
            "doi": esterni.get("DOI"),
            "titolo": titolo,
            "autori": autori,
            "anno": item.get("year"),
            "venue": item.get("venue"),
            "abstract": item.get("abstract"),
            "url": item.get("url"),
            "arxiv_id": esterni.get("ArXiv"),
            "pdf_oa_url": oa.get("url"),
            "fonte": "semantic_scholar",
        })
    return risultati
