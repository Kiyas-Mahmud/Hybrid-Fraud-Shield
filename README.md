# Hybrid Fraud Detection System

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)](https://tensorflow.org)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.x-yellow.svg)](https://scikit-learn.org)
[![License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)

> **Enterprise-grade fraud detection system combining 13 machine learning models with meta-learning and SHAP explainability for superior accuracy and regulatory compliance**

## Table of Contents

- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [Framework Flowchart](#framework-flowchart)
- [Key Features](#key-features)
- [Performance Metrics](#performance-metrics)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [API Usage](#api-usage)
- [Model Training](#model-training)
- [Explainability](#explainability)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

This project implements a state-of-the-art fraud detection system that leverages the power of **hybrid ensemble learning** and **meta-learning** to achieve exceptional fraud detection performance. The system combines multiple machine learning and deep learning models with SHAP-based explainability for transparent, regulatory-compliant fraud detection.

### Core Components

- **13 Base Models**: 5 ML + 8 DL models capturing diverse fraud patterns
- **Meta-Learning**: Logistic Regression meta-learner optimally combines predictions
- **SHAP Explainability**: Transparent, interpretable fraud detection decisions
- **Production API**: FastAPI-based REST API for real-time inference
- **Comprehensive Training**: End-to-end model training and hyperparameter tuning

## System Architecture

````
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          HYBRID FRAUD DETECTION SYSTEM                         │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────────────────┐
│   INPUT DATA    │────│  PREPROCESSING   │────│         BASE MODELS             │
│                 │    │                  │    │                                 │
│ • Transaction   │    │ • Feature Eng.   │    │ ┌─────────────────────────────┐ │
│   Features (63) │    │ • Scaling        │    │ │      ML MODELS (5)          │ │
```mermaid
flowchart TD
    A[Raw Transaction Data] --> B[Data Preprocessing]
    B --> C{Feature Engineering}
    C --> D[Train/Val/Test Split]
    D --> E[ML Pipeline]
    D --> F[DL Pipeline]

    E --> G[Logistic Regression]
    E --> H[Random Forest]
    E --> I[XGBoost]
    E --> J[XGBoost-SMOTE]
    E --> K[CatBoost]

    F --> L[Feed Forward NN]
    F --> M[CNN]
    F --> N[LSTM]
    F --> O[BiLSTM]
    F --> P[CNN-BiLSTM]
    F --> Q[Autoencoder]
    F --> R[Tuned Variants]

    G --> S[Meta-Learner Training]
    H --> S
    I --> S
    J --> S
    K --> S
    L --> S
    M --> S
    N --> S
    O --> S
    P --> S
    Q --> S
    R --> S

    S --> T[Threshold Optimization]
    T --> U[Model Validation]
    U --> V[Production Deployment]

    V --> W[FastAPI Server]
    W --> X[Real-time Predictions]
    W --> Y[SHAP Explanations]

    X --> Z[Fraud Detection Result]
    Y --> Z

    style A fill:#e1f5fe
    style Z fill:#c8e6c9
    style S fill:#fff3e0
    style W fill:#f3e5f5
````

## Key Features

### Advanced Ensemble Learning

- **Diverse Model Portfolio**: Combines 5 ML and 8 DL models for comprehensive fraud pattern detection
- **Meta-Learning Architecture**: Logistic Regression meta-learner learns optimal model combination
- **Automatic Model Selection**: Intelligent weighting based on individual model strengths
- **Calibrated Predictions**: Reliable probability estimates for risk assessment

### Production-Ready API

- **FastAPI Framework**: High-performance, modern Python API framework
- **Real-time Inference**: Sub-second response times for production workloads
- **Interactive Documentation**: Auto-generated Swagger UI at `/docs`
- **Health Monitoring**: Comprehensive system health checks and model validation
- **Batch Processing**: Support for single and multiple transaction processing

### Explainable AI

- **SHAP Integration**: State-of-the-art model explainability framework
- **Feature Importance**: Global and local feature importance analysis
- **Risk Factor Identification**: Automated identification of fraud indicators
- **Regulatory Compliance**: Transparent decision-making for audit requirements
- **Human-readable Explanations**: Natural language explanations for business users

### Robust Data Pipeline

- **Feature Engineering**: 63 carefully engineered fraud detection features
- **Multiple Scaling**: StandardScaler and MinMaxScaler for different model requirements
- **Class Imbalance Handling**: SMOTE oversampling and class weighting strategies
- **Data Validation**: Comprehensive input validation and error handling

## Performance Metrics

### Test Set Performance

| Metric                | Value  | Description                              |
| --------------------- | ------ | ---------------------------------------- |
| **F1-Score**          | 0.6326 | Harmonic mean of precision and recall    |
| **ROC-AUC**           | 0.8745 | Area under the ROC curve                 |
| **Precision**         | 0.7481 | True positive rate (fraud accuracy)      |
| **Recall**            | 0.5480 | Fraud detection rate                     |
| **Specificity**       | 0.9789 | True negative rate (legitimate accuracy) |
| **Optimal Threshold** | 0.400  | F1-optimized decision boundary           |

### Model Composition

| Model Category       | Count | Examples                                              |
| -------------------- | ----- | ----------------------------------------------------- |
| **Machine Learning** | 5     | XGBoost, CatBoost, Random Forest, Logistic Regression |
| **Deep Learning**    | 8     | CNN, LSTM, BiLSTM, Autoencoder, FNN variants          |
| **Meta-Learner**     | 1     | Logistic Regression (ensemble combiner)               |
| **Total Models**     | 14    | Complete hybrid ensemble system                       |

### Performance Benchmarks

- **API Response Time**: 1-4 seconds per prediction
- **Model Loading Time**: 15-30 seconds (one-time startup)
- **Memory Usage**: ~2-4 GB (all models loaded)
- **CPU Usage**: Optimized for multi-core processing
- **Scalability**: Horizontal scaling via container orchestration

## Project Structure

```
Fraud_Detection_Hybrid/
├── README.md                      # Project documentation
├── requirements.txt               # Python dependencies
├── .gitignore                    # Git ignore rules
│
├── data/                         # Data directory
│   ├── raw/                     # Original datasets
│   ├── processed_data/          # Preprocessed datasets
│   └── final_processed_data/    # Final feature-engineered data
│
├── model/                        # Model training notebooks
│   ├── ml/                      # Machine Learning models
│   │   └── 01_ml_models_training_and_tuning.ipynb
│   ├── dl/                      # Deep Learning models
│   │   └── 01_dl_models_training_and_tuning.ipynb
│   └── hybrid/                  # Hybrid ensemble models
│       ├── 01_ml_dl_hybrid_fusion_ensemble.ipynb
│       ├── 02_meta_learner_fusion_training.ipynb
│       └── 03_explainability_shap_analysis.ipynb
│
├── Fusion_API/                   # Production API
│   ├── app/                     # FastAPI application
│   │   ├── main.py             # API entry point
│   │   ├── model_loader.py     # Model management
│   │   ├── preprocessing.py    # Data preprocessing
│   │   ├── inference.py        # Prediction engine
│   │   └── explainability.py   # SHAP explanations
│   ├── artifacts/              # Trained model files
│   │   ├── ml_models/         # ML model artifacts
│   │   ├── dl_models/         # DL model artifacts
│   │   ├── scalers/           # Preprocessing scalers
│   │   └── meta_learner/      # Meta-learner model
│   ├── sample_requests/        # Example API requests
│   ├── test_*.py              # API test scripts
│   ├── run.sh                 # Linux/Mac startup script
│   └── run.ps1               # Windows PowerShell script
│
└── Results/                      # Training results and metrics
    ├── model_performance/       # Performance metrics
    ├── visualizations/         # Charts and plots
    └── reports/                # Analysis reports
```

## Installation & Setup

### Prerequisites

- **Python 3.9+** (recommended: Python 3.9 or 3.10)
- **Git** for repository cloning
- **8+ GB RAM** for optimal performance
- **2+ CPU cores** recommended

### Step-by-Step Installation Guide

#### 1. Clone the Repository

```bash
git clone https://github.com/Kiyas-Mahmud/fraude-detection-hybrid-api.git
cd fraude-detection-hybrid-api
```

#### 2. Create Virtual Environment

**Option A: Using venv (Recommended)**

```bash
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

**Option B: Using conda**

```bash
conda create -n fraud-detection python=3.9
conda activate fraud-detection
```

#### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Verify Installation

```bash
python -c "import tensorflow, sklearn, fastapi, shap; print('All dependencies installed successfully!')"
```

#### 5. Download Pre-trained Models

Ensure all trained models are available in the `Fusion_API/artifacts/` directory:

- ML models: `ml_models/`
- DL models: `dl_models/`
- Scalers: `scalers/`
- Meta-learner: `meta_learner/`

#### 6. Start the API Server

**Option A: Using PowerShell (Windows)**

```powershell
cd Fusion_API
.\run.ps1
```

**Option B: Using Bash (Linux/Mac)**

```bash
cd Fusion_API
chmod +x run.sh
./run.sh
```

**Option C: Manual Start**

```bash
cd Fusion_API/app
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 7. Verify API is Running

- **API Endpoint**: http://127.0.0.1:8000
- **Interactive Docs**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health

### Expected Startup Output

```
Starting Fusion API - Hybrid Fraud Detection System
=======================================================
Installing dependencies...
Navigating to app directory...
Starting API server on http://127.0.0.1:8000
API Documentation: http://127.0.0.1:8000/docs

INFO: Loading ML models...
INFO: Loading DL models...
INFO: Loading meta-learner...
INFO: Loading scalers...
INFO: Initializing SHAP explainer...
INFO: All models loaded successfully!
INFO: Application startup complete.
INFO: Uvicorn running on http://127.0.0.1:8000
```

## API Usage

### API Endpoints

| Endpoint   | Method | Description                          |
| ---------- | ------ | ------------------------------------ |
| `/health`  | GET    | System health check and model status |
| `/predict` | POST   | Fraud detection prediction           |
| `/explain` | POST   | Prediction with SHAP explanations    |
| `/info`    | GET    | API version and model information    |
| `/docs`    | GET    | Interactive API documentation        |

### Example Requests

#### 1. Health Check

```bash
curl -X GET "http://127.0.0.1:8000/health"
```

**Response:**

```json
{
  "status": "Healthy",
  "message": "All systems operational",
  "models_loaded": {
    "ml_models": 5,
    "dl_models": 8,
    "meta_learner": true,
    "explainer_ready": true
  },
  "total_models": 13
}
```

#### 2. Fraud Prediction

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d @Fusion_API/sample_requests/high_fraud_sample.json
```

**Response:**

```json
{
  "status": "success",
  "is_fraud": true,
  "fraud_probability": 0.8456,
  "confidence": 0.9234,
  "risk_score": 8.456,
  "processing_time_ms": 1247.3,
  "model_version": "1.0.0"
}
```

#### 3. Explainable Prediction

```bash
curl -X POST "http://127.0.0.1:8000/explain" \
  -H "Content-Type: application/json" \
  -d @Fusion_API/sample_requests/high_fraud_sample.json
```

**Response:**

```json
{
  "prediction": {
    "is_fraud": true,
    "probability": 0.8456,
    "confidence": 0.9234
  },
  "explanation": {
    "prediction_summary": {
      "status": "HIGH FRAUD RISK",
      "risk_level": "Critical",
      "confidence": 0.9234
    },
    "feature_importance": [
      {
        "feature": "v257_critical_rank001",
        "value": 8.5432,
        "importance": 0.2156,
        "impact": "INCREASES fraud risk"
      }
    ],
    "risk_factors": [
      {
        "factor": "Extremely high transaction amount pattern",
        "severity": "Critical"
      }
    ],
    "explanation": "High fraud probability due to suspicious transaction patterns...",
    "recommendations": [
      "Immediate manual review required",
      "Verify customer identity"
    ]
  }
}
```

### Python Client Example

```python
import requests
import json

# API base URL
BASE_URL = "http://127.0.0.1:8000"

# Load sample data
with open("Fusion_API/sample_requests/high_fraud_sample.json", "r") as f:
    sample_data = json.load(f)

# Make prediction request
response = requests.post(f"{BASE_URL}/predict", json=sample_data)
prediction = response.json()

print(f"Fraud Probability: {prediction['fraud_probability']:.4f}")
print(f"Is Fraud: {prediction['is_fraud']}")
print(f"Confidence: {prediction['confidence']:.4f}")

# Get explanation
response = requests.post(f"{BASE_URL}/explain", json=sample_data)
explanation = response.json()

print(f"Risk Level: {explanation['explanation']['prediction_summary']['risk_level']}")
print(f"Top Risk Factor: {explanation['explanation']['risk_factors'][0]['factor']}")
```

## Model Training

### Training Pipeline Overview

The model training process consists of three main phases:

#### Phase 1: Base Model Training

1. **ML Models Training** (`model/ml/01_ml_models_training_and_tuning.ipynb`)

   - Train 5 machine learning models
   - Hyperparameter tuning using GridSearch/RandomSearch
   - Cross-validation and performance evaluation
   - Save best models to artifacts

2. **DL Models Training** (`model/dl/01_dl_models_training_and_tuning.ipynb`)
   - Train 8 deep learning models
   - Neural architecture optimization
   - Early stopping and regularization
   - Model checkpointing and saving

#### Phase 2: Hybrid Ensemble Creation

3. **Fusion Ensemble** (`model/hybrid/01_ml_dl_hybrid_fusion_ensemble.ipynb`)

   - Load all pre-trained base models
   - Generate predictions on validation set
   - Create fusion dataset for meta-learner training
   - Evaluate ensemble performance

4. **Meta-Learner Training** (`model/hybrid/02_meta_learner_fusion_training.ipynb`)
   - Train Logistic Regression meta-learner
   - Optimize decision threshold for F1-score
   - Final model validation and testing
   - Save complete hybrid system

#### Phase 3: Explainability Analysis

5. **SHAP Analysis** (`model/hybrid/03_explainability_shap_analysis.ipynb`)
   - Initialize SHAP explainer with trained models
   - Generate global feature importance
   - Create local explanations for sample cases
   - Validate explainability system

### Training from Scratch

To retrain the entire system:

1. **Prepare Data**: Ensure processed data is available in `data/processed_data/`
2. **Run Training Notebooks**: Execute notebooks in sequence (01 → 02 → 03)
3. **Validate Models**: Check model performance and save artifacts
4. **Update API**: Restart API server to load new models

### Custom Model Addition

To add new models to the ensemble:

1. Train your model using the same data preprocessing pipeline
2. Save model artifacts in the appropriate directory
3. Update `model_loader.py` to include your model
4. Retrain the meta-learner with the new model predictions
5. Update API configuration and restart server

## Explainability

### SHAP Integration

The system uses SHAP (SHapley Additive exPlanations) for model interpretability:

#### Global Explanations

- **Feature Importance**: Overall impact of each feature across all predictions
- **Feature Interactions**: How features work together to influence decisions
- **Model Behavior**: Understanding of model decision patterns

#### Local Explanations

- **Individual Predictions**: Why a specific transaction was flagged as fraud
- **Feature Contributions**: How each feature contributed to the final decision
- **Counterfactual Analysis**: What would change the prediction

#### Business Value

- **Regulatory Compliance**: Transparent AI for financial regulations
- **Trust Building**: Explainable decisions increase user confidence
- **Model Debugging**: Identify potential biases or errors
- **Domain Insights**: Learn new fraud patterns from model explanations

### Explanation API Usage

The `/explain` endpoint provides comprehensive explanations including:

- Prediction summary with risk level
- Top contributing features with importance scores
- Identified risk factors with severity levels
- Human-readable explanations
- Actionable recommendations

## Troubleshooting

### Common Issues

#### 1. Model Loading Errors

**Error**: `FileNotFoundError: Model file not found`
**Solution**:

- Verify all model files exist in `Fusion_API/artifacts/`
- Check file permissions and paths
- Re-run training notebooks if models are missing

#### 2. Memory Issues

**Error**: `MemoryError: Unable to allocate memory`
**Solution**:

- Increase system RAM (minimum 8GB recommended)
- Close other applications
- Consider loading models on-demand instead of all at startup

#### 3. API Startup Failures

**Error**: `Port already in use`
**Solution**:

- Change port in startup script: `--port 8001`
- Kill existing processes: `pkill -f uvicorn`
- Use different port: `python -m uvicorn main:app --port 8001`

#### 4. Prediction Errors

**Error**: `Invalid input format`
**Solution**:

- Verify input data has exactly 63 features
- Check feature names match expected format
- Validate data types (all numeric)
- Review sample requests for correct format

### Performance Optimization

#### 1. Model Loading Optimization

- Load models asynchronously during startup
- Use model caching for frequently accessed models
- Implement lazy loading for less critical models

#### 2. Prediction Speed Optimization

- Use batch predictions for multiple transactions
- Implement model result caching
- Optimize preprocessing pipeline

#### 3. Memory Management

- Implement model unloading for unused models
- Use model quantization for smaller memory footprint
- Configure garbage collection optimization

## Contributing

We welcome contributions to improve the fraud detection system! Here's how you can contribute:

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with proper testing
4. Ensure code follows project style guidelines
5. Submit a pull request with detailed description

### Contribution Areas

- **Model Improvements**: New algorithms, better hyperparameters
- **API Enhancements**: New endpoints, better error handling
- **Performance Optimization**: Speed improvements, memory efficiency
- **Documentation**: Better guides, examples, tutorials
- **Testing**: Unit tests, integration tests, performance tests

### Code Style Guidelines

- Follow PEP 8 for Python code formatting
- Use meaningful variable and function names
- Add docstrings for all functions and classes
- Include type hints where appropriate
- Write comprehensive test coverage

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **SHAP**: For providing excellent model explainability framework
- **FastAPI**: For the high-performance API framework
- **Scikit-learn**: For comprehensive machine learning tools
- **TensorFlow**: For deep learning model development
- **Open Source Community**: For the amazing tools and libraries

## Contact

For questions, issues, or collaboration opportunities:

- **Repository**: [fraude-detection-hybrid-api](https://github.com/Kiyas-Mahmud/fraude-detection-hybrid-api)
- **Issues**: [GitHub Issues](https://github.com/Kiyas-Mahmud/fraude-detection-hybrid-api/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Kiyas-Mahmud/fraude-detection-hybrid-api/discussions)

---

## Quick Start Summary

```bash
# 1. Clone repository
git clone https://github.com/Kiyas-Mahmud/fraude-detection-hybrid-api.git
cd fraude-detection-hybrid-api

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start API server
cd Fusion_API
.\run.ps1  # Windows
# ./run.sh  # Linux/Mac

# 5. Test API
curl http://127.0.0.1:8000/health

# 6. View documentation
# Open: http://127.0.0.1:8000/docs
```

**System Status**: Production Ready ✓  
**Documentation**: Complete ✓  
**API**: Fully Functional ✓  
**Models**: Trained & Validated ✓

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
