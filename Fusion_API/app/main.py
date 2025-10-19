"""
Main FastAPI Application for Hybrid Fraud Detection API

Endpoints:
- GET /health: Health check
- POST /predict: Fraud prediction
- POST /explain: Prediction explanation  
- GET /info: API and model information
"""

import logging
import traceback
from datetime import datetime
from typing import Dict, Any, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

# Import our custom modules
from model_loader import initialize_models, get_models
from preprocessing import create_preprocessor, validate_and_preprocess
from inference import create_inference_engine
from explainability import initialize_explainer, get_explanation, is_explainer_ready

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class TransactionRequest(BaseModel):
    """Request model for transaction prediction expecting 63 features"""
    
    def __init__(self, **data):
        super().__init__(**data)
    
    @validator('*', pre=True)
    def validate_numeric_fields(cls, v):
        try:
            return float(v)
        except (ValueError, TypeError):
            raise ValueError(f"All features must be numeric, got: {type(v)}")
    
    class Config:
        extra = "forbid"
        schema_extra = {
            "example": {f"feature_{i}": 0.5 for i in range(63)}
        }

class PredictionResponse(BaseModel):
    """Response model for fraud prediction"""
    status: str = Field(..., description="Fraud or Safe")
    probability: float = Field(..., description="Fraud probability (0-1)")
    calibrated_probability: float = Field(..., description="Calibrated fraud probability")
    confidence: float = Field(..., description="Prediction confidence (0-1)")
    prediction: int = Field(..., description="Binary prediction (0=Safe, 1=Fraud)")
    threshold_used: float = Field(..., description="Threshold used for classification")
    inference_time_ms: float = Field(..., description="Inference time in milliseconds")
    model_stats: Dict[str, int] = Field(..., description="Model usage statistics")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    message: str
    models_loaded: Dict[str, Any]
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class ExplanationResponse(BaseModel):
    """Response model for prediction explanation"""
    prediction: PredictionResponse
    explanation: Dict[str, Any]
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# Initialize FastAPI app
app = FastAPI(
    title="Hybrid Fraud Detection API",
    description="Advanced fraud detection using ML+DL ensemble with meta-learning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models_initialized = False
preprocessor = None
inference_engine = None
model_info = None
explainer_ready = False

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global models_initialized, preprocessor, inference_engine, model_info, explainer_ready
    
    logger.info("Starting Hybrid Fraud Detection API...")
    
    try:
        # Initialize models
        logger.info("Loading models...")
        result = initialize_models()
        
        if not result["ready"]:
            logger.error("Model initialization failed")
            return
        
        # Get loaded models
        ml_models, dl_models, hybrid_models, scalers = get_models()
        
        # Create preprocessor
        preprocessor = create_preprocessor(scalers)
        logger.info("Preprocessor created")
        
        # Create inference engine
        inference_engine = create_inference_engine(ml_models, dl_models, hybrid_models, scalers)
        logger.info("Inference engine created")
        
        try:
            import json
            try:
                with open('../../actual_features.json', 'r') as f:
                    feature_names = json.load(f)
            except:
                feature_names = [f"feature_{i}" for i in range(63)]
            
            all_models = {**ml_models, **dl_models}
            if hybrid_models:
                all_models.update(hybrid_models)
            
            explainer_ready = initialize_explainer(all_models, feature_names)
            if explainer_ready:
                logger.info("Explainer initialized successfully")
            else:
                logger.warning("Explainer initialization failed, basic explanations will be used")
                
        except Exception as e:
            logger.warning(f"Explainer initialization error: {e}")
            explainer_ready = False
        
        model_info = result
        models_initialized = True
        
        logger.info("Hybrid Fraud Detection API is ready!")
        logger.info(f"Loaded {len(ml_models)} ML + {len(dl_models)} DL models")
        
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        logger.error(traceback.format_exc())

@app.get("/", response_model=Dict[str, str])
async def root():
    return {
        "message": "Hybrid Fraud Detection API", 
        "version": "1.0.0",
        "status": "Running" if models_initialized else "Initializing",
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    try:
        if not models_initialized:
            return HealthResponse(
                status="Initializing",
                message="Models are still loading...",
                models_loaded={}
            )
        
        engine_info = inference_engine.get_engine_info() if inference_engine else {}
        
        return HealthResponse(
            status="Healthy" if models_initialized else "Unhealthy",
            message="API is running and models are loaded" if models_initialized else "Models not loaded",
            models_loaded={
                **engine_info,
                "explainer_ready": explainer_ready,
                "explainability_available": is_explainer_ready()
            }
        )
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.post("/predict", response_model=PredictionResponse)
async def predict_fraud(transaction: Dict[str, float]):
    try:
        if not models_initialized:
            raise HTTPException(status_code=503, detail="Models not initialized")
        
        success, preprocessed_data = validate_and_preprocess(transaction, preprocessor)
        
        if not success:
            raise HTTPException(status_code=400, detail=preprocessed_data["error"])
        
        result = inference_engine.predict(preprocessed_data)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        response = PredictionResponse(
            status=result["status"],
            probability=result["probability"],
            calibrated_probability=result["calibrated_probability"],
            confidence=result["confidence"],
            prediction=result["prediction"],
            threshold_used=result["threshold_used"],
            inference_time_ms=result["inference_time_ms"],
            model_stats=result["model_stats"]
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/explain", response_model=ExplanationResponse)
async def explain_prediction_endpoint(transaction: Dict[str, float]):
    try:
        if not models_initialized:
            raise HTTPException(status_code=503, detail="Models not initialized")
        
        success, preprocessed_data = validate_and_preprocess(transaction, preprocessor)
        
        if not success:
            raise HTTPException(status_code=400, detail=preprocessed_data["error"])
        
        prediction_result = inference_engine.predict(preprocessed_data)
        
        if "error" in prediction_result:
            raise HTTPException(status_code=500, detail=prediction_result["error"])
        
        explanation_data = get_explanation(transaction, prediction_result)
        
        prediction_response = PredictionResponse(
            status=prediction_result["status"],
            probability=prediction_result["probability"],
            calibrated_probability=prediction_result["calibrated_probability"],
            confidence=prediction_result["confidence"],
            prediction=prediction_result["prediction"],
            threshold_used=prediction_result["threshold_used"],
            inference_time_ms=prediction_result["inference_time_ms"],
            model_stats=prediction_result["model_stats"]
        )
        
        return ExplanationResponse(
            prediction=prediction_response,
            explanation=explanation_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Explanation error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")

@app.get("/info", response_model=Dict[str, Any])
async def get_api_info():
    try:
        if not models_initialized:
            return {"status": "Models not initialized"}
        
        preprocessor_info = preprocessor.get_feature_info() if preprocessor else {}
        engine_info = inference_engine.get_engine_info() if inference_engine else {}
        
        return {
            "api_info": {
                "title": "Hybrid Fraud Detection API",
                "version": "1.0.0",
                "status": "Running",
                "startup_time": datetime.now().isoformat()
            },
            "model_info": engine_info,
            "preprocessing_info": preprocessor_info,
            "explainability_info": {
                "enabled": explainer_ready,
                "methods": ["SHAP Values", "Feature Importance", "Risk Factor Analysis"],
                "features": [
                    "Real-time explanations",
                    "Feature contribution analysis", 
                    "Risk factor identification",
                    "Actionable recommendations"
                ]
            },
            "endpoints": {
                "/health": "Health check and system status",
                "/predict": "Fraud prediction with probability scores", 
                "/explain": "Prediction with detailed SHAP-based explanation",
                "/info": "API and model information",
                "/docs": "Interactive API documentation"
            }
        }
        
    except Exception as e:
        logger.error(f"Info endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Info retrieval failed: {str(e)}")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8001,
        reload=False,
        log_level="info"
    )