"""Ricerca su Crossref: copre qualsiasi editore (IEEE, Elsevier, ...) perché
indicizza i metadati pubblicati da chiunque abbia registrato un DOI."""
from datetime import date, timedelta

import requests

API = "https://api.crossref.org/works"


def cerca(venue: str, giorni: int, email: str, righe: int = 50) -> list[dict]:
    da = (date.today() - timedelta(days=giorni)).isoformat()
    parametri = {
        "query.container-title": venue,
        "filter": f"from-pub-date:{da}",
        "rows": righe,
        "mailto": email,
    }
    try:
        r = requests.get(API, params=parametri, timeout=20)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"  [crossref] errore su '{venue}': {e}")
        return []

    risultati = []
    for item in r.json().get("message", {}).get("items", []):
        titolo = (item.get("title") or [None])[0]
        if not titolo:
            continue
        autori = [
            " ".join(p for p in (a.get("given"), a.get("family")) if p)
            for a in item.get("author", [])
        ]
        anno = None
        for campo in ("published-print", "published-online", "published"):
            parti = item.get(campo, {}).get("date-parts")
            if parti and parti[0]:
                anno = parti[0][0]
                break
        risultati.append({
            "doi": item.get("DOI"),
            "titolo": titolo,
            "autori": autori,
            "anno": anno,
            "venue": (item.get("container-title") or [venue])[0],
            "abstract": item.get("abstract"),
            "url": item.get("URL"),
            "arxiv_id": None,
            "fonte": "crossref",
        })
    return risultati
