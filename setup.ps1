# Setup script for Diet Meal Planner
# Run this to create venv and install all dependencies

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  SETTING UP DIET MEAL PLANNER" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if venv exists
if (Test-Path "venv") {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
} else {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Virtual environment created!" -ForegroundColor Green
}

Write-Host "`n📥 Installing dependencies..." -ForegroundColor Yellow

# Activate venv and install
& ".\venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\venv\Scripts\python.exe" -m pip install -r requirements.txt

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  SETUP COMPLETE! ✅" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "To run the project:" -ForegroundColor Yellow
Write-Host "  1. Activate venv: .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  2. Run project: python main.py" -ForegroundColor White
Write-Host "     OR: python -m src.main" -ForegroundColor White
Write-Host "     OR: crewai run`n" -ForegroundColor White
