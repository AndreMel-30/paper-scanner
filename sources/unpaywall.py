"""Risolve, a partire da un DOI, un link a una copia open-access legale del
paper (versione pubblicata gratuita, o preprint ospitato dall'editore stesso)."""
import requests

API = "https://api.unpaywall.org/v2/{doi}"


def trova_pdf_oa(doi: str, email: str) -> str | None:
    if not doi:
        return None
    try:
        r = requests.get(API.format(doi=doi), params={"email": email}, timeout=20)
        if r.status_code == 404:
            return None
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"  [unpaywall] errore su DOI {doi}: {e}")
        return None

    dati = r.json()
    posizione = dati.get("best_oa_location") or {}
    return posizione.get("url_for_pdf") or posizione.get("url")
