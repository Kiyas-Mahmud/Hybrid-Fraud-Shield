# Quick Start Script for Windows PowerShell

Write-Host "Hybrid Fraud Shield - Quick Start Setup" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Check if MySQL is running
Write-Host "`nStep 1: Checking MySQL..." -ForegroundColor Yellow
$mysqlService = Get-Service -Name "MySQL*" -ErrorAction SilentlyContinue
if ($mysqlService) {
    if ($mysqlService.Status -eq "Running") {
        Write-Host "MySQL is running" -ForegroundColor Green
    } else {
        Write-Host "Starting MySQL..." -ForegroundColor Yellow
        Start-Service $mysqlService.Name
    }
} else {
    Write-Host "Warning: MySQL service not found. Please ensure MySQL is installed and running." -ForegroundColor Red
}

# Setup Backend
Write-Host "`nStep 2: Setting up Backend..." -ForegroundColor Yellow
Set-Location backend

if (-Not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if (-Not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "Please edit .env file with your MySQL credentials before continuing." -ForegroundColor Red
    Write-Host "Press any key to continue after editing .env..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

Write-Host "`nStep 3: Initializing Database..." -ForegroundColor Yellow
python init_db.py

Write-Host "`nStep 4: Backend setup complete!" -ForegroundColor Green
Write-Host "To start the backend server, run:" -ForegroundColor Cyan
Write-Host "  cd app" -ForegroundColor White
Write-Host "  uvicorn main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White

Set-Location ..

# Setup Frontend
Write-Host "`nStep 5: Setting up Frontend..." -ForegroundColor Yellow
Set-Location frontend

if (Test-Path "package.json") {
    Write-Host "Installing Node dependencies..." -ForegroundColor Yellow
    npm install
    Write-Host "Frontend setup complete!" -ForegroundColor Green
}

Set-Location ..

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Start Backend:" -ForegroundColor Cyan
Write-Host "   cd backend\app" -ForegroundColor White
Write-Host "   uvicorn main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
Write-Host "`n2. Start Frontend:" -ForegroundColor Cyan
Write-Host "   cd frontend" -ForegroundColor White
Write-Host "   npm start" -ForegroundColor White
Write-Host "`n3. API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "`n4. Default Admin Login:" -ForegroundColor Cyan
Write-Host "   Username: admin" -ForegroundColor White
Write-Host "   Password: admin123" -ForegroundColor White
Write-Host "`nHappy Coding!" -ForegroundColor Green
