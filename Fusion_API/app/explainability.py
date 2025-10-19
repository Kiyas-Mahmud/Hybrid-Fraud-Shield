"""
Explainability module for Hybrid Fraud Detection API
Provides SHAP-based explanations for fraud detection predictions.
"""

import json
import logging
import warnings
from typing import Dict, List, Any, Optional

import numpy as np
import pandas as pd
import shap
from datetime import datetime

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class FraudExplainer:
    """Provides explanations for fraud detection predictions using SHAP values"""
    
    def __init__(self, models_dict: Dict, feature_names: List[str]):
        self.models_dict = models_dict
        self.feature_names = feature_names
        self.explainers = {}
        self.feature_importance_cache = {}
        
        self._load_feature_rankings()
        self._initialize_explainers()
        
    def _load_feature_rankings(self):
        try:
            with open('../../actual_features.json', 'r') as f:
                features = json.load(f)
                
            self.feature_rankings = {}
            for i, feature in enumerate(features):
                if 'rank' in feature:
                    try:
                        rank = int(feature.split('rank')[1])
                        self.feature_rankings[feature] = 1.0 / (rank + 1)
                    except:
                        self.feature_rankings[feature] = 0.5
                elif 'critical' in feature:
                    self.feature_rankings[feature] = 0.9
                elif 'high' in feature:
                    self.feature_rankings[feature] = 0.7
                else:
                    self.feature_rankings[feature] = 0.5
                    
        except Exception as e:
            logger.warning(f"Could not load feature rankings: {e}")
            self.feature_rankings = {}
    
    def _initialize_explainers(self):
        try:
            ml_models = ['lr_model', 'rf_model', 'xgb_model', 'catboost_model']
            
            for model_name in ml_models:
                if model_name in self.models_dict:
                    try:
                        model = self.models_dict[model_name]
                        
                        if 'xgb' in model_name or 'catboost' in model_name:
                            self.explainers[model_name] = shap.TreeExplainer(model)
                        else:
                            self.explainers[model_name] = shap.Explainer(model)
                            
                        logger.info(f"SHAP explainer initialized for {model_name}")
                        
                    except Exception as e:
                        logger.warning(f"Could not initialize SHAP explainer for {model_name}: {e}")
                        
            if 'meta_model' in self.models_dict:
                try:
                    self.explainers['meta_model'] = shap.Explainer(self.models_dict['meta_model'])
                    logger.info("SHAP explainer initialized for meta_model")
                except Exception as e:
                    logger.warning(f"Could not initialize SHAP explainer for meta_model: {e}")
                    
        except Exception as e:
            logger.error(f"Error initializing explainers: {e}")
    
    def explain_prediction(self, input_data: Dict, prediction_result: Dict) -> Dict[str, Any]:
        try:
            df_input = pd.DataFrame([input_data])
            
            if self.feature_names:
                missing_features = set(self.feature_names) - set(df_input.columns)
                if missing_features:
                    logger.warning(f"Missing features: {missing_features}")
                    for feature in missing_features:
                        df_input[feature] = 0.0
                
                df_input = df_input[self.feature_names]
            
            feature_explanations = self._get_feature_importance(df_input)
            risk_factors = self._identify_risk_factors(input_data, prediction_result)
            explanation_summary = self._generate_explanation_summary(
                prediction_result, risk_factors, feature_explanations
            )
            recommendations = self._get_recommendations(prediction_result, risk_factors)
            
            return {
                "prediction_summary": {
                    "status": prediction_result.get("status", "UNKNOWN"),
                    "probability": prediction_result.get("probability", 0.0),
                    "confidence": prediction_result.get("confidence", 0.0),
                    "risk_level": self._get_risk_level(prediction_result.get("probability", 0.0)),
                    "threshold_used": prediction_result.get("threshold_used", 0.5)
                },
                "feature_importance": feature_explanations,
                "risk_factors": risk_factors,
                "explanation": explanation_summary,
                "recommendations": recommendations,
                "model_insights": self._get_model_insights(prediction_result),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Explanation generation failed: {e}")
            return {
                "error": f"Explanation generation failed: {str(e)}",
                "basic_explanation": {
                    "status": prediction_result.get("status", "UNKNOWN"),
                    "probability": prediction_result.get("probability", 0.0),
                    "message": f"Transaction classified as {prediction_result.get('status', 'Unknown')} with {prediction_result.get('probability', 0):.1%} probability"
                }
            }
    
    def _get_feature_importance(self, df_input: pd.DataFrame) -> List[Dict]:
        try:
            shap_importance = self._get_shap_importance(df_input)
            if shap_importance:
                return shap_importance
                
        except Exception as e:
            logger.warning(f"SHAP explanation failed: {e}")
        
        return self._get_rule_based_importance(df_input)
    
    def _get_shap_importance(self, df_input: pd.DataFrame) -> Optional[List[Dict]]:
        try:
            explainer_priority = ['meta_model', 'xgb_model', 'rf_model', 'lr_model']
            
            for explainer_name in explainer_priority:
                if explainer_name in self.explainers:
                    try:
                        explainer = self.explainers[explainer_name]
                        shap_values = explainer.shap_values(df_input)
                        
                        if isinstance(shap_values, list):
                            shap_values = shap_values[1] if len(shap_values) > 1 else shap_values[0]
                        
                        if len(shap_values.shape) > 1:
                            shap_values = shap_values[0]
                        
                        feature_importance = []
                        for i, (feature, shap_value) in enumerate(zip(df_input.columns, shap_values)):
                            feature_value = float(df_input.iloc[0, i])
                            
                            feature_importance.append({
                                "feature": feature,
                                "value": feature_value,
                                "shap_value": float(shap_value),
                                "importance": abs(float(shap_value)),
                                "impact": self._categorize_impact(float(shap_value)),
                                "contribution": "Increases Risk" if shap_value > 0 else "Decreases Risk",
                                "explanation": self._get_feature_explanation(feature, feature_value, float(shap_value))
                            })
                        
                        feature_importance.sort(key=lambda x: x["importance"], reverse=True)
                        return feature_importance[:15]
                        
                    except Exception as e:
                        logger.warning(f"SHAP calculation failed for {explainer_name}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"SHAP importance calculation failed: {e}")
            
        return None
    
    def _get_rule_based_importance(self, df_input: pd.DataFrame) -> List[Dict]:
        feature_importance = []
        
        for feature in df_input.columns:
            value = float(df_input[feature].iloc[0])
            base_importance = self.feature_rankings.get(feature, 0.5)
            value_magnitude = abs(value)
            
            if "critical" in feature.lower():
                if value_magnitude > 2.0:
                    importance = base_importance * value_magnitude * 0.5
                    impact = "Very High"
                elif value_magnitude > 1.0:
                    importance = base_importance * value_magnitude * 0.3
                    impact = "High"
                else:
                    importance = base_importance * value_magnitude * 0.2
                    impact = "Medium"
            elif "high" in feature.lower():
                if value_magnitude > 1.5:
                    importance = base_importance * value_magnitude * 0.3
                    impact = "High"
                else:
                    importance = base_importance * value_magnitude * 0.2
                    impact = "Medium"
            else:
                importance = base_importance * value_magnitude * 0.1
                impact = "Low"
            
            contribution = "Increases Risk" if value > 0 else "Decreases Risk"
            
            feature_importance.append({
                "feature": feature,
                "value": value,
                "shap_value": None,
                "importance": importance,
                "impact": impact,
                "contribution": contribution,
                "explanation": self._get_feature_explanation(feature, value, None)
            })
        
        # Sort by importance
        feature_importance.sort(key=lambda x: x["importance"], reverse=True)
        
        return feature_importance[:15]
    
    def _categorize_impact(self, shap_value: float) -> str:
        abs_value = abs(shap_value)
        
        if abs_value > 0.3:
            return "Very High"
        elif abs_value > 0.15:
            return "High"
        elif abs_value > 0.05:
            return "Medium"
        else:
            return "Low"
    
    def _get_feature_explanation(self, feature_name: str, value: float, shap_value: Optional[float]) -> str:
        if "critical" in feature_name.lower():
            feature_type = "Critical Risk Indicator"
        elif "high" in feature_name.lower():
            feature_type = "High Risk Indicator"
        else:
            feature_type = "Risk Indicator"
        
        if shap_value is not None:
            if shap_value > 0.1:
                return f"{feature_type}: High suspicious activity detected (value: {value:.2f})"
            elif shap_value < -0.1:
                return f"{feature_type}: Normal behavior pattern (value: {value:.2f})"
            else:
                return f"{feature_type}: Neutral indicator (value: {value:.2f})"
        else:
            if abs(value) > 2.0:
                return f"{feature_type}: Extreme value detected (value: {value:.2f})"
            elif abs(value) > 1.0:
                return f"{feature_type}: Elevated activity (value: {value:.2f})"
            else:
                return f"{feature_type}: Normal range (value: {value:.2f})"
    
    def _identify_risk_factors(self, input_data: Dict, prediction_result: Dict) -> List[Dict]:
        risk_factors = []
        
        for feature, value in input_data.items():
            if "critical" in feature and abs(value) > 2.0:
                risk_factors.append({
                    "factor": "Critical Pattern Anomaly",
                    "feature": feature,
                    "value": value,
                    "threshold": 2.0,
                    "severity": "High",
                    "description": f"Critical feature {feature} shows highly unusual pattern"
                })
        
        high_risk_count = sum(1 for feature, value in input_data.items() 
                             if "high" in feature and abs(value) > 1.5)
        
        if high_risk_count > 3:
            risk_factors.append({
                "factor": "Multiple High-Risk Indicators",
                "feature": "multiple_features",
                "value": high_risk_count,
                "threshold": 3,
                "severity": "Medium",
                "description": f"{high_risk_count} high-risk features exceed normal thresholds"
            })
        
        total_risk_score = sum(abs(value) for feature, value in input_data.items() 
                              if "critical" in feature or "high" in feature)
        
        if total_risk_score > 10.0:
            risk_factors.append({
                "factor": "Elevated Overall Risk Profile",
                "feature": "risk_aggregate",
                "value": total_risk_score,
                "threshold": 10.0,
                "severity": "Medium",
                "description": "Combined risk indicators suggest suspicious activity"
            })
        
        return risk_factors
    
    def _generate_explanation_summary(self, prediction_result: Dict, risk_factors: List, 
                                    feature_explanations: List) -> str:
        status = prediction_result.get("status", "UNKNOWN")
        probability = prediction_result.get("probability", 0.0)
        
        if status == "FRAUD":
            base_explanation = f"This transaction was flagged as FRAUDULENT with {probability:.1%} confidence. "
            
            # Add risk factor details
            if risk_factors:
                explanation = base_explanation + "Key concerns identified: "
                concerns = [rf["factor"] for rf in risk_factors[:3]]
                explanation += ", ".join(concerns) + ". "
            else:
                explanation = base_explanation + "Multiple suspicious patterns detected by the AI model. "
            
            if feature_explanations:
                top_features = [f["feature"] for f in feature_explanations[:3] if f.get("shap_value", 0) > 0]
                if top_features:
                    explanation += f"Primary risk indicators: {', '.join(top_features)}."
                    
        elif status == "SAFE":
            explanation = f"This transaction appears LEGITIMATE with {(1-probability):.1%} confidence. "
            
            if risk_factors:
                explanation += f"Although {len(risk_factors)} minor risk factors were detected, "
                explanation += "they are within acceptable limits for normal transactions. "
            else:
                explanation += "No significant risk patterns were identified. "
                
            if feature_explanations:
                protective_features = [f["feature"] for f in feature_explanations[:3] 
                                     if f.get("shap_value", 0) < -0.05]
                if protective_features:
                    explanation += f"Strong legitimacy indicators: {', '.join(protective_features)}."
        else:
            explanation = f"Transaction classification: {status} with {probability:.1%} fraud probability. "
            explanation += "Please review manually for final decision."
        
        return explanation
    
    def _get_risk_level(self, probability: float) -> str:
        if probability >= 0.8:
            return "CRITICAL"
        elif probability >= 0.6:
            return "HIGH"
        elif probability >= 0.4:
            return "MEDIUM"
        elif probability >= 0.2:
            return "LOW"
        else:
            return "VERY LOW"
    
    def _get_recommendations(self, prediction_result: Dict, risk_factors: List) -> List[str]:
        recommendations = []
        
        status = prediction_result.get("status", "UNKNOWN")
        probability = prediction_result.get("probability", 0.0)
        
        if status == "FRAUD" or probability > 0.7:
            recommendations.append("BLOCK transaction immediately")
            recommendations.append("Flag account for comprehensive security review")
            recommendations.append("Initiate customer verification process")
            
            if any("Critical Pattern Anomaly" in rf.get("factor", "") for rf in risk_factors):
                recommendations.append("Escalate to fraud investigation team")
            
            if any("Multiple" in rf.get("factor", "") for rf in risk_factors):
                recommendations.append("Review recent transaction history for patterns")
                
        elif status == "SAFE" or probability < 0.3:
            recommendations.append("APPROVE transaction")
            
            if risk_factors:
                recommendations.append("Monitor account for 24 hours")
                recommendations.append("Update customer risk profile")
            else:
                recommendations.append("Process normally")
                
        else:
            recommendations.append("REVIEW transaction manually")
            recommendations.append("Consider additional authentication")
            recommendations.append("Monitor for related suspicious activity")
        
        return recommendations
    
    def _get_model_insights(self, prediction_result: Dict) -> Dict[str, Any]:
        return {
            "models_used": prediction_result.get("model_stats", {}),
            "inference_time": prediction_result.get("inference_time_ms", 0),
            "confidence_level": prediction_result.get("confidence", 0),
            "threshold_applied": prediction_result.get("threshold_used", 0.5),
            "ensemble_method": "Hybrid ML+DL with Meta-Learning",
            "explainability_method": "SHAP Values + Rule-based Analysis"
        }


fraud_explainer: Optional[FraudExplainer] = None

def initialize_explainer(models_dict: Dict, feature_names: List[str]) -> bool:
    global fraud_explainer
    
    try:
        fraud_explainer = FraudExplainer(models_dict, feature_names)
        logger.info("Fraud explainer initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize fraud explainer: {e}")
        return False

def get_explanation(input_data: Dict, prediction_result: Dict) -> Dict[str, Any]:
    if fraud_explainer is None:
        return {
            "error": "Explainer not initialized",
            "basic_explanation": {
                "status": prediction_result.get("status", "UNKNOWN"),
                "probability": prediction_result.get("probability", 0.0),
                "message": "Detailed explanations are currently unavailable"
            }
        }
    
    return fraud_explainer.explain_prediction(input_data, prediction_result)

def is_explainer_ready() -> bool:
    return fraud_explainer is not None