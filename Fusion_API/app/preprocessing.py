"""
Preprocessing Module for Hybrid Fraud Detection API
Handles data cleaning, feature engineering, and scaling.
"""

import logging
import warnings
from typing import Dict, List, Any, Tuple, Optional

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler

warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPreprocessor:
    """Handles data preprocessing for fraud detection API"""
    
    def __init__(self, scalers: Dict[str, Any]):
        self.scalers = scalers
        self.expected_features = 63
        self.feature_names = [
            f"feature_{i}" for i in range(self.expected_features)
        ]
        
        logger.info(f"Initialized DataPreprocessor with {len(self.scalers)} scalers")
        logger.info(f"Expected feature count: {self.expected_features}")
    
    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        try:
            if not isinstance(data, dict):
                return False, "Input must be a dictionary"
            
            if len(data) == 0:
                return False, "Input data is empty"
            
            df = pd.DataFrame([data])
            
            if df.shape[1] != self.expected_features:
                return False, f"Expected {self.expected_features} features, got {df.shape[1]}"
            
            if df.isnull().any().any():
                missing_cols = df.columns[df.isnull().any()].tolist()
                return False, f"Missing values in columns: {missing_cols}"
            
            if np.isinf(df.select_dtypes(include=[np.number])).any().any():
                return False, "Input contains infinite values"
            
            return True, "Valid input"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def preprocess_for_ml(self, data: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        try:
            df = pd.DataFrame([data])
            
            if len(df.columns) == self.expected_features:
                if all(isinstance(col, (int, float)) for col in df.columns):
                    df.columns = [f"feature_{i}" for i in range(len(df.columns))]
            
            df = df.astype(float)
            unscaled_data = df.copy()
            
            if 'standard' in self.scalers:
                scaled_data = pd.DataFrame(
                    self.scalers['standard'].transform(df),
                    columns=df.columns,
                    index=df.index
                )
            else:
                logger.warning("StandardScaler not available, using unscaled data")
                scaled_data = df.copy()
            
            return scaled_data, unscaled_data
            
        except Exception as e:
            logger.error(f"Error in ML preprocessing: {str(e)}")
            raise
    
    def preprocess_for_dl(self, data: Dict[str, Any]) -> np.ndarray:
        try:
            df = pd.DataFrame([data])
            
            if len(df.columns) == self.expected_features:
                if all(isinstance(col, (int, float)) for col in df.columns):
                    df.columns = [f"feature_{i}" for i in range(len(df.columns))]
            
            df = df.astype(float)
            
            if 'standard' in self.scalers:
                scaled_data = self.scalers['standard'].transform(df)
            else:
                logger.warning("StandardScaler not available, using raw data")
                scaled_data = df.values
            
            return scaled_data
            
        except Exception as e:
            logger.error(f"Error in DL preprocessing: {str(e)}")
            raise
    
    def create_sample_input(self, fraud_type: str = "normal") -> Dict[str, float]:
        np.random.seed(42)
        
        if fraud_type == "fraud":
            sample = {
                f"feature_{i}": np.random.uniform(0.7, 1.0) if i < 10 else np.random.uniform(0.3, 0.8)
                for i in range(self.expected_features)
            }
            sample['feature_0'] = np.random.uniform(0.8, 1.0)
            sample['feature_1'] = np.random.uniform(0.9, 1.0)
            
        else:
            sample = {
                f"feature_{i}": np.random.uniform(0.0, 0.3) if i < 10 else np.random.uniform(0.1, 0.5)
                for i in range(self.expected_features)
            }
            sample['feature_0'] = np.random.uniform(0.0, 0.2)
            sample['feature_1'] = np.random.uniform(0.0, 0.1)
        
        return sample
    
    def get_feature_info(self) -> Dict[str, Any]:
        return {
            "expected_feature_count": self.expected_features,
            "feature_names": self.feature_names,
            "available_scalers": list(self.scalers.keys()),
            "data_types": "All features should be numeric (float/int)"
        }

def create_preprocessor(scalers: Dict[str, Any]) -> DataPreprocessor:
    return DataPreprocessor(scalers)

def validate_and_preprocess(
    data: Dict[str, Any], 
    preprocessor: DataPreprocessor
) -> Tuple[bool, Dict[str, Any]]:
    try:
        is_valid, message = preprocessor.validate_input(data)
        if not is_valid:
            return False, {"error": message}
        
        ml_scaled, ml_unscaled = preprocessor.preprocess_for_ml(data)
        dl_data = preprocessor.preprocess_for_dl(data)
        
        return True, {
            "ml_scaled": ml_scaled,
            "ml_unscaled": ml_unscaled, 
            "dl_data": dl_data,
            "original_data": data
        }
        
    except Exception as e:
        logger.error(f"Preprocessing error: {str(e)}")
        return False, {"error": f"Preprocessing failed: {str(e)}"}

if __name__ == "__main__":
    from sklearn.preprocessing import StandardScaler
    
    dummy_scaler = StandardScaler()
    dummy_data = np.random.randn(100, 63)
    dummy_scaler.fit(dummy_data)
    
    scalers = {"standard": dummy_scaler}
    preprocessor = create_preprocessor(scalers)
    
    sample_normal = preprocessor.create_sample_input("normal")
    sample_fraud = preprocessor.create_sample_input("fraud")
    
    print("Sample Normal Transaction:")
    print(f"Features: {len(sample_normal)}")
    print(f"First 5 features: {dict(list(sample_normal.items())[:5])}")
    
    print("\nSample Fraud Transaction:")
    print(f"Features: {len(sample_fraud)}")
    print(f"First 5 features: {dict(list(sample_fraud.items())[:5])}")
    
    success, result = validate_and_preprocess(sample_normal, preprocessor)
    print(f"\nPreprocessing test - Success: {success}")
    if success:
        print(f"ML scaled shape: {result['ml_scaled'].shape}")
        print(f"ML unscaled shape: {result['ml_unscaled'].shape}")
        print(f"DL data shape: {result['dl_data'].shape}")