"""Ricerca su Semantic Scholar: arricchisce Crossref con abstract e link al PDF
open-access quando esiste, oltre all'ID arXiv se il paper ha anche un preprint.

Senza una API key l'endpoint pubblico è condiviso tra tutti e si satura in
fretta (risposta 429): tra una chiamata e l'altra si aspetta un po', e se
scatta comunque il limite si riprova una volta dopo una pausa più lunga.
"""
import time

import requests

API = "https://api.semanticscholar.org/graph/v1/paper/search"
CAMPI = "title,abstract,year,venue,externalIds,openAccessPdf,url"
PAUSA_TRA_CHIAMATE_S = 3
PAUSA_DOPO_429_S = 20


def cerca(parola_chiave: str, righe: int = 50, api_key: str | None = None) -> list[dict]:
    parametri = {"query": parola_chiave, "limit": righe, "fields": CAMPI}
    headers = {"x-api-key": api_key} if api_key else {}
    try:
        r = requests.get(API, params=parametri, headers=headers, timeout=20)
        if r.status_code == 429:
            time.sleep(PAUSA_DOPO_429_S)
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
        risultati.append({
            "doi": esterni.get("DOI"),
            "titolo": titolo,
            "autori": [],
            "anno": item.get("year"),
            "venue": item.get("venue"),
            "abstract": item.get("abstract"),
            "url": item.get("url"),
            "arxiv_id": esterni.get("ArXiv"),
            "pdf_oa_url": oa.get("url"),
            "fonte": "semantic_scholar",
        })
    return risultati
