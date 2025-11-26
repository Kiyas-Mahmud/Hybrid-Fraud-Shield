"""
Meta-Learner Fraud Detection Deployment Script
===============================================
This script provides a production-ready interface for fraud detection using
the trained meta-learner ensemble system.

Author: Hybrid Fraud Shield Team
Date: November 7, 2025
"""

import numpy as np
import pandas as pd
import joblib
import json
import os
from tensorflow import keras

class MetaLearnerPredictor:
    """
    Production deployment class for meta-learner fraud detection.
    """

    def __init__(self, model_dir='saved_models', ml_dir='../ml/models', dl_dir='../dl/saved_models'):
        """
        Initialize the meta-learner predictor.

        Args:
            model_dir: Directory containing meta-learner and config
            ml_dir: Directory containing ML models
            dl_dir: Directory containing DL models
        """
        self.model_dir = model_dir
        self.ml_dir = ml_dir
        self.dl_dir = dl_dir

        # Load configuration
        self.config = self._load_config()
        self.optimal_threshold = self.config['optimal_threshold']

        # Load models
        self.scaler = self._load_scaler()
        self.meta_learner = self._load_meta_learner()
        self.ml_models = self._load_ml_models()
        self.dl_models = self._load_dl_models()

        print("Meta-Learner Predictor initialized successfully!")
        print(f"Optimal Threshold: {self.optimal_threshold:.4f}")
        print(f"Base Models: {self.config['base_models']['total_models']}")

    def _load_config(self):
        """Load configuration file."""
        config_path = os.path.join(self.model_dir, 'config.json')
        with open(config_path, 'r') as f:
            return json.load(f)

    def _load_scaler(self):
        """Load StandardScaler."""
        scaler_path = os.path.join(self.model_dir, 'scaler.pkl')
        return joblib.load(scaler_path)

    def _load_meta_learner(self):
        """Load trained meta-learner."""
        meta_path = os.path.join(self.model_dir, 'meta_learner.pkl')
        return joblib.load(meta_path)

    def _load_ml_models(self):
        """Load all ML models."""
        ml_model_files = {
            'Logistic Regression': 'logistic_regression_tuned_72features.pkl',
            'Random Forest': 'random_forest_tuned_72features.pkl',
            'XGBoost': 'xgboost_tuned_72features.pkl',
            'CatBoost': 'catboost_tuned_72features.pkl',
            'LightGBM': 'lightgbm_tuned_72features.pkl'
        }

        models = {}
        for name, filename in ml_model_files.items():
            path = os.path.join(self.ml_dir, filename)
            models[name] = joblib.load(path)

        return models

    def _load_dl_models(self):
        """Load all DL models."""
        dl_model_files = {
            'FNN': 'fnn_tuned.keras',
            'CNN': 'cnn_tuned.keras',
            'LSTM': 'lstm_tuned.keras',
            'BiLSTM': 'bilstm_tuned.keras',
            'Hybrid': 'hybrid_cnn_bilstm_tuned.keras',
            'Autoencoder': 'autoencoder_tuned.keras'
        }

        models = {}
        for name, filename in dl_model_files.items():
            path = os.path.join(self.dl_dir, filename)
            models[name] = keras.models.load_model(path)

        return models

    def _generate_ml_predictions(self, X_scaled, X_unscaled):
        """Generate predictions from ML models."""
        predictions = []

        for name, model in self.ml_models.items():
            if name == 'Logistic Regression':
                pred = model.predict_proba(X_scaled)[:, 1]
            else:
                pred = model.predict_proba(X_unscaled)[:, 1]
            predictions.append(pred)

        return np.column_stack(predictions)

    def _generate_dl_predictions(self, X_scaled):
        """Generate predictions from DL models."""
        predictions = []

        for name, model in self.dl_models.items():
            if name == 'Autoencoder':
                reconstructed = model.predict(X_scaled, verbose=0)
                reconstruction_error = np.mean((X_scaled - reconstructed) ** 2, axis=1)
                pred = (reconstruction_error - reconstruction_error.min()) / \
                       (reconstruction_error.max() - reconstruction_error.min())
            else:
                pred = model.predict(X_scaled, verbose=0).ravel()

            predictions.append(pred)

        return np.column_stack(predictions)

    def predict(self, X, return_proba=False):
        """
        Make fraud predictions on new data.

        Args:
            X: Input features (DataFrame or numpy array)
            return_proba: If True, return probabilities instead of binary predictions

        Returns:
            predictions: Binary fraud labels (0/1) or probabilities
        """
        # Convert to DataFrame if necessary
        if isinstance(X, np.ndarray):
            X = pd.DataFrame(X)

        # Scale data
        X_scaled = pd.DataFrame(
            self.scaler.transform(X),
            columns=X.columns,
            index=X.index
        )

        # Generate base model predictions
        ml_predictions = self._generate_ml_predictions(X_scaled, X)
        dl_predictions = self._generate_dl_predictions(X_scaled.values)

        # Combine predictions
        all_predictions = np.column_stack([ml_predictions, dl_predictions])

        # Meta-learner prediction
        probabilities = self.meta_learner.predict_proba(all_predictions)[:, 1]

        if return_proba:
            return probabilities
        else:
            return (probabilities >= self.optimal_threshold).astype(int)

    def predict_batch(self, X, batch_size=1000):
        """
        Make predictions on large datasets in batches.

        Args:
            X: Input features
            batch_size: Number of samples per batch

        Returns:
            predictions: Binary fraud labels
        """
        n_samples = len(X)
        predictions = np.zeros(n_samples, dtype=int)

        for start_idx in range(0, n_samples, batch_size):
            end_idx = min(start_idx + batch_size, n_samples)
            batch = X.iloc[start_idx:end_idx]
            predictions[start_idx:end_idx] = self.predict(batch)

        return predictions

    def get_model_info(self):
        """Return model configuration and performance metrics."""
        return self.config


# Example usage
if __name__ == "__main__":
    # Initialize predictor
    predictor = MetaLearnerPredictor()

    # Load sample data
    print("\nLoading sample data...")
    data = pd.read_csv('../../data/train_72_features.csv')
    X_sample = data.drop('Class', axis=1).head(10)
    y_sample = data['Class'].head(10)

    # Make predictions
    print("\nMaking predictions...")
    predictions = predictor.predict(X_sample)
    probabilities = predictor.predict(X_sample, return_proba=True)

    # Display results
    print("\n" + "="*80)
    print("PREDICTION RESULTS")
    print("="*80)
    for i in range(len(predictions)):
        print(f"Sample {i+1}: True={y_sample.iloc[i]}, Predicted={predictions[i]}, "
              f"Probability={probabilities[i]:.4f}")

    # Display model info
    print("\n" + "="*80)
    print("MODEL INFORMATION")
    print("="*80)
    info = predictor.get_model_info()
    print(f"Training Date: {info['training_date']}")
    print(f"Test F1-Score: {info['performance']['test']['f1_score']:.4f}")
    print(f"Test ROC-AUC: {info['performance']['test']['roc_auc']:.4f}")
