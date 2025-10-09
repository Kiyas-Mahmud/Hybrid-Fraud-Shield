"""
Preprocessing Module for Hybrid Fraud Detection API

This module handles data cleaning, feature engineering, and scaling
to match the training pipeline preprocessing steps.

Author: Fraud Detection Team
Date: October 2025
"""

import logging
import warnings
from typing import Dict, List, Any, Tuple, Optional

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# Suppress warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPreprocessor:
    """
    Handles data preprocessing for fraud detection API
    Matches the preprocessing pipeline used during training
    """
    
    def __init__(self, scalers: Dict[str, Any]):
        """
        Initialize the preprocessor with trained scalers
        
        Args:
            scalers (Dict): Dictionary containing trained scalers
        """
        self.scalers = scalers
        self.expected_features = 63  # Based on training data
        
        # Feature names (this should match your training features)
        # Note: In production, this should be loaded from a configuration file
        self.feature_names = [
            f"feature_{i}" for i in range(self.expected_features)
        ]
        
        logger.info(f"Initialized DataPreprocessor with {len(self.scalers)} scalers")
        logger.info(f"Expected feature count: {self.expected_features}")
    
    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate input data format and completeness
        
        Args:
            data (Dict): Input transaction data
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            # Check if data is a dictionary
            if not isinstance(data, dict):
                return False, "Input must be a dictionary"
            
            # Check for required fields (basic validation)
            if len(data) == 0:
                return False, "Input data is empty"
            
            # Convert to DataFrame for processing
            df = pd.DataFrame([data])
            
            # Check feature count after conversion
            if df.shape[1] != self.expected_features:
                return False, f"Expected {self.expected_features} features, got {df.shape[1]}"
            
            # Check for missing values
            if df.isnull().any().any():
                missing_cols = df.columns[df.isnull().any()].tolist()
                return False, f"Missing values in columns: {missing_cols}"
            
            # Check for infinite values
            if np.isinf(df.select_dtypes(include=[np.number])).any().any():
                return False, "Input contains infinite values"
            
            return True, "Valid input"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def preprocess_for_ml(self, data: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Preprocess data for ML models
        
        Args:
            data (Dict): Input transaction data
            
        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: (scaled_data, unscaled_data)
        """
        try:
            # Convert to DataFrame
            df = pd.DataFrame([data])
            
            # Ensure correct column order (if needed)
            if len(df.columns) == self.expected_features:
                # If columns are just numeric, ensure proper naming
                if all(isinstance(col, (int, float)) for col in df.columns):
                    df.columns = [f"feature_{i}" for i in range(len(df.columns))]
            
            # Handle any data type conversions
            df = df.astype(float)
            
            # Create unscaled version (for tree-based models)
            unscaled_data = df.copy()
            
            # Create scaled version (for Logistic Regression)
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
        """
        Preprocess data for Deep Learning models
        
        Args:
            data (Dict): Input transaction data
            
        Returns:
            np.ndarray: Scaled data for DL models
        """
        try:
            # Convert to DataFrame
            df = pd.DataFrame([data])
            
            # Ensure correct column order and naming
            if len(df.columns) == self.expected_features:
                if all(isinstance(col, (int, float)) for col in df.columns):
                    df.columns = [f"feature_{i}" for i in range(len(df.columns))]
            
            # Handle data type conversions
            df = df.astype(float)
            
            # Scale data using StandardScaler (DL models prefer standardized input)
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
        """
        Create a sample input for testing purposes
        
        Args:  
            fraud_type (str): "normal" or "fraud" - type of sample to create
            
        Returns:
            Dict[str, float]: Sample transaction data
        """
        np.random.seed(42)  # For reproducible samples
        
        if fraud_type == "fraud":
            # Create fraud-like sample (higher risk features)
            sample = {
                f"feature_{i}": np.random.uniform(0.7, 1.0) if i < 10 else np.random.uniform(0.3, 0.8)
                for i in range(self.expected_features)
            }
            # Add some specific fraud indicators
            sample['feature_0'] = np.random.uniform(0.8, 1.0)  # High risk indicator
            sample['feature_1'] = np.random.uniform(0.9, 1.0)  # Very high risk
            
        else:  # normal transaction
            # Create normal-like sample (lower risk features)  
            sample = {
                f"feature_{i}": np.random.uniform(0.0, 0.3) if i < 10 else np.random.uniform(0.1, 0.5)
                for i in range(self.expected_features)
            }
            # Add some specific normal indicators
            sample['feature_0'] = np.random.uniform(0.0, 0.2)  # Low risk indicator
            sample['feature_1'] = np.random.uniform(0.0, 0.1)  # Very low risk
        
        return sample
    
    def get_feature_info(self) -> Dict[str, Any]:
        """
        Get information about expected features
        
        Returns:
            Dict: Feature information
        """
        return {
            "expected_feature_count": self.expected_features,
            "feature_names": self.feature_names,
            "available_scalers": list(self.scalers.keys()),
            "data_types": "All features should be numeric (float/int)"
        }

def create_preprocessor(scalers: Dict[str, Any]) -> DataPreprocessor:
    """
    Factory function to create a DataPreprocessor instance
    
    Args:
        scalers (Dict): Dictionary of trained scalers
        
    Returns:
        DataPreprocessor: Configured preprocessor instance
    """
    return DataPreprocessor(scalers)

def validate_and_preprocess(
    data: Dict[str, Any], 
    preprocessor: DataPreprocessor
) -> Tuple[bool, Dict[str, Any]]:
    """
    Validate input and preprocess data for both ML and DL models
    
    Args:
        data (Dict): Input transaction data
        preprocessor (DataPreprocessor): Preprocessor instance
        
    Returns:
        Tuple[bool, Dict]: (success, result_dict)
    """
    try:
        # Validate input
        is_valid, message = preprocessor.validate_input(data)
        if not is_valid:
            return False, {"error": message}
        
        # Preprocess for ML models
        ml_scaled, ml_unscaled = preprocessor.preprocess_for_ml(data)
        
        # Preprocess for DL models  
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
    # Test preprocessing with dummy scalers
    from sklearn.preprocessing import StandardScaler
    
    # Create dummy scaler for testing
    dummy_scaler = StandardScaler()
    dummy_data = np.random.randn(100, 63)
    dummy_scaler.fit(dummy_data)
    
    scalers = {"standard": dummy_scaler}
    preprocessor = create_preprocessor(scalers)
    
    # Test with sample data
    sample_normal = preprocessor.create_sample_input("normal")
    sample_fraud = preprocessor.create_sample_input("fraud")
    
    print("Sample Normal Transaction:")
    print(f"Features: {len(sample_normal)}")
    print(f"First 5 features: {dict(list(sample_normal.items())[:5])}")
    
    print("\nSample Fraud Transaction:")
    print(f"Features: {len(sample_fraud)}")
    print(f"First 5 features: {dict(list(sample_fraud.items())[:5])}")
    
    # Test preprocessing
    success, result = validate_and_preprocess(sample_normal, preprocessor)
    print(f"\nPreprocessing test - Success: {success}")
    if success:
        print(f"ML scaled shape: {result['ml_scaled'].shape}")
        print(f"ML unscaled shape: {result['ml_unscaled'].shape}")
        print(f"DL data shape: {result['dl_data'].shape}")