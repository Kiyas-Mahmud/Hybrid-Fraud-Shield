@echo off
cd /d e:\Research\Biin\Fraud_Ditection_Enhance\backend
echo Starting Fraud Detection Backend Server...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
