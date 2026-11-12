# Prepara l'ambiente del tool su Windows: venv locale e dipendenze Python.
# Da lanciare una volta per macchina (richiede una connessione a internet).
# Equivalente di setup.sh per chi non ha bash (WSL o Git Bash non necessari).

Set-Location $PSScriptRoot

python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip --quiet
.\.venv\Scripts\python.exe -m pip install -r requirements.txt --quiet

Write-Host "Setup completato."
Write-Host "Prossimo passo: .\scan.ps1 --dry-run"
