# Fusion API - Hybrid Fraud Detection System

🚀 **Advanced fraud detection API using ML+DL ensemble with meta-learning**

## Overview

This API combines **5 Machine Learning models** and **8 Deep Learning models** using a trained meta-learner to provide highly accurate fraud detection predictions. The system uses an optimized threshold (0.400) and calibrated probabilities for reliable results.

## 🏗️ Architecture

```
Input Transaction (63 features)
    ↓
Data Preprocessing (Scaling/Validation)
    ↓
┌─────────────────┬─────────────────┐
│   ML Models     │   DL Models     │
│ • Logistic Reg  │ • FNN/FNN Tuned │
│ • Random Forest │ • CNN/CNN Tuned │
│ • XGBoost       │ • LSTM          │
│ • XGB SMOTE     │ • BiLSTM        │
│ • CatBoost      │ • CNN-BiLSTM    │
│                 │ • Autoencoder   │
└─────────────────┴─────────────────┘
    ↓
Meta-Learner (Logistic Regression)
    ↓
Final Prediction (Fraud/Safe + Probability)
```

## 📁 Project Structure

```
Fusion_API/
├── app/
│   ├── main.py              # FastAPI application
│   ├── model_loader.py      # Model loading utilities
│   ├── preprocessing.py     # Data preprocessing
│   └── inference.py         # Hybrid inference engine
├── artifacts/
│   ├── ml/                  # ML model files (.pkl)
│   ├── dl/                  # DL model files (.keras)
│   ├── hybrid/              # Meta-learner and config
│   ├── standard_scaler.pkl  # Data scaler
│   └── minmax_scaler.pkl    # Alternative scaler
├── sample_requests/
│   ├── fraud_sample.json    # Example fraud transaction
│   └── safe_sample.json     # Example safe transaction
├── results/                 # API test logs and outputs
├── requirements.txt         # Python dependencies
├── run.sh                   # Quick start script
└── README.md               # This file
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- Virtual environment (recommended)
- 4GB+ RAM (for model loading)

### 2. Installation

```bash
# Clone and navigate to the project
cd Fusion_API

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Start the API

```bash
# Quick start with script
chmod +x run.sh
./run.sh

# OR manually
cd app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Access the API

- **API Base URL**: http://127.0.0.1:8000
- **Interactive Docs**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health

## 🔗 API Endpoints

### 1. Health Check

```bash
GET /health
```

**Response:**

```json
{
  "status": "Healthy",
  "message": "API is running and models are loaded",
  "models_loaded": {
    "ml_models": [
      "logistic_regression",
      "random_forest",
      "xgboost",
      "xgboost_smote",
      "catboost"
    ],
    "dl_models": [
      "fnn",
      "fnn_tuned",
      "cnn",
      "cnn_tuned",
      "lstm",
      "bilstm",
      "cnn_bilstm",
      "autoencoder"
    ],
    "total_base_models": 13
  }
}
```

### 2. Fraud Prediction

```bash
POST /predict
Content-Type: application/json
```

**Request Body:**

```json
{
  "feature_0": 0.85,
  "feature_1": 0.92,
  "feature_2": 0.78,
  ...
  "feature_62": 0.87
}
```

**Response:**

```json
{
  "status": "Fraud",
  "probability": 0.8745,
  "calibrated_probability": 0.8821,
  "confidence": 0.749,
  "prediction": 1,
  "threshold_used": 0.4,
  "inference_time_ms": 245.67,
  "model_stats": {
    "ml_models_used": 5,
    "dl_models_used": 8,
    "total_base_models": 13
  }
}
```

### 3. Prediction with Explanation

```bash
POST /explain
Content-Type: application/json
```

**Response:** (Same as /predict plus explanation details)

```json
{
  "prediction": { ... },
  "explanation": {
    "top_contributing_models": [
      ["xgboost_pred", 0.92],
      ["cnn_tuned_pred", 0.89],
      ["catboost_pred", 0.87]
    ],
    "model_agreement": {
      "high_risk_models": 8,
      "medium_risk_models": 3,
      "low_risk_models": 2
    }
  }
}
```

### 4. API Information

```bash
GET /info
```

## 🧪 Testing

### Using Sample Files

```bash
# Test with safe transaction
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d @sample_requests/safe_sample.json

# Test with fraud transaction
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d @sample_requests/fraud_sample.json
```

### Using Python

```python
import requests
import json

url = "http://127.0.0.1:8000/predict"

# Load sample data
with open("sample_requests/fraud_sample.json", "r") as f:
    fraud_sample = json.load(f)

# Make prediction
response = requests.post(url, json=fraud_sample)
result = response.json()

print(f"Status: {result['status']}")
print(f"Probability: {result['probability']:.4f}")
print(f"Confidence: {result['confidence']:.4f}")
```

## 📊 Model Performance

- **Test F1-Score**: 0.6326
- **Test ROC-AUC**: 0.8745
- **Test Precision**: 0.7481
- **Test Recall**: 0.5480
- **Optimal Threshold**: 0.400

## 🔧 Configuration

### Model Components

- **ML Models**: 5 (Logistic Regression, Random Forest, XGBoost, XGBoost SMOTE, CatBoost)
- **DL Models**: 8 (FNN, CNN, LSTM, BiLSTM, CNN-BiLSTM, Autoencoder + tuned versions)
- **Meta-Learner**: Logistic Regression with GridSearchCV optimization
- **Features**: 63 optimized features from feature selection process

### Input Requirements

- **Feature Count**: Exactly 63 numeric features
- **Feature Names**: `feature_0` to `feature_62`
- **Data Type**: All values must be numeric (float/int)
- **Range**: No strict range requirements (handled by preprocessing)

## 🚨 Troubleshooting

### Common Issues

1. **Model Loading Errors**

   - Ensure all model files are in the correct `artifacts/` subdirectories
   - Check that Python environment has all required packages

2. **Memory Issues**

   - Requires ~4GB RAM for full model loading
   - Consider reducing batch size for multiple requests

3. **Input Validation Errors**

   - Ensure exactly 63 features are provided
   - All feature values must be numeric
   - Check for missing or null values

4. **Port Already in Use**
   ```bash
   # Change port in run.sh or use:
   uvicorn main:app --port 8001
   ```

### Logs and Debugging

```bash
# Check API logs
tail -f results/api_logs.txt

# Test individual components
cd app
python model_loader.py  # Test model loading
python preprocessing.py # Test preprocessing
```

## 📈 Performance Monitoring

The API provides detailed timing and model statistics:

- **Inference Time**: Typically 100-300ms per prediction
- **Model Loading**: ~30-60 seconds on startup
- **Memory Usage**: ~4GB for all models loaded

## 🔒 Security Considerations

- Input validation prevents injection attacks
- No sensitive data is logged
- CORS configured for development (restrict for production)
- Consider rate limiting for production deployment

## 🚀 Production Deployment

For production deployment:

1. **Use WSGI server** (Gunicorn + Uvicorn workers)
2. **Add authentication** (API keys, JWT tokens)
3. **Configure logging** (structured logs, monitoring)
4. **Add rate limiting** (prevent abuse)
5. **Use load balancer** (multiple API instances)
6. **Monitor metrics** (latency, throughput, error rates)

```bash
# Production example
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📞 Support

For issues or questions:

- Check the `/health` endpoint for model status
- Review logs in the `results/` directory
- Test with provided sample files first
- Ensure all dependencies are correctly installed

---

**Fusion API v1.0** - Advanced Hybrid Fraud Detection System  
_Combining the power of ML, DL, and Meta-Learning for superior fraud detection_
