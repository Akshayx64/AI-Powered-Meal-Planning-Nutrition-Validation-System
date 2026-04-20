# Run script for Diet Meal Planner (using venv)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  RUNNING DIET MEAL PLANNER" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if venv exists
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "   Run setup.ps1 first: .\setup.ps1`n" -ForegroundColor Yellow
    exit 1
}

Write-Host "🚀 Starting meal planning crew...`n" -ForegroundColor Yellow

# Run using venv python
& ".\venv\Scripts\python.exe" main.py

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  EXECUTION COMPLETE!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Check outputs in:" -ForegroundColor Yellow
Write-Host "  - output/meal_plan.md" -ForegroundColor White
Write-Host "  - output/shopping_list.md" -ForegroundColor White
Write-Host "  - logs/agent_execution.log`n" -ForegroundColor White
