"""
Simplified explainability service for admin panel
Provides model predictions breakdown and basic feature analysis
"""

from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class AdminExplainabilityService:
    """Provides explainability for admin panel"""
    
    @staticmethod
    def get_model_breakdown(model_predictions: Dict) -> List[Dict]:
        """Extract individual model predictions with feature importance"""
        breakdown = []
        
        if not model_predictions:
            return breakdown
        
        # Get model contributions if available
        contributions = model_predictions.get('model_contributions', {})
        
        # ML Models - check both with and without 'ml_' prefix
        ml_models = {
            'catboost': 'CatBoost',
            'lightgbm': 'LightGBM',
            'logistic_regression': 'Logistic Regression',
            'random_forest': 'Random Forest',
            'xgboost': 'XGBoost'
        }
        
        for key, name in ml_models.items():
            # Check both 'key' and 'ml_key' formats
            pred_key = key if key in model_predictions else f'ml_{key}'
            if pred_key in model_predictions:
                pred = model_predictions[pred_key]
                pred_value = float(pred)
                
                # Get contribution for this model
                contrib_key = key if key in contributions else f'ml_{key}'
                contribution = contributions.get(contrib_key, 0.0)
                
                breakdown.append({
                    'model_name': name,
                    'type': 'Machine Learning',
                    'prediction': AdminExplainabilityService._classify_prediction(pred_value),
                    'confidence': pred_value,
                    'contribution': float(contribution),
                    'model_key': pred_key
                })
        
        # DL Models - check both with and without 'dl_' prefix
        dl_models = {
            'autoencoder': 'Autoencoder',
            'bilstm': 'BiLSTM',
            'cnn': 'CNN',
            'fnn': 'FNN',
            'hybrid_dl': 'Hybrid DL',
            'lstm': 'LSTM'
        }
        
        for key, name in dl_models.items():
            # Check both 'key' and 'dl_key' formats
            pred_key = key if key in model_predictions else f'dl_{key}'
            if pred_key in model_predictions:
                pred = model_predictions[pred_key]
                pred_value = float(pred)
                
                # Get contribution for this model
                contrib_key = key if key in contributions else f'dl_{key}'
                contribution = contributions.get(contrib_key, 0.0)
                
                breakdown.append({
                    'model_name': name,
                    'type': 'Deep Learning',
                    'prediction': AdminExplainabilityService._classify_prediction(pred_value),
                    'confidence': pred_value,
                    'contribution': float(contribution),
                    'model_key': pred_key
                })
        
        # Meta model - check multiple possible keys
        meta_keys = ['meta_model', 'weighted_ensemble', 'ensemble']
        for meta_key in meta_keys:
            if meta_key in model_predictions:
                pred = model_predictions[meta_key]
                pred_value = float(pred)
                breakdown.append({
                    'model_name': 'Meta Learner (Final)',
                    'type': 'Ensemble',
                    'prediction': AdminExplainabilityService._classify_prediction(pred_value),
                    'confidence': pred_value,
                    'contribution': 1.0,  # Ensemble uses all
                    'model_key': meta_key
                })
                break  # Only add once
        
        return breakdown
    
    @staticmethod
    def _classify_prediction(score: float) -> str:
        """Convert risk score to classification label"""
        if score >= 0.7:
            return 'FRAUD'
        elif score >= 0.4:
            return 'SUSPICIOUS'
        else:
            return 'SAFE'
    
    @staticmethod
    def get_feature_analysis(features: Dict, risk_score: float) -> List[Dict]:
        """Analyze key features contributing to risk"""
        analysis = []
        
        # Amount analysis
        if 'amount' in features:
            amount = features['amount']
            impact_level = 'NEGATIVE' if amount > 1000 else 'NEUTRAL' if amount > 150 else 'POSITIVE'
            importance = min(amount / 5000, 1.0) if amount > 150 else 0.3
            analysis.append({
                'feature': 'Transaction Amount',
                'value': f"${amount:.2f}",
                'impact': impact_level,
                'importance': importance
            })
        
        # Time analysis
        if 'transaction_hour' in features:
            hour = features.get('transaction_hour', 12)
            is_unusual = hour < 6 or hour > 22
            analysis.append({
                'feature': 'Transaction Time',
                'value': f'{int(hour)}:00',
                'impact': 'NEGATIVE' if is_unusual else 'POSITIVE',
                'importance': 0.8 if is_unusual else 0.2
            })
        
        # Location analysis
        if 'location' in features and features['location']:
            location = features['location']
            analysis.append({
                'feature': 'Location',
                'value': location,
                'impact': 'NEUTRAL',
                'importance': 0.5
            })
        
        # Device analysis
        if 'device_info' in features and features['device_info']:
            device = features['device_info']
            analysis.append({
                'feature': 'Device',
                'value': device,
                'impact': 'POSITIVE',
                'importance': 0.3
            })
        
        # Merchant analysis
        if 'merchant_name' in features:
            merchant = features['merchant_name']
            analysis.append({
                'feature': 'Merchant',
                'value': merchant,
                'impact': 'NEUTRAL',
                'importance': 0.6
            })
        
        # Risk score based analysis
        if risk_score > 0.7:
            analysis.append({
                'feature': 'Overall Risk Pattern',
                'value': 'High Risk',
                'impact': 'NEGATIVE',
                'importance': 0.9
            })
        
        return analysis
    
    @staticmethod
    def get_model_specific_features(model_name: str, model_confidence: float, features: Dict, model_type: str) -> List[Dict]:
        """Generate model-specific feature analysis based on model type and confidence"""
        analysis = []
        
        # Different models focus on different features
        if 'Machine Learning' in model_type:
            # ML models focus on statistical patterns
            if 'CatBoost' in model_name or 'XGBoost' in model_name:
                # Tree-based models - focus on categorical and numerical interactions
                if 'amount' in features:
                    amount = features['amount']
                    analysis.append({
                        'feature': 'Transaction Amount Pattern',
                        'value': f"${amount:.2f}",
                        'impact': 'POSITIVE' if model_confidence > 0.5 else 'NEGATIVE',
                        'importance': abs(model_confidence - 0.5) * 2
                    })
                
                if 'merchant_name' in features:
                    analysis.append({
                        'feature': 'Merchant Category Risk',
                        'value': features['merchant_name'],
                        'impact': 'POSITIVE' if model_confidence > 0.6 else 'NEUTRAL',
                        'importance': 0.7 if model_confidence > 0.6 else 0.4
                    })
                    
                if 'location' in features:
                    analysis.append({
                        'feature': 'Geographic Pattern',
                        'value': features.get('location', 'Unknown'),
                        'impact': 'NEUTRAL',
                        'importance': 0.5
                    })
                    
            elif 'LightGBM' in model_name:
                # LightGBM - efficient with large features
                if 'amount' in features:
                    analysis.append({
                        'feature': 'Amount Histogram Bin',
                        'value': f"${features['amount']:.2f}",
                        'impact': 'POSITIVE' if model_confidence > 0.5 else 'NEGATIVE',
                        'importance': min(model_confidence * 1.2, 1.0)
                    })
                    
                if 'transaction_hour' in features:
                    hour = features.get('transaction_hour', 12)
                    analysis.append({
                        'feature': 'Time-based Pattern',
                        'value': f'{int(hour)}:00',
                        'impact': 'POSITIVE' if hour < 6 or hour > 22 else 'NEGATIVE',
                        'importance': 0.6
                    })
                    
            elif 'Random Forest' in model_name:
                # Random Forest - ensemble of decision trees
                if 'amount' in features:
                    analysis.append({
                        'feature': 'Amount Decision Path',
                        'value': f"${features['amount']:.2f}",
                        'impact': 'POSITIVE' if model_confidence > 0.5 else 'NEGATIVE',
                        'importance': 0.8
                    })
                    
                if 'device_info' in features:
                    analysis.append({
                        'feature': 'Device Trust Score',
                        'value': features.get('device_info', 'Unknown'),
                        'impact': 'NEGATIVE',
                        'importance': 0.6
                    })
                    
            elif 'Logistic' in model_name:
                # Logistic Regression - linear patterns
                if 'amount' in features:
                    analysis.append({
                        'feature': 'Amount Linear Weight',
                        'value': f"${features['amount']:.2f}",
                        'impact': 'POSITIVE' if model_confidence > 0.5 else 'NEGATIVE',
                        'importance': model_confidence
                    })
                    
                analysis.append({
                    'feature': 'Linear Risk Score',
                    'value': f'{model_confidence * 100:.1f}%',
                    'impact': 'POSITIVE' if model_confidence > 0.5 else 'NEGATIVE',
                    'importance': 0.9
                })
                
        elif 'Deep Learning' in model_type:
            # DL models detect complex patterns
            if 'CNN' in model_name:
                # CNN - spatial/sequential patterns
                analysis.append({
                    'feature': 'Sequential Pattern Detection',
                    'value': 'Anomaly Detected' if model_confidence > 0.7 else 'Normal Pattern',
                    'impact': 'POSITIVE' if model_confidence > 0.7 else 'NEGATIVE',
                    'importance': 0.95
                })
                
                if 'amount' in features:
                    analysis.append({
                        'feature': 'Transaction Flow Pattern',
                        'value': f"${features['amount']:.2f}",
                        'impact': 'POSITIVE' if model_confidence > 0.5 else 'NEGATIVE',
                        'importance': 0.8
                    })
                    
            elif 'LSTM' in model_name or 'BiLSTM' in model_name:
                # LSTM/BiLSTM - temporal patterns
                analysis.append({
                    'feature': 'Temporal Sequence Anomaly',
                    'value': 'High Risk Pattern' if model_confidence > 0.6 else 'Normal Sequence',
                    'impact': 'POSITIVE' if model_confidence > 0.6 else 'NEGATIVE',
                    'importance': 0.9
                })
                
                if 'transaction_hour' in features:
                    analysis.append({
                        'feature': 'Time Series Pattern',
                        'value': f'{int(features.get("transaction_hour", 12))}:00',
                        'impact': 'NEUTRAL',
                        'importance': 0.7
                    })
                    
            elif 'Autoencoder' in model_name:
                # Autoencoder - reconstruction error
                analysis.append({
                    'feature': 'Reconstruction Error',
                    'value': f'{model_confidence * 100:.1f}% anomaly',
                    'impact': 'POSITIVE' if model_confidence > 0.7 else 'NEGATIVE',
                    'importance': 0.95
                })
                
                analysis.append({
                    'feature': 'Pattern Deviation Score',
                    'value': 'High' if model_confidence > 0.7 else 'Low',
                    'impact': 'POSITIVE' if model_confidence > 0.7 else 'NEGATIVE',
                    'importance': 0.85
                })
                
            elif 'FNN' in model_name:
                # Feedforward Neural Network
                if 'amount' in features:
                    analysis.append({
                        'feature': 'Neural Network Weight',
                        'value': f"${features['amount']:.2f}",
                        'impact': 'POSITIVE' if model_confidence > 0.5 else 'NEGATIVE',
                        'importance': 0.75
                    })
                    
                analysis.append({
                    'feature': 'Hidden Layer Activation',
                    'value': f'{model_confidence * 100:.1f}% confidence',
                    'impact': 'POSITIVE' if model_confidence > 0.5 else 'NEGATIVE',
                    'importance': 0.8
                })
                
            elif 'Hybrid' in model_name:
                # Hybrid model - combined features
                analysis.append({
                    'feature': 'Multi-Model Feature Fusion',
                    'value': 'Complex Pattern Detected' if model_confidence > 0.5 else 'Normal',
                    'impact': 'POSITIVE' if model_confidence > 0.5 else 'NEGATIVE',
                    'importance': 0.9
                })
                
                if 'merchant_name' in features:
                    analysis.append({
                        'feature': 'Merchant Embedding Vector',
                        'value': features['merchant_name'],
                        'impact': 'NEUTRAL',
                        'importance': 0.6
                    })
                    
        else:
            # Ensemble model
            analysis.append({
                'feature': 'Weighted Model Consensus',
                'value': f'{model_confidence * 100:.1f}% agreement',
                'impact': 'POSITIVE' if model_confidence > 0.5 else 'NEGATIVE',
                'importance': 1.0
            })
            
            analysis.append({
                'feature': 'Meta-Learning Decision',
                'value': 'High Risk' if model_confidence > 0.5 else 'Low Risk',
                'impact': 'POSITIVE' if model_confidence > 0.5 else 'NEGATIVE',
                'importance': 0.95
            })
        
        # Add common features for all models
        if len(analysis) < 5:
            if 'device_info' in features and 'device_info' not in str(analysis):
                analysis.append({
                    'feature': 'Device Profile',
                    'value': features.get('device_info', 'Unknown'),
                    'impact': 'NEUTRAL',
                    'importance': 0.4
                })
            
            if 'location' in features and 'location' not in str(analysis):
                analysis.append({
                    'feature': 'Location Data',
                    'value': features.get('location', 'Unknown'),
                    'impact': 'NEUTRAL',
                    'importance': 0.5
                })
        
        # Sort by importance and return top 5
        analysis.sort(key=lambda x: x['importance'], reverse=True)
        return analysis[:5]
    
    @staticmethod
    def get_risk_summary(classification: str, risk_score: float, amount: float) -> Dict:
        """Generate risk summary for admin"""
        return {
            'classification': classification,
            'risk_score': risk_score,
            'risk_percentage': f"{risk_score * 100:.1f}%",
            'risk_level': 'Critical' if risk_score >= 0.7 else 'High' if risk_score >= 0.5 else 'Medium' if risk_score >= 0.3 else 'Low',
            'amount': amount,
            'recommendation': AdminExplainabilityService._get_recommendation(classification, risk_score),
            'risk_factors': AdminExplainabilityService._generate_risk_factors(classification, risk_score, amount)
        }
    
    @staticmethod
    def _get_recommendation(classification: str, risk_score: float) -> str:
        """Get admin recommendation"""
        if classification == 'FRAUD':
            return '🚨 High fraud probability - Transaction automatically blocked'
        elif classification == 'SUSPICIOUS':
            if risk_score >= 0.6:
                return '⚠️ High suspicion - Recommend user verification'
            else:
                return '⚠️ Moderate suspicion - User confirmation required'
        else:
            return '✅ Low risk - Transaction approved'
    
    @staticmethod
    def _generate_risk_factors(classification: str, risk_score: float, amount: float) -> List[Dict]:
        """Generate risk factors based on transaction analysis"""
        risk_factors = []
        
        # High risk score factor
        if risk_score >= 0.7:
            risk_factors.append({
                'factor': 'Critical Risk Score',
                'severity': 'HIGH',
                'description': f'Transaction has a very high risk score of {risk_score * 100:.1f}%, indicating strong fraud signals'
            })
        elif risk_score >= 0.5:
            risk_factors.append({
                'factor': 'Elevated Risk Score',
                'severity': 'MEDIUM',
                'description': f'Transaction has an elevated risk score of {risk_score * 100:.1f}%, requiring attention'
            })
        elif risk_score >= 0.3:
            risk_factors.append({
                'factor': 'Moderate Risk Score',
                'severity': 'LOW',
                'description': f'Transaction has a moderate risk score of {risk_score * 100:.1f}%'
            })
        
        # High amount factor
        if amount > 5000:
            risk_factors.append({
                'factor': 'Unusually High Transaction Amount',
                'severity': 'HIGH',
                'description': f'Transaction amount of ${amount:.2f} is significantly higher than average, which may indicate fraud'
            })
        elif amount > 1000:
            risk_factors.append({
                'factor': 'High Transaction Amount',
                'severity': 'MEDIUM',
                'description': f'Transaction amount of ${amount:.2f} is above normal range'
            })
        
        # Classification-based factors
        if classification == 'FRAUD':
            risk_factors.append({
                'factor': 'Fraudulent Classification',
                'severity': 'HIGH',
                'description': 'Multiple AI models have classified this transaction as fraudulent with high confidence'
            })
        elif classification == 'SUSPICIOUS':
            risk_factors.append({
                'factor': 'Suspicious Pattern Detected',
                'severity': 'MEDIUM',
                'description': 'AI models detected unusual patterns that warrant further investigation'
            })
        
        # If no risk factors, add a positive note
        if not risk_factors:
            risk_factors.append({
                'factor': 'Normal Transaction Pattern',
                'severity': 'LOW',
                'description': 'Transaction shows normal patterns with no significant risk indicators'
            })
        
        return risk_factors
