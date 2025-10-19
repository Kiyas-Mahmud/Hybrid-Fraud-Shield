"""
Model Loader Module for Hybrid Fraud Detection API
Handles loading of ML, DL, and hybrid models from the artifacts directory.
"""

import os
import json
import joblib
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelLoader:
    """Handles loading and management of all fraud detection models"""
    
    def __init__(self, artifacts_path: str = "../artifacts"):
        self.artifacts_path = Path(artifacts_path).resolve()
        self.ml_models = {}
        self.dl_models = {}
        self.hybrid_models = {}
        self.scalers = {}
        self.config = {}
        
        logger.info(f"Initialized ModelLoader with artifacts path: {self.artifacts_path}")
    
    def load_all_models(self) -> Dict[str, bool]:
        status = {}
        
        try:
            status['scalers'] = self._load_scalers()
            status['ml_models'] = self._load_ml_models()
            status['dl_models'] = self._load_dl_models()
            status['hybrid_models'] = self._load_hybrid_models()
            status['config'] = self._load_config()
            
            logger.info("All models loaded successfully")
            return status
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            return {"error": str(e)}
    
    def _load_scalers(self) -> bool:
        try:
            scaler_path = self.artifacts_path / "standard_scaler.pkl"
            if scaler_path.exists():
                self.scalers['standard'] = joblib.load(scaler_path)
                logger.info("StandardScaler loaded")
            
            scaler_path = self.artifacts_path / "minmax_scaler.pkl"
            if scaler_path.exists():
                self.scalers['minmax'] = joblib.load(scaler_path)
                logger.info("MinMaxScaler loaded")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading scalers: {str(e)}")
            return False
    
    def _load_ml_models(self) -> bool:
        try:
            ml_path = self.artifacts_path / "ml"
            
            ml_model_files = {
                'logistic_regression': 'logistic_regression_model.pkl',
                'random_forest': 'random_forest_model.pkl', 
                'xgboost': 'xgboost_model.pkl',
                'xgboost_smote': 'xgboost_smote_model.pkl',
                'catboost': 'catboost_model.pkl',
                'isolation_forest': 'isolation_forest_model.pkl'
            }
            
            loaded_count = 0
            for model_name, filename in ml_model_files.items():
                model_path = ml_path / filename
                if model_path.exists():
                    try:
                        self.ml_models[model_name] = joblib.load(model_path)
                        logger.info(f"ML Model loaded: {model_name}")
                        loaded_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to load {model_name}: {str(e)}")
                else:
                    logger.warning(f"ML Model not found: {filename}")
            
            logger.info(f"Loaded {loaded_count}/{len(ml_model_files)} ML models")
            return loaded_count > 0
            
        except Exception as e:
            logger.error(f"Error loading ML models: {str(e)}")
            return False
    
    def _load_dl_models(self) -> bool:
        try:
            dl_path = self.artifacts_path / "dl"
            
            dl_model_files = {
                'fnn': 'fnn_model.keras',
                'fnn_tuned': 'fnn_tuned_model.keras',
                'cnn': 'cnn_model.keras',
                'cnn_tuned': 'cnn_tuned_model.keras',
                'lstm': 'lstm_model.keras',
                'bilstm': 'bilstm_model.keras',
                'cnn_bilstm': 'cnn_bilstm_model.keras',
                'autoencoder': 'autoencoder_model.keras'
            }
            
            loaded_count = 0
            for model_name, filename in dl_model_files.items():
                model_path = dl_path / filename
                if model_path.exists():
                    try:
                        self.dl_models[model_name] = keras.models.load_model(model_path)
                        logger.info(f"DL Model loaded: {model_name}")
                        loaded_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to load {model_name}: {str(e)}")
                else:
                    logger.warning(f"DL Model not found: {filename}")
            
            logger.info(f"Loaded {loaded_count}/{len(dl_model_files)} DL models")
            return loaded_count > 0
            
        except Exception as e:
            logger.error(f"Error loading DL models: {str(e)}")
            return False
    
    def _load_hybrid_models(self) -> bool:
        try:
            hybrid_path = self.artifacts_path / "hybrid"
            
            meta_model_path = hybrid_path / "meta_model.pkl"
            if meta_model_path.exists():
                self.hybrid_models['meta_learner'] = joblib.load(meta_model_path)
                logger.info("Meta-learner loaded")
            
            calibrated_model_path = hybrid_path / "fusion_calibrator.pkl"
            if calibrated_model_path.exists():
                self.hybrid_models['calibrated'] = joblib.load(calibrated_model_path)
                logger.info("Calibrated model loaded")
            
            threshold_path = hybrid_path / "best_threshold.json"
            if threshold_path.exists():
                with open(threshold_path, 'r') as f:
                    threshold_config = json.load(f)
                    self.hybrid_models['threshold'] = threshold_config['best_threshold']
                    logger.info(f"Optimal threshold loaded: {self.hybrid_models['threshold']}")
            
            return len(self.hybrid_models) > 0
            
        except Exception as e:
            logger.error(f"Error loading hybrid models: {str(e)}")
            return False
    
    def _load_config(self) -> bool:
        try:
            config_path = self.artifacts_path / "hybrid" / "deployment_config.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
                    logger.info("Deployment configuration loaded")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "ml_models": list(self.ml_models.keys()),
            "dl_models": list(self.dl_models.keys()), 
            "hybrid_models": list(self.hybrid_models.keys()),
            "scalers": list(self.scalers.keys()),
            "total_models": len(self.ml_models) + len(self.dl_models),
            "config_loaded": bool(self.config)
        }
    
    def validate_models(self) -> Dict[str, bool]:
        validation = {
            "has_ml_models": len(self.ml_models) > 0,
            "has_dl_models": len(self.dl_models) > 0,
            "has_meta_learner": "meta_learner" in self.hybrid_models,
            "has_threshold": "threshold" in self.hybrid_models,
            "has_scalers": len(self.scalers) > 0,
            "ready_for_inference": False
        }
        
        validation["ready_for_inference"] = all([
            validation["has_ml_models"],
            validation["has_dl_models"], 
            validation["has_meta_learner"],
            validation["has_threshold"],
            validation["has_scalers"]
        ])
        
        return validation

model_loader = ModelLoader()

def initialize_models() -> Dict[str, Any]:
    logger.info("Initializing Fraud Detection Models...")
    
    load_status = model_loader.load_all_models()
    model_info = model_loader.get_model_info()
    validation = model_loader.validate_models()
    
    result = {
        "load_status": load_status,
        "model_info": model_info,
        "validation": validation,
        "ready": validation["ready_for_inference"]
    }
    
    if result["ready"]:
        logger.info("All models initialized successfully - Ready for inference!")
    else:
        logger.error("Model initialization incomplete - Check logs for details")
    
    return result

def get_models() -> Tuple[Dict, Dict, Dict, Dict]:
    return (
        model_loader.ml_models,
        model_loader.dl_models, 
        model_loader.hybrid_models,
        model_loader.scalers
    )

if __name__ == "__main__":
    # Test model loading
    result = initialize_models()
    print(json.dumps(result, indent=2))