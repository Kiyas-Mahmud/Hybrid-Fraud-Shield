"""
Inference Engine for Hybrid Fraud Detection API

This module combines predictions from ML and DL models using the trained meta-learner
and applies the optimal threshold for final fraud detection.

Author: Fraud Detection Team  
Date: October 2025
"""

import logging
import time
from typing import Dict, List, Any, Tuple, Optional

import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridInferenceEngine:
    """
    Handles hybrid inference combining ML, DL, and meta-learning predictions
    """
    
    def __init__(self, ml_models: Dict, dl_models: Dict, hybrid_models: Dict, scalers: Dict):
        """
        Initialize the inference engine
        
        Args:
            ml_models (Dict): Loaded ML models
            dl_models (Dict): Loaded DL models  
            hybrid_models (Dict): Loaded hybrid models (meta-learner, threshold)
            scalers (Dict): Loaded scalers
        """
        self.ml_models = ml_models
        self.dl_models = dl_models
        self.hybrid_models = hybrid_models
        self.scalers = scalers
        
        # Get optimal threshold
        self.optimal_threshold = hybrid_models.get('threshold', 0.5)
        
        # Define proper model name mappings for meta-learner (only models used in training)
        self.ml_name_mapping = {
            'logistic_regression': 'Logistic Regression',
            'random_forest': 'Random Forest',
            'xgboost': 'XGBoost',
            'xgboost_smote': 'XGBoost SMOTE',
            'catboost': 'CatBoost'
        }
        
        self.dl_name_mapping = {
            'fnn': 'FNN',
            'fnn_tuned': 'FNN Tuned',
            'cnn': 'CNN',
            'cnn_tuned': 'CNN Tuned',
            'lstm': 'LSTM',
            'bilstm': 'BiLSTM',
            'cnn_bilstm': 'CNN-BiLSTM',
            'autoencoder': 'Autoencoder'
        }
        
        # Models to exclude from meta-learner (not used in training)
        self.excluded_models = {'isolation_forest'}
        
        logger.info(f"Initialized HybridInferenceEngine with:")
        logger.info(f"  - ML Models: {len(ml_models)}")
        logger.info(f"  - DL Models: {len(dl_models)}")
        logger.info(f"  - Optimal Threshold: {self.optimal_threshold}")
    
    def generate_ml_predictions(self, ml_scaled: pd.DataFrame, ml_unscaled: pd.DataFrame) -> Dict[str, float]:
        """
        Generate predictions from all ML models
        
        Args:
            ml_scaled (pd.DataFrame): Scaled data for Logistic Regression
            ml_unscaled (pd.DataFrame): Unscaled data for tree-based models
            
        Returns:
            Dict[str, float]: ML model predictions
        """
        ml_predictions = {}
        
        try:
            for model_name, model in self.ml_models.items():
                # Skip models not used in meta-learner training
                if model_name in self.excluded_models:
                    continue
                    
                if model_name == 'logistic_regression':
                    # Logistic Regression uses scaled data
                    pred_proba = model.predict_proba(ml_scaled)[:, 1][0]
                elif model_name == 'isolation_forest':
                    # Isolation Forest returns anomaly scores, convert to probabilities
                    anomaly_score = model.decision_function(ml_unscaled)[0]
                    # Convert to probability (higher score = more normal, so invert)
                    pred_proba = 1.0 / (1.0 + np.exp(anomaly_score))
                else:
                    # Tree-based models (RF, XGBoost, CatBoost) use unscaled data
                    pred_proba = model.predict_proba(ml_unscaled)[:, 1][0]
                
                # Use proper name mapping for meta-learner
                display_name = self.ml_name_mapping.get(model_name, model_name)
                ml_predictions[f'{display_name}_pred'] = float(pred_proba)
                
            logger.debug(f"Generated {len(ml_predictions)} ML predictions")
            return ml_predictions
            
        except Exception as e:
            logger.error(f"Error generating ML predictions: {str(e)}")
            raise
    
    def generate_dl_predictions(self, dl_data: np.ndarray) -> Dict[str, float]:
        """
        Generate predictions from all DL models
        
        Args:
            dl_data (np.ndarray): Scaled data for DL models
            
        Returns:
            Dict[str, float]: DL model predictions
        """
        dl_predictions = {}
        
        try:
            for model_name, model in self.dl_models.items():
                if model_name == 'autoencoder':
                    # Autoencoder: calculate reconstruction error as anomaly score
                    reconstructed = model.predict(dl_data, verbose=0)
                    reconstruction_error = np.mean((dl_data - reconstructed) ** 2, axis=1)[0]
                    
                    # Normalize to [0,1] range (simple normalization)
                    # In production, you might want to use the same normalization as training
                    pred_proba = min(max(reconstruction_error / 10.0, 0.0), 1.0)
                else:
                    # Regular DL classification models
                    pred_proba = model.predict(dl_data, verbose=0).ravel()[0]
                
                # Use proper name mapping for meta-learner
                display_name = self.dl_name_mapping.get(model_name, model_name)
                dl_predictions[f'{display_name}_pred'] = float(pred_proba)
                
            logger.debug(f"Generated {len(dl_predictions)} DL predictions")
            return dl_predictions
            
        except Exception as e:
            logger.error(f"Error generating DL predictions: {str(e)}")
            raise
    
    def combine_predictions(self, ml_predictions: Dict[str, float], dl_predictions: Dict[str, float]) -> Dict[str, Any]:
        """
        Combine ML and DL predictions using the meta-learner
        
        Args:
            ml_predictions (Dict): ML model predictions
            dl_predictions (Dict): DL model predictions
            
        Returns:
            Dict[str, Any]: Final prediction results
        """
        try:
            # Combine all predictions into fusion feature vector
            all_predictions = {**ml_predictions, **dl_predictions}
            
            # Create DataFrame for meta-learner input
            fusion_features = pd.DataFrame([all_predictions])
            
            # Get meta-learner
            meta_learner = self.hybrid_models['meta_learner']
            
            # Generate final probability
            final_probability = meta_learner.predict_proba(fusion_features)[:, 1][0]
            
            # Apply optimal threshold
            final_prediction = int(final_probability >= self.optimal_threshold)
            
            # Determine status
            status = "Fraud" if final_prediction == 1 else "Safe"
            
            # Calculate confidence (distance from threshold)
            confidence = abs(final_probability - self.optimal_threshold) / 0.5
            confidence = min(max(confidence, 0.0), 1.0)  # Clamp to [0,1]
            
            # Use calibrated model if available
            calibrated_probability = final_probability
            if 'calibrated' in self.hybrid_models:
                try:
                    calibrated_probability = self.hybrid_models['calibrated'].predict_proba(fusion_features)[:, 1][0]
                except Exception as e:
                    logger.warning(f"Calibrated model failed, using meta-learner: {str(e)}")
            
            return {
                "status": status,
                "probability": float(final_probability),
                "calibrated_probability": float(calibrated_probability),
                "confidence": float(confidence),
                "prediction": final_prediction,
                "threshold_used": self.optimal_threshold,
                "base_predictions": {
                    "ml_predictions": ml_predictions,
                    "dl_predictions": dl_predictions
                }
            }
            
        except Exception as e:
            logger.error(f"Error combining predictions: {str(e)}")
            raise
    
    def predict(self, preprocessed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main prediction function - combines all models for final prediction
        
        Args:
            preprocessed_data (Dict): Preprocessed data from preprocessing module
            
        Returns:
            Dict[str, Any]: Complete prediction results
        """
        start_time = time.time()
        
        try:
            # Generate ML predictions
            ml_predictions = self.generate_ml_predictions(
                preprocessed_data['ml_scaled'],
                preprocessed_data['ml_unscaled']
            )
            
            # Generate DL predictions
            dl_predictions = self.generate_dl_predictions(preprocessed_data['dl_data'])
            
            # Combine predictions using meta-learner
            final_result = self.combine_predictions(ml_predictions, dl_predictions)
            
            # Add timing information
            inference_time = time.time() - start_time
            final_result['inference_time_ms'] = round(inference_time * 1000, 2)
            
            # Add model statistics
            final_result['model_stats'] = {
                "ml_models_used": len(ml_predictions),
                "dl_models_used": len(dl_predictions),
                "total_base_models": len(ml_predictions) + len(dl_predictions)
            }
            
            logger.info(f"Prediction completed: {final_result['status']} "
                       f"(prob: {final_result['probability']:.4f}, "
                       f"time: {final_result['inference_time_ms']}ms)")
            
            return final_result
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {
                "error": str(e),
                "status": "Error",
                "probability": 0.0,
                "inference_time_ms": round((time.time() - start_time) * 1000, 2)
            }
    
    def get_feature_importance(self, preprocessed_data: Dict[str, Any], top_n: int = 10) -> Dict[str, Any]:
        """
        Get feature importance/explanation for the prediction
        
        Args:
            preprocessed_data (Dict): Preprocessed data
            top_n (int): Number of top features to return
            
        Returns:
            Dict[str, Any]: Feature importance information
        """
        try:
            # This is a simplified feature importance
            # In production, you might want to use SHAP or LIME
            
            # Get base predictions
            ml_predictions = self.generate_ml_predictions(
                preprocessed_data['ml_scaled'],
                preprocessed_data['ml_unscaled']
            )
            dl_predictions = self.generate_dl_predictions(preprocessed_data['dl_data'])
            
            # Analyze which models contributed most
            all_predictions = {**ml_predictions, **dl_predictions}
            
            # Sort by prediction value (higher = more fraud-like)
            sorted_predictions = sorted(all_predictions.items(), key=lambda x: x[1], reverse=True)
            
            return {
                "top_contributing_models": sorted_predictions[:top_n],
                "model_agreement": {
                    "high_risk_models": len([p for p in all_predictions.values() if p > 0.7]),
                    "medium_risk_models": len([p for p in all_predictions.values() if 0.3 <= p <= 0.7]),
                    "low_risk_models": len([p for p in all_predictions.values() if p < 0.3])
                },
                "prediction_spread": {
                    "min_prediction": min(all_predictions.values()),
                    "max_prediction": max(all_predictions.values()),
                    "std_prediction": float(np.std(list(all_predictions.values())))
                }
            }
            
        except Exception as e:
            logger.error(f"Feature importance error: {str(e)}")
            return {"error": str(e)}
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get information about the inference engine"""
        return {
            "ml_models": list(self.ml_models.keys()),
            "dl_models": list(self.dl_models.keys()),
            "hybrid_models": list(self.hybrid_models.keys()),
            "optimal_threshold": self.optimal_threshold,
            "total_base_models": len(self.ml_models) + len(self.dl_models),
            "ready": len(self.ml_models) > 0 and len(self.dl_models) > 0 and 'meta_learner' in self.hybrid_models
        }

def create_inference_engine(ml_models: Dict, dl_models: Dict, hybrid_models: Dict, scalers: Dict) -> HybridInferenceEngine:
    """
    Factory function to create inference engine
    
    Args:
        ml_models (Dict): ML models
        dl_models (Dict): DL models
        hybrid_models (Dict): Hybrid models
        scalers (Dict): Scalers
        
    Returns:
        HybridInferenceEngine: Configured inference engine
    """
    return HybridInferenceEngine(ml_models, dl_models, hybrid_models, scalers)

if __name__ == "__main__":
    # Test inference engine (requires loaded models)
    print("Inference engine module loaded successfully")
    print("Use create_inference_engine() to initialize with loaded models")