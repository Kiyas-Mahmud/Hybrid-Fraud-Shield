"""
Prediction Tracker for Adaptive Meta-Learning
==============================================
Tracks prediction statistics for each model to enable adaptive normalization.
Stores running mean, std, min, max for each of the 11 models.

Part of the Adaptive Meta-Layer research contribution.

Author: Hybrid Fraud Shield Team
Date: November 11, 2025
"""

import numpy as np
import json
import os
from collections import deque
from datetime import datetime
from typing import Dict, List, Optional


# Training distribution from IEEE-CIS dataset (approximate statistics)
TRAINING_STATISTICS = {
    'ml_catboost': {'mean': 0.18, 'std': 0.22, 'min': 0.0, 'max': 0.95},
    'ml_lightgbm': {'mean': 0.20, 'std': 0.24, 'min': 0.0, 'max': 0.98},
    'ml_logistic_regression': {'mean': 0.25, 'std': 0.30, 'min': 0.0, 'max': 1.0},
    'ml_random_forest': {'mean': 0.22, 'std': 0.26, 'min': 0.0, 'max': 1.0},
    'ml_xgboost': {'mean': 0.19, 'std': 0.23, 'min': 0.0, 'max': 0.97},
    'dl_autoencoder': {'mean': 0.24, 'std': 0.28, 'min': 0.0, 'max': 0.99},
    'dl_bilstm': {'mean': 0.26, 'std': 0.31, 'min': 0.0, 'max': 1.0},
    'dl_cnn': {'mean': 0.25, 'std': 0.29, 'min': 0.0, 'max': 1.0},
    'dl_fnn': {'mean': 0.23, 'std': 0.27, 'min': 0.0, 'max': 0.99},
    'dl_hybrid_dl': {'mean': 0.22, 'std': 0.26, 'min': 0.0, 'max': 0.98},
    'dl_lstm': {'mean': 0.25, 'std': 0.28, 'min': 0.0, 'max': 1.0}
}


class PredictionTracker:
    """
    Tracks prediction statistics for adaptive meta-learning.
    
    Features:
    - Rolling window of predictions (default 1000 samples)
    - Running statistics: mean, std, min, max
    - Exponential Moving Average (EMA) for online updates
    - Persistence to disk
    - Automatic initialization with training distribution
    """
    
    def __init__(self, window_size: int = 1000, stats_file: str = None):
        """
        Initialize prediction tracker.
        
        Args:
            window_size: Maximum number of predictions to keep in history
            stats_file: Path to save/load statistics (default: backend/data/prediction_stats.json)
        """
        self.window_size = window_size
        
        # Set default stats file path
        if stats_file is None:
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(backend_dir, 'data')
            os.makedirs(data_dir, exist_ok=True)
            self.stats_file = os.path.join(data_dir, 'prediction_stats.json')
        else:
            self.stats_file = stats_file
        
        # Prediction history (rolling window)
        self.predictions_history: Dict[str, deque] = {
            model: deque(maxlen=window_size) 
            for model in TRAINING_STATISTICS.keys()
        }
        
        # Current statistics (updated with EMA)
        self.stats: Dict[str, Dict] = {}
        
        # EMA decay rate (alpha)
        # Higher alpha = more weight to recent observations
        self.alpha: Dict[str, float] = {
            model: 0.01 for model in TRAINING_STATISTICS.keys()
        }
        
        # Update counter for auto-save
        self.update_count = 0
        self.auto_save_interval = 100  # Save every 100 updates
        
        # Initialize or load statistics
        if os.path.exists(self.stats_file):
            self.load_from_disk()
            print(f"📊 Loaded prediction statistics from {self.stats_file}")
        else:
            self.initialize_with_training_distribution()
            self._pre_seed_with_training_distribution()  # Pre-seed for immediate normalization
            print(f"[INIT] Initialized with training distribution statistics + 100 synthetic samples per model")
    
    def initialize_with_training_distribution(self):
        """
        Bootstrap statistics using IEEE-CIS training distribution.
        """
        for model, train_stats in TRAINING_STATISTICS.items():
            self.stats[model] = {
                'mean': train_stats['mean'],
                'std': train_stats['std'],
                'min': train_stats['min'],
                'max': train_stats['max'],
                'count': 0,  # No actual samples yet
                'last_updated': datetime.now().isoformat()
            }
    
    def update(self, model_predictions: Dict[str, float]):
        """
        Add new predictions to history and update statistics.
        
        Args:
            model_predictions: Dict mapping model names to predictions (0-1)
        """
        for model, prediction in model_predictions.items():
            if model not in self.predictions_history:
                continue
            
            # Only track valid probabilities
            if not (0.0 <= prediction <= 1.0):
                continue
            
            # Add to history
            self.predictions_history[model].append(prediction)
            
            # Update statistics using EMA
            self._update_statistics_ema(model, prediction)
        
        # Increment update counter and auto-save
        self.update_count += 1
        if self.update_count % self.auto_save_interval == 0:
            self.save_to_disk()
    
    def _update_statistics_ema(self, model: str, prediction: float):
        """
        Update statistics using Exponential Moving Average.
        
        Args:
            model: Model name
            prediction: New prediction value
        """
        alpha = self.alpha[model]
        
        # Get current stats
        current_mean = self.stats[model]['mean']
        current_std = self.stats[model]['std']
        current_min = self.stats[model]['min']
        current_max = self.stats[model]['max']
        count = self.stats[model]['count']
        
        # Update mean: EMA
        new_mean = alpha * prediction + (1 - alpha) * current_mean
        
        # Update std: EMA of variance
        variance = current_std ** 2
        new_variance = alpha * (prediction - new_mean) ** 2 + (1 - alpha) * variance
        new_std = np.sqrt(max(new_variance, 1e-6))  # Avoid zero std
        
        # Update min/max
        new_min = min(current_min, prediction)
        new_max = max(current_max, prediction)
        
        # Update stats
        self.stats[model] = {
            'mean': float(new_mean),
            'std': float(new_std),
            'min': float(new_min),
            'max': float(new_max),
            'count': count + 1,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_statistics(self, model: str) -> Dict:
        """
        Get current statistics for a model.
        
        Args:
            model: Model name
            
        Returns:
            Dict with mean, std, min, max, count
        """
        return self.stats.get(model, TRAINING_STATISTICS.get(model, {}))
    
    def get_all_statistics(self) -> Dict:
        """
        Get statistics for all models.
        
        Returns:
            Dict mapping model names to their statistics
        """
        return self.stats
    
    def get_training_statistics(self, model: str) -> Dict:
        """
        Get original training distribution statistics.
        
        Args:
            model: Model name
            
        Returns:
            Training statistics dict
        """
        return TRAINING_STATISTICS.get(model, {})
    
    def get_history(self, model: str, n: Optional[int] = None) -> List[float]:
        """
        Get prediction history for a model.
        
        Args:
            model: Model name
            n: Number of recent predictions to return (None = all)
            
        Returns:
            List of predictions
        """
        history = list(self.predictions_history.get(model, []))
        if n is not None:
            return history[-n:]
        return history
    
    def reset_model_statistics(self, model: str):
        """
        Reset statistics for a specific model to training distribution.
        
        Args:
            model: Model name
        """
        if model in TRAINING_STATISTICS:
            train_stats = TRAINING_STATISTICS[model]
            self.stats[model] = {
                'mean': train_stats['mean'],
                'std': train_stats['std'],
                'min': train_stats['min'],
                'max': train_stats['max'],
                'count': 0,
                'last_updated': datetime.now().isoformat()
            }
            self.predictions_history[model].clear()
            print(f"🔄 Reset statistics for {model}")
    
    def reset_all_statistics(self):
        """
        Reset all statistics to training distribution.
        """
        for model in TRAINING_STATISTICS.keys():
            self.reset_model_statistics(model)
        print(f"🔄 Reset all statistics to training distribution")
    
    def increase_adaptation_rate(self, model: str, factor: float = 5.0):
        """
        Temporarily increase adaptation rate (alpha) for a model.
        Useful when distribution shift is detected.
        
        Args:
            model: Model name
            factor: Multiplication factor for alpha
        """
        new_alpha = min(self.alpha[model] * factor, 0.1)  # Cap at 10%
        self.alpha[model] = new_alpha
        print(f"⚡ Increased adaptation rate for {model}: α={new_alpha:.4f}")
    
    def save_to_disk(self):
        """
        Save statistics to disk as JSON.
        """
        try:
            data = {
                'statistics': self.stats,
                'alpha': self.alpha,
                'update_count': self.update_count,
                'window_size': self.window_size,
                'last_saved': datetime.now().isoformat()
            }
            
            with open(self.stats_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # print(f"💾 Saved statistics to {self.stats_file}")
            
        except Exception as e:
            print(f"❌ Error saving statistics: {str(e)}")
    
    def load_from_disk(self):
        """
        Load statistics from disk.
        """
        try:
            with open(self.stats_file, 'r') as f:
                data = json.load(f)
            
            self.stats = data.get('statistics', {})
            self.alpha = data.get('alpha', {model: 0.01 for model in TRAINING_STATISTICS.keys()})
            self.update_count = data.get('update_count', 0)
            
            # Ensure all models have statistics
            for model in TRAINING_STATISTICS.keys():
                if model not in self.stats:
                    self.stats[model] = TRAINING_STATISTICS[model].copy()
                    self.stats[model]['count'] = 0
                    self.stats[model]['last_updated'] = datetime.now().isoformat()
            
            print(f"✅ Loaded statistics: {self.update_count} predictions tracked")
            
        except Exception as e:
            print(f"⚠️ Error loading statistics: {str(e)}")
            self.initialize_with_training_distribution()
    
    def get_summary(self) -> str:
        """
        Get a summary of current tracking status.
        
        Returns:
            Formatted summary string
        """
        summary = f"\n📊 Prediction Tracker Summary:\n"
        summary += f"   Total predictions tracked: {self.update_count}\n"
        summary += f"   Window size: {self.window_size}\n"
        summary += f"   Auto-save interval: {self.auto_save_interval}\n\n"
        
        summary += "   Model Statistics:\n"
        for model, stats in self.stats.items():
            summary += f"   {model:25s} | mean={stats['mean']:.3f}, std={stats['std']:.3f}, n={stats['count']}\n"
        
        return summary
    
    def _pre_seed_with_training_distribution(self, num_samples: int = 100):
        """
        Pre-seed the tracker with synthetic samples from training distribution.
        This enables immediate normalization without waiting for real samples.
        
        Synthetic samples are drawn from Gaussian distribution matching IEEE-CIS training stats.
        
        Args:
            num_samples: Number of synthetic samples to generate per model (default: 100)
        """
        import numpy as np
        
        print(f"🌱 Pre-seeding tracker with {num_samples} synthetic samples per model...")
        
        for model, train_stats in TRAINING_STATISTICS.items():
            mean = train_stats['mean']
            std = train_stats['std']
            min_val = train_stats['min']
            max_val = train_stats['max']
            
            # Generate samples from Gaussian, clipped to valid range
            samples = np.random.normal(mean, std, num_samples)
            samples = np.clip(samples, min_val, max_val)
            
            # Add to history
            for sample in samples:
                self.predictions_history[model].append(float(sample))
            
            # Update statistics
            self.stats[model]['count'] = num_samples
            self.stats[model]['mean'] = float(np.mean(samples))
            self.stats[model]['std'] = float(np.std(samples))
            self.stats[model]['min'] = float(np.min(samples))
            self.stats[model]['max'] = float(np.max(samples))
        
        print(f"✅ Pre-seeded with {num_samples} samples - normalization ready from first prediction")


# Global instance (singleton pattern)
_tracker_instance = None

def get_prediction_tracker() -> PredictionTracker:
    """
    Get or create the global prediction tracker instance.
    
    Returns:
        PredictionTracker singleton
    """
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = PredictionTracker()
    return _tracker_instance
