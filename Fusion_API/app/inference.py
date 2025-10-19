"""
Inference Engine for Hybrid Fraud Detection API
Combines predictions from ML and DL models using meta-learner.
"""

import logging
import time
from typing import Dict, List, Any, Tuple, Optional

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridInferenceEngine:
    """Handles hybrid inference combining ML, DL, and meta-learning predictions"""
    
    def __init__(self, ml_models: Dict, dl_models: Dict, hybrid_models: Dict, scalers: Dict):
        self.ml_models = ml_models
        self.dl_models = dl_models
        self.hybrid_models = hybrid_models
        self.scalers = scalers
        
        self.optimal_threshold = hybrid_models.get('threshold', 0.5)
        
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
        
        self.excluded_models = {'isolation_forest'}
        
        logger.info(f"Initialized HybridInferenceEngine with:")
        logger.info(f"  - ML Models: {len(ml_models)}")
        logger.info(f"  - DL Models: {len(dl_models)}")
        logger.info(f"  - Optimal Threshold: {self.optimal_threshold}")
    
    def generate_ml_predictions(self, ml_scaled: pd.DataFrame, ml_unscaled: pd.DataFrame) -> Dict[str, float]:
        ml_predictions = {}
        
        try:
            for model_name, model in self.ml_models.items():
                if model_name in self.excluded_models:
                    continue
                    
                if model_name == 'logistic_regression':
                    pred_proba = model.predict_proba(ml_scaled)[:, 1][0]
                elif model_name == 'isolation_forest':
                    anomaly_score = model.decision_function(ml_unscaled)[0]
                    pred_proba = 1.0 / (1.0 + np.exp(anomaly_score))
                else:
                    pred_proba = model.predict_proba(ml_unscaled)[:, 1][0]
                
                ml_predictions[model_name] = float(pred_proba)
                
            logger.debug(f"Generated {len(ml_predictions)} ML predictions")
            return ml_predictions
            
        except Exception as e:
            logger.error(f"Error generating ML predictions: {str(e)}")
            raise
    
    def generate_dl_predictions(self, dl_data: np.ndarray) -> Dict[str, float]:
        dl_predictions = {}
        
        try:
            for model_name, model in self.dl_models.items():
                if model_name == 'autoencoder':
                    reconstructed = model.predict(dl_data, verbose=0)
                    reconstruction_error = np.mean((dl_data - reconstructed) ** 2, axis=1)[0]
                    pred_proba = min(max(reconstruction_error / 10.0, 0.0), 1.0)
                else:
                    pred_proba = model.predict(dl_data, verbose=0).ravel()[0]
                
                dl_predictions[model_name] = float(pred_proba)
                
            logger.debug(f"Generated {len(dl_predictions)} DL predictions")
            return dl_predictions
            
        except Exception as e:
            logger.error(f"Error generating DL predictions: {str(e)}")
            raise
    
    def combine_predictions(self, ml_predictions: Dict[str, float], dl_predictions: Dict[str, float]) -> Dict[str, Any]:
        try:
            all_predictions = {**ml_predictions, **dl_predictions}
            fusion_data = {}
            
            for model_key, prediction in ml_predictions.items():
                if model_key == 'logistic_regression':
                    fusion_data['Logistic Regression_pred'] = prediction
                elif model_key == 'random_forest':
                    fusion_data['Random Forest_pred'] = prediction
                elif model_key == 'xgboost':
                    fusion_data['XGBoost_pred'] = prediction
                elif model_key == 'xgboost_smote':
                    fusion_data['XGBoost SMOTE_pred'] = prediction
                elif model_key == 'catboost':
                    fusion_data['CatBoost_pred'] = prediction
            
            for model_key, prediction in dl_predictions.items():
                if model_key == 'fnn':
                    fusion_data['FNN_pred'] = prediction
                elif model_key == 'fnn_tuned':
                    fusion_data['FNN Tuned_pred'] = prediction
                elif model_key == 'cnn':
                    fusion_data['CNN_pred'] = prediction
                elif model_key == 'cnn_tuned':
                    fusion_data['CNN Tuned_pred'] = prediction
                elif model_key == 'lstm':
                    fusion_data['LSTM_pred'] = prediction
                elif model_key == 'bilstm':
                    fusion_data['BiLSTM_pred'] = prediction
                elif model_key == 'cnn_bilstm':
                    fusion_data['CNN-BiLSTM_pred'] = prediction
                elif model_key == 'autoencoder':
                    fusion_data['Autoencoder_pred'] = prediction
            
            expected_features = [
                'Logistic Regression_pred', 'Random Forest_pred', 'XGBoost_pred', 
                'XGBoost SMOTE_pred', 'CatBoost_pred', 'FNN_pred', 'FNN Tuned_pred', 
                'CNN_pred', 'CNN Tuned_pred', 'LSTM_pred', 'BiLSTM_pred', 
                'CNN-BiLSTM_pred', 'Autoencoder_pred'
            ]
            
            available_predictions = list(fusion_data.values())
            if available_predictions:
                default_value = np.mean(available_predictions)
            else:
                default_value = 0.5
            
            for feature in expected_features:
                if feature not in fusion_data:
                    fusion_data[feature] = default_value
                    logger.warning(f"Missing model prediction for {feature}, using default: {default_value:.3f}")
            
            fusion_features = pd.DataFrame([fusion_data])
            meta_learner = self.hybrid_models['meta_learner']
            final_probability = meta_learner.predict_proba(fusion_features)[:, 1][0]
            final_prediction = int(final_probability >= self.optimal_threshold)
            status = "Fraud" if final_prediction == 1 else "Safe"
            confidence = abs(final_probability - self.optimal_threshold) / 0.5
            confidence = min(max(confidence, 0.0), 1.0)
            
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
        start_time = time.time()
        
        try:
            ml_predictions = self.generate_ml_predictions(
                preprocessed_data['ml_scaled'],
                preprocessed_data['ml_unscaled']
            )
            
            dl_predictions = self.generate_dl_predictions(preprocessed_data['dl_data'])
            final_result = self.combine_predictions(ml_predictions, dl_predictions)
            
            inference_time = time.time() - start_time
            final_result['inference_time_ms'] = round(inference_time * 1000, 2)
            
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
        try:
            ml_predictions = self.generate_ml_predictions(
                preprocessed_data['ml_scaled'],
                preprocessed_data['ml_unscaled']
            )
            dl_predictions = self.generate_dl_predictions(preprocessed_data['dl_data'])
            all_predictions = {**ml_predictions, **dl_predictions}
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
        return {
            "ml_models": list(self.ml_models.keys()),
            "dl_models": list(self.dl_models.keys()),
            "hybrid_models": list(self.hybrid_models.keys()),
            "optimal_threshold": self.optimal_threshold,
            "total_base_models": len(self.ml_models) + len(self.dl_models),
            "ready": len(self.ml_models) > 0 and len(self.dl_models) > 0 and 'meta_learner' in self.hybrid_models
        }

def create_inference_engine(ml_models: Dict, dl_models: Dict, hybrid_models: Dict, scalers: Dict) -> HybridInferenceEngine:
    return HybridInferenceEngine(ml_models, dl_models, hybrid_models, scalers)

if __name__ == "__main__":
    print("Inference engine module loaded successfully")
    print("Use create_inference_engine() to initialize with loaded models")