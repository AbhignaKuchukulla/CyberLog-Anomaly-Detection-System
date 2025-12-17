# PowerShell runner for CyberLog-Anomaly-Detection-System
# Executes: data generation -> preprocessing -> anomaly detection

$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot
$srcDir = Join-Path $projectRoot "src"

$dataGen = Join-Path $srcDir "data_generator.py"
$preproc = Join-Path $srcDir "preprocessing.py"
$anom = Join-Path $srcDir "anomaly_model.py"

function Get-Python {
    # Prefer venv Python in parent or project; fallback to python/py
    $candidates = @(
        (Join-Path (Split-Path $projectRoot -Parent) ".venv/Scripts/python.exe"),
        (Join-Path $projectRoot ".venv/Scripts/python.exe"),
        "python",
        "py -3"
    )
    foreach ($c in $candidates) {
        if ($c -eq "py -3") { return $c }
        if (Test-Path $c) { return $c }
        $cmd = Get-Command $c -ErrorAction SilentlyContinue
        if ($cmd) { return $c }
    }
    throw "Python interpreter not found. Install Python 3 or create a venv."
}

$python = Get-Python

function Invoke-Python($scriptPath) {
    if ($python -eq "py -3") {
        & py -3 $scriptPath
    } else {
        & $python $scriptPath
    }
}

Write-Host "[1/3] Generating synthetic logs..." -ForegroundColor Cyan
Invoke-Python $dataGen

Write-Host "[2/3] Preprocessing logs..." -ForegroundColor Cyan
Invoke-Python $preproc

Write-Host "[3/3] Running anomaly detection..." -ForegroundColor Cyan
Invoke-Python $anom

Write-Host "Done. Check 'data/' for CSVs and 'visuals/' for plots." -ForegroundColor Green
