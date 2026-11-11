"""Scarica un PDF via HTTP semplice (per i link open-access) e verifica che il
contenuto sia davvero un PDF e non una pagina di errore/captcha travestita da
.pdf — è già successo scaricando a mano i documenti 3GPP."""
from pathlib import Path

import requests

AGENTE = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)


def scarica_url(url: str, dest_path: Path) -> bool:
    try:
        r = requests.get(url, headers={"User-Agent": AGENTE}, timeout=30)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"  [download] errore su {url}: {e}")
        return False

    if not r.content.startswith(b"%PDF"):
        print(f"  [download] contenuto non è un PDF valido: {url}")
        return False

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_bytes(r.content)
    return True


def e_pdf_valido(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            return f.read(4) == b"%PDF"
    except OSError:
        return False
