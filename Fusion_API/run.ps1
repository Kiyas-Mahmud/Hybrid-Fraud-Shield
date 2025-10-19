# Fusion API PowerShell Run Script
# Hybrid Fraud Detection API Launcher

Write-Host "Starting Fusion API - Hybrid Fraud Detection System" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Green

# Check if virtual environment exists
if (!(Test-Path ".venv")) {
    Write-Host "Virtual environment not found. Creating one..." -ForegroundColor Yellow
    python -m venv .venv
}

# Install dependencies if needed
Write-Host "Installing dependencies..." -ForegroundColor Blue
& ".venv\Scripts\python.exe" -m pip install --quiet --upgrade pip
& ".venv\Scripts\python.exe" -m pip install --quiet -r requirements.txt

# Navigate to app directory
Write-Host "Navigating to app directory..." -ForegroundColor Blue
Set-Location "app"

# Start the API server
Write-Host "Starting API server on http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "API Documentation: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start uvicorn server
& "..\..\.venv\Scripts\python.exe" -m uvicorn main:app --reload --host 127.0.0.1 --port 8000