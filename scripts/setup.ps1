<#
.SYNOPSIS
Prépare un poste Windows pour le projet (idempotent).

.DESCRIPTION
1. crée l'environnement virtuel .venv (sauf -NoVenv) ;
2. installe requirements.txt (Robot Framework, Browser, faster-whisper, rf-mcp) ;
3. télécharge les navigateurs Playwright (équivalent `rfbrowser init`) ;
4. contrôle la présence de ffmpeg dans le PATH.

Le premier /video-to-rf téléchargera en plus le modèle whisper (~460 Mo,
une seule fois, dans %USERPROFILE%\.cache\huggingface).

.EXAMPLE
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1 -NoVenv   # Python global
#>
param([switch]$NoVenv)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root
$env:PYTHONIOENCODING = 'utf-8'

$py = 'python'
if (-not $NoVenv) {
    if (-not (Test-Path '.venv')) {
        Write-Host '[..] Création de .venv'
        python -m venv .venv
    }
    $py = Join-Path $root '.venv\Scripts\python.exe'
}

& $py --version
& $py -m pip install --upgrade pip
& $py -m pip install -r requirements.txt

Write-Host '[..] Navigateurs Playwright (rfbrowser init)'
& $py -m Browser.entry init

if (Get-Command ffmpeg -ErrorAction SilentlyContinue) {
    Write-Host '[OK] ffmpeg présent dans le PATH'
} else {
    Write-Warning 'ffmpeg introuvable, installer : winget install ffmpeg (puis rouvrir le terminal)'
}

Write-Host ''
Write-Host '[OK] Poste prêt.'
if (-not $NoVenv) {
    Write-Host '     Sélectionner .venv comme interpréteur Python dans VS Code'
    Write-Host '     (ou activer .venv\Scripts\Activate.ps1 dans le terminal).'
}
