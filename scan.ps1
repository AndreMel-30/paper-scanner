# Equivalente di scan.sh per chi usa Windows senza bash (WSL o Git Bash).

Set-Location $PSScriptRoot

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Error "Ambiente non pronto: lancia prima .\setup.ps1"
    exit 1
}

& .\.venv\Scripts\python.exe scan_paper.py @args
exit $LASTEXITCODE
