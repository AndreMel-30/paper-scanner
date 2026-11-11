#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -x ".venv/bin/python3" ]; then
    echo "Ambiente non pronto: lancia prima ./setup.sh" >&2
    exit 1
fi

exec .venv/bin/python3 scan_paper.py "$@"
