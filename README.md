# 🚀 Advanced Hybrid Fraud Detection System

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)](https://tensorflow.org)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.x-yellow.svg)](https://scikit-learn.org)
[![License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)

> **State-of-the-art fraud detection system combining 13 machine learning models with meta-learning for superior accuracy**

## 📊 **Project Overview**

This project implements a comprehensive fraud detection system that leverages the power of **ensemble learning** and **meta-learning** to achieve exceptional fraud detection performance. The system combines:

- **5 Machine Learning Models**: Logistic Regression, Random Forest, XGBoost, XGBoost-SMOTE, CatBoost
- **8 Deep Learning Models**: FNN, FNN-Tuned, CNN, CNN-Tuned, LSTM, BiLSTM, CNN-BiLSTM, Autoencoder
- **Meta-Learning**: Trained meta-learner combines all model predictions
- **Production API**: FastAPI-based REST API for real-time fraud detection

## 🎯 **Key Features**

### 🔬 **Advanced Model Ensemble**

- **13 Diverse Models**: Different algorithms capture various fraud patterns
- **Meta-Learning**: Optimal combination of base model predictions
- **Calibrated Probabilities**: Reliable confidence scores
- **Optimal Threshold**: Data-driven decision boundary (0.400)

### 🚀 **Production-Ready API**

- **FastAPI Framework**: High-performance, auto-documented API
- **Real-time Predictions**: Sub-second response times
- **Interactive Documentation**: Swagger UI at `/docs`
- **Health Monitoring**: System status and model validation
- **Batch Processing**: Multiple transaction support

### 📈 **Superior Performance**

- **F1-Score**: 0.6326 (Test Set)
- **ROC-AUC**: 0.8745
- **Precision**: 0.7481
- **Recall**: 0.5480
- **Processing Time**: ~1-4 seconds per prediction

## 🏗️ **System Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRAUD DETECTION PIPELINE                     │
├─────────────────────────────────────────────────────────────────┤
│  Input Transaction (63 Optimized Features)                     │
│                           ↓                                     │
│  Data Preprocessing & Validation                               │
│                           ↓                                     │
│  ┌─────────────────┬─────────────────┬─────────────────┐      │
│  │   ML Models     │   DL Models     │   Preprocessing │      │
│  │ • Logistic Reg  │ • FNN/FNN Tuned │ • StandardScaler│      │
│  │ • Random Forest │ • CNN/CNN Tuned │ • MinMaxScaler  │      │
│  │ • XGBoost       │ • LSTM          │ • Feature Valid │      │
│  │ • XGBoost-SMOTE │ • BiLSTM        │ • Data Routing  │      │
│  │ • CatBoost      │ • CNN-BiLSTM    │                 │      │
│  │                 │ • Autoencoder   │                 │      │
│  └─────────────────┴─────────────────┴─────────────────┘      │
│                           ↓                                     │
│                   Meta-Learning Layer                          │
│                  (Logistic Regression)                        │
│                           ↓                                     │
│              Calibrated Probability + Threshold               │
│                           ↓                                     │
│                   Final Fraud Prediction                      │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 **Project Structure**

```
Fraud_Ditection_Enhance/
├── 📊 data/
│   └── reduced_df.csv                 # Training dataset (102→63 features)
├── 🤖 model/
│   ├── dl/                           # Deep Learning models
│   ├── hybrid/                       # Meta-learning components
│   └── ml/                           # Machine Learning models
├── 🚀 Fusion_API/                    # Production API
│   ├── app/                          # FastAPI application
│   │   ├── main.py                   # API endpoints
│   │   ├── model_loader.py           # Model management
│   │   ├── preprocessing.py          # Data preprocessing
│   │   └── inference.py              # Hybrid inference engine
│   ├── artifacts/                    # Deployed models
│   │   ├── ml/                       # ML model files (.pkl)
│   │   ├── dl/                       # DL model files (.keras)
│   │   └── hybrid/                   # Meta-learner & config
│   ├── sample_requests/              # Test data
│   │   ├── high_fraud_sample.json    # High-risk transaction
│   │   ├── legitimate_sample.json    # Safe transaction
│   │   ├── borderline_sample.json    # Suspicious transaction
│   │   └── batch_sample.json         # Multiple transactions
│   ├── requirements.txt              # Python dependencies
│   ├── README.md                     # API documentation
│   └── test_api_comprehensive.py     # Testing suite
├── 📈 Results/                       # Training results & metrics
├── 🐍 .venv/                         # Virtual environment
└── 📋 README.md                      # This file
```

## 🚀 **Quick Start**

### **Prerequisites**

- Python 3.9+
- Virtual environment (recommended)
- 8GB+ RAM (for model loading)

### **Installation**

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Fraud_Ditection_Enhance
   ```

2. **Set up virtual environment**

   ```bash
   python -m venv .venv

   # Windows
   .venv\Scripts\activate

   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   cd Fusion_API
   pip install -r requirements.txt
   ```

### **Start the API Server**

```bash
# Navigate to API directory
cd Fusion_API/app

# Start FastAPI server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### **Access the API**

- **🌐 API Base URL**: `http://127.0.0.1:8000`
- **📖 Interactive Docs**: `http://127.0.0.1:8000/docs`
- **🔍 Health Check**: `http://127.0.0.1:8000/health`

## 🔧 **API Usage**

### **Health Check**

```bash
curl http://127.0.0.1:8000/health
```

**Response:**

```json
{
  "status": "Healthy",
  "message": "API is running and models are loaded",
  "models_loaded": {
    "ml_models": 5,
    "dl_models": 8,
    "hybrid_models": 1
  },
  "total_models": 13,
  "optimal_threshold": 0.4
}
```

### **Fraud Prediction**

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d @sample_requests/high_fraud_sample.json
```

**Response:**

```json
{
  "v7_high_rank056": 0.2341,
  "v19_high_rank055": 0.8921,
  "v23_critical_rank017": 1.4567,
  "v35_critical_rank039": 0.3456,
  "v36_critical_rank037": 0.789,
  "v38_critical_rank021": 1.2345,
  "v45_critical_rank006": 2.1098,
  "v47_critical_rank019": 0.5432,
  "v53_high_rank052": 0.9876,
  "v61_high_rank053": 1.1111,
  "v62_high_rank049": 0.8765,
  "v67_high_rank050": 1.3579,
  "v78_critical_rank041": 0.2468,
  "v82_high_rank045": 0.9753,
  "v83_high_rank048": 1.0864,
  "v86_critical_rank009": 2.0,
  "v87_critical_rank010": 1.8642,
  "v108_critical_rank035": 0.4321,
  "v110_critical_rank043": 0.6789,
  "v111_critical_rank023": 1.5555,
  "v112_critical_rank033": 0.3333,
  "v113_critical_rank025": 1.4444,
  "v114_critical_rank042": 0.7777,
  "v119_high_rank054": 0.8888,
  "v123_critical_rank018": 1.6666,
  "v124_high_rank044": 0.1234,
  "v140_high_rank051": 0.9999,
  "v148_critical_rank026": 1.7777,
  "v149_critical_rank020": 0.5678,
  "v153_critical_rank034": 0.4567,
  "v154_critical_rank031": 1.2222,
  "v155_critical_rank028": 0.8901,
  "v170_critical_rank013": 1.9876,
  "v176_critical_rank029": 0.6543,
  "v186_critical_rank030": 0.7654,
  "v188_critical_rank008": 2.3456,
  "v189_critical_rank007": 2.4567,
  "v190_critical_rank015": 1.8765,
  "v194_critical_rank022": 1.321,
  "v195_critical_rank027": 0.9012,
  "v197_critical_rank024": 1.5678,
  "v198_critical_rank036": 0.2109,
  "v199_critical_rank012": 2.1111,
  "v200_critical_rank005": 2.6789,
  "v201_critical_rank004": 2.789,
  "v228_critical_rank014": 1.9999,
  "v242_critical_rank003": 2.8901,
  "v243_critical_rank016": 1.7654,
  "v244_critical_rank002": 3.0,
  "v245_high_rank047": 0.1111,
  "v248_high_rank057": 0.0987,
  "v249_high_rank046": 0.1357,
  "v252_critical_rank040": 0.2222,
  "v257_critical_rank001": 3.5,
  "v258_critical_rank011": 2.0123,
  "v260_critical_rank038": 0.3579,
  "v262_critical_rank032": 0.1975,
  "d9_distance": 4.5678,
  "id_11": 100.0,
  "id_13": 150.0,
  "id_17": 200.0,
  "email_match": 1.0,
  "R_emaildomain_FE": 0.8
}

```

### **Batch Processing**

```bash
curl -X POST "http://127.0.0.1:8000/predict/batch" \
  -H "Content-Type: application/json" \
  -d @sample_requests/batch_sample.json
```

## 📊 **Model Performance**

| Metric                | Value  | Description                                         |
| --------------------- | ------ | --------------------------------------------------- |
| **F1-Score**          | 0.6326 | Harmonic mean of precision and recall               |
| **ROC-AUC**           | 0.8745 | Area under the ROC curve                            |
| **Precision**         | 0.7481 | True positives / (True positives + False positives) |
| **Recall**            | 0.5480 | True positives / (True positives + False negatives) |
| **Accuracy**          | 0.8923 | Overall classification accuracy                     |
| **Optimal Threshold** | 0.400  | Data-driven decision boundary                       |

### **Model Breakdown**

| Model Type           | Count  | Purpose                               |
| -------------------- | ------ | ------------------------------------- |
| **Machine Learning** | 5      | Linear patterns, tree-based decisions |
| **Deep Learning**    | 8      | Complex non-linear patterns           |
| **Meta-Learner**     | 1      | Optimal combination of base models    |
| **Total Ensemble**   | **13** | **Comprehensive fraud detection**     |

## 🧪 **Testing**

### **Comprehensive Test Suite**

```bash
cd Fusion_API
python test_api_comprehensive.py
```

### **Individual Sample Testing**

```bash
# Test high-risk transaction
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d @sample_requests/high_fraud_sample.json

# Test legitimate transaction
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d @sample_requests/legitimate_sample.json

# Test borderline case
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d @sample_requests/borderline_sample.json
```

## 🔧 **Configuration**

### **Environment Variables**

```bash
# API Configuration
API_HOST=127.0.0.1
API_PORT=8000
MODEL_PATH=./artifacts

# Model Settings
OPTIMAL_THRESHOLD=0.400
ENABLE_MODEL_VALIDATION=true
MAX_BATCH_SIZE=1000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### **Model Configuration**

The system automatically loads all available models from the `artifacts/` directory:

- **ML Models**: `.pkl` files in `artifacts/ml/`
- **DL Models**: `.keras` files in `artifacts/dl/`
- **Scalers**: `standard_scaler.pkl`, `minmax_scaler.pkl`
- **Meta-Learner**: `meta_model.pkl` in `artifacts/hybrid/`

## 🚀 **Production Deployment**

### **Docker Deployment**

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY Fusion_API/ .
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Cloud Deployment Options**

- **AWS**: EC2, ECS, Lambda
- **Google Cloud**: Cloud Run, GKE, App Engine
- **Azure**: Container Instances, App Service
- **Heroku**: Web dyno with Docker

### **Performance Optimization**

- **Model Caching**: Pre-load models on startup
- **Async Processing**: Non-blocking inference
- **Load Balancing**: Multiple API instances
- **GPU Acceleration**: For deep learning models

## 🔍 **Feature Engineering**

### **Input Features (63 optimized)**

The model expects exactly **63 features** with specific naming convention:

- **V-Features**: `v{number}_{importance}_rank{rank}` (e.g., `v257_critical_rank001`)
- **Distance Features**: `d9_distance`
- **ID Features**: `id_11`, `id_13`, `id_17`
- **Email Features**: `email_match`, `R_emaildomain_FE`

### **Feature Importance Levels**

- **Critical**: Highest fraud indicators (rank 001-042)
- **High**: Important secondary features (rank 043-057)
- **Distance**: Geographic/behavioral patterns

## 🛠️ **Development**

### **Adding New Models**

1. Train your model using the same 63 features
2. Save model file in appropriate format (`.pkl` or `.keras`)
3. Add model file to `artifacts/ml/` or `artifacts/dl/`
4. Update model mapping in `inference.py`
5. Retrain meta-learner with new model predictions

### **API Extension**

```python
# Add new endpoint in main.py
@app.post("/predict/explain")
async def explain_prediction(transaction: TransactionData):
    # Your implementation
    return explanation_result
```

### **Custom Preprocessing**

```python
# Extend preprocessing.py
class CustomPreprocessor(DataPreprocessor):
    def custom_feature_engineering(self, data):
        # Your feature engineering logic
        return processed_data
```

## 📚 **Documentation**

- **API Documentation**: Available at `/docs` when server is running
- **Model Documentation**: See `Results/` directory for training metrics
- **Code Documentation**: Inline docstrings throughout codebase

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Scikit-learn**: Machine learning models
- **TensorFlow/Keras**: Deep learning framework
- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **Research Community**: Fraud detection methodologies

## 📞 **Support**

For support, please:

1. Check the [API Documentation](http://127.0.0.1:8000/docs)
2. Review [Issues](https://github.com/your-repo/issues)
3. Contact the development team

---

<div align="center">

**⚡ Powered by Advanced Machine Learning ⚡**

_Protecting businesses from fraud with cutting-edge AI_

</div>
