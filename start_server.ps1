# Health Insurance Helper - Quick Start Script (PowerShell)
# This script activates the virtual environment and starts the Django server

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host " Health Insurance Helper - Starting Server" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

$currentDir = $PSScriptRoot
$appDir = Join-Path $currentDir "health_insurance_helper"

Set-Location $appDir

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ../env/Scripts/Activate.ps1

Write-Host "Running database migrations..." -ForegroundColor Yellow
python manage.py migrate

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "Starting Django development server..." -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan
Write-Host "Server running at: http://127.0.0.1:8000/" -ForegroundColor Green
Write-Host "Admin panel: http://127.0.0.1:8000/admin/" -ForegroundColor Green
Write-Host "`nPress Ctrl+C to stop the server`n" -ForegroundColor Yellow

python manage.py runserver
