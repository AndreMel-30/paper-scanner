#!/usr/bin/env bash
# Prepara l'ambiente del tool: venv locale e dipendenze Python.
# Da lanciare una volta per macchina (richiede una connessione a internet).
set -euo pipefail
cd "$(dirname "$0")"

python3 -m venv .venv
.venv/bin/pip install --upgrade pip --quiet
.venv/bin/pip install -r requirements.txt --quiet

echo "Setup completato."
echo "Prossimo passo: ./scan.sh --dry-run"
