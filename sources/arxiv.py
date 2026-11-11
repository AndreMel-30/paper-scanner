"""Ricerca su arXiv: niente venue (sono preprint), filtro solo per parola chiave.
Utile per i lavori ancora non pubblicati o per trovare una copia gratuita di un
paper altrimenti a pagamento."""
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone

import requests

API = "http://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom"}


def cerca(query_completa: str, giorni: int, righe: int = 50) -> list[dict]:
    """query_completa è già nella sintassi di arXiv, es. 'all:"NTN" OR all:"satellite"'."""
    parametri = {
        "search_query": query_completa,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": righe,
    }
    try:
        r = requests.get(API, params=parametri, timeout=20)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"  [arxiv] errore sulla ricerca: {e}")
        return []

    soglia = datetime.now(timezone.utc) - timedelta(days=giorni)
    root = ET.fromstring(r.content)
    risultati = []
    for entry in root.findall("a:entry", NS):
        pubblicato = entry.findtext("a:published", default="", namespaces=NS)
        try:
            data_pub = datetime.fromisoformat(pubblicato.replace("Z", "+00:00"))
        except ValueError:
            data_pub = None
        if data_pub and data_pub < soglia:
            continue
        titolo = (entry.findtext("a:title", default="", namespaces=NS) or "").strip()
        if not titolo:
            continue
        autori = [
            a.findtext("a:name", default="", namespaces=NS)
            for a in entry.findall("a:author", NS)
        ]
        arxiv_id = (entry.findtext("a:id", default="", namespaces=NS) or "").rsplit("/", 1)[-1]
        pdf_url = None
        for link in entry.findall("a:link", NS):
            if link.get("title") == "pdf":
                pdf_url = link.get("href")
        risultati.append({
            "doi": entry.findtext("{http://arxiv.org/schemas/atom}doi", default=None, namespaces=NS),
            "titolo": titolo,
            "autori": autori,
            "anno": data_pub.year if data_pub else None,
            "venue": "arXiv",
            "abstract": (entry.findtext("a:summary", default="", namespaces=NS) or "").strip(),
            "url": entry.findtext("a:id", default="", namespaces=NS),
            "arxiv_id": arxiv_id,
            "pdf_oa_url": pdf_url,
            "fonte": "arxiv",
        })
    return risultati
