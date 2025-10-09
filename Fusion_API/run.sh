#!/bin/bash

# Fusion API Run Script
# Hybrid Fraud Detection API Launcher

echo "🚀 Starting Fusion API - Hybrid Fraud Detection System"
echo "======================================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python -m venv .venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv/bin/activate  # For Linux/Mac
# For Windows, use: .venv\Scripts\activate

# Install dependencies
echo "📋 Installing dependencies..."
pip install -r requirements.txt

# Navigate to app directory
cd app

# Start the API server
echo "🌐 Starting FastAPI server..."
echo "   Local URL: http://127.0.0.1:8000"
echo "   Docs URL:  http://127.0.0.1:8000/docs"
echo "   Health:    http://127.0.0.1:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================================="

# Run with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo "🛑 API server stopped"