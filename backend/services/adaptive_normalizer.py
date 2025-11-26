"""
Adaptive Normalizer for Meta-Learning
======================================
Normalizes model predictions from current distribution to training distribution.
Uses statistical normalization (z-score) with confidence-weighted blending.

Part of the Adaptive Meta-Layer research contribution.

Author: Hybrid Fraud Shield Team
Date: November 11, 2025
"""

import numpy as np
from typing import Dict, Tuple
from .prediction_tracker import PredictionTracker, TRAINING_STATISTICS


class AdaptiveNormalizer:
    """
    Normalizes model predictions to match training distribution.
    
    Features:
    - Z-score normalization with domain adaptation
    - Confidence-weighted blending (raw vs normalized)
    - Automatic adaptation to distribution changes
    - Handles edge cases (zero std, insufficient samples)
    
    Algorithm:
    1. Standardize prediction: z = (pred - current_mean) / current_std
    2. Scale to training distribution: norm = z * training_std + training_mean
    3. Calculate confidence based on sample count and stability
    4. Blend: final = confidence * norm + (1 - confidence) * raw
    """
    
    def __init__(self, prediction_tracker: PredictionTracker):
        """
        Initialize adaptive normalizer.
        
        Args:
            prediction_tracker: PredictionTracker instance with statistics
        """
        self.tracker = prediction_tracker
        self.min_samples_for_normalization = 50  # Minimum samples before normalizing
        self.confidence_saturation_samples = 500  # Samples for full confidence
    
    def normalize_predictions(self, raw_predictions: Dict[str, float]) -> Dict[str, float]:
        """
        Transform predictions from current distribution to training distribution.
        
        Uses Z-score normalization:
        normalized = (pred - current_mean) / current_std * training_std + training_mean
        
        Args:
            raw_predictions: Dict mapping model names to raw predictions (0-1)
            
        Returns:
            Dict mapping model names to normalized predictions (0-1)
        """
        normalized = {}
        
        for model, raw_pred in raw_predictions.items():
            # Skip invalid predictions
            if not (0.0 <= raw_pred <= 1.0):
                normalized[model] = np.clip(raw_pred, 0.0, 1.0)
                continue
            
            # Get current statistics (from recent predictions)
            current_stats = self.tracker.get_statistics(model)
            current_mean = current_stats.get('mean', 0.25)
            current_std = max(current_stats.get('std', 0.3), 0.01)  # Avoid division by zero
            sample_count = current_stats.get('count', 0)
            
            # Get training statistics (target distribution)
            training_stats = TRAINING_STATISTICS.get(model, {})
            training_mean = training_stats.get('mean', 0.25)
            training_std = training_stats.get('std', 0.3)
            
            # If too few samples, use training distribution
            if sample_count < self.min_samples_for_normalization:
                normalized[model] = raw_pred
                continue
            
            # Z-score: standardize to N(0,1)
            z_score = (raw_pred - current_mean) / current_std
            
            # Clip extreme z-scores to prevent outliers
            z_score = np.clip(z_score, -3.0, 3.0)
            
            # Scale to training distribution
            normalized_pred = z_score * training_std + training_mean
            
            # Clip to valid probability range
            normalized_pred = np.clip(normalized_pred, 0.0, 1.0)
            
            normalized[model] = float(normalized_pred)
        
        return normalized
    
    def calculate_confidence(self, model: str) -> float:
        """
        Calculate confidence in normalization based on:
        1. Number of samples collected (more samples = higher confidence)
        2. Stability of statistics (less variance = higher confidence)
        
        Args:
            model: Model name
            
        Returns:
            Confidence score between 0 and 1
        """
        # Get statistics
        stats = self.tracker.get_statistics(model)
        sample_count = stats.get('count', 0)
        
        # Confidence increases with more samples (sigmoid curve)
        # Maps 0 samples → 0.0 confidence, 500 samples → ~1.0 confidence
        sample_confidence = 1 / (1 + np.exp(-(sample_count - self.confidence_saturation_samples / 2) / 100))
        
        # Confidence decreases if std is changing rapidly (instability)
        recent_history = self.tracker.get_history(model, n=100)
        if len(recent_history) > 10:
            recent_std = np.std(recent_history)
            overall_std = stats.get('std', 0.3)
            
            # Stability: how close recent std is to overall std
            # If recent_std ≈ overall_std → stability ≈ 1.0
            std_diff = abs(recent_std - overall_std) / (overall_std + 0.01)
            stability = 1 / (1 + std_diff * 5)  # Penalize instability
        else:
            stability = 0.5  # Neutral if insufficient history
        
        # Combined confidence (weighted average)
        confidence = 0.7 * sample_confidence + 0.3 * stability
        
        return float(np.clip(confidence, 0.0, 1.0))
    
    def adaptive_normalize(self, raw_predictions: Dict[str, float]) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Blend raw and normalized predictions based on confidence.
        
        High confidence → use normalized (adapted to training distribution)
        Low confidence → use raw (not enough data to normalize reliably)
        
        Args:
            raw_predictions: Dict mapping model names to raw predictions
            
        Returns:
            Tuple of (blended_predictions, confidence_scores)
        """
        # Get normalized predictions
        normalized = self.normalize_predictions(raw_predictions)
        
        # Blend based on confidence
        blended = {}
        confidences = {}
        
        for model, raw_pred in raw_predictions.items():
            # Calculate confidence for this model
            confidence = self.calculate_confidence(model)
            confidences[model] = confidence
            
            # Get normalized prediction
            norm_pred = normalized.get(model, raw_pred)
            
            # Blend: high confidence → use normalized, low confidence → use raw
            blended_pred = confidence * norm_pred + (1 - confidence) * raw_pred
            blended[model] = float(blended_pred)
        
        return blended, confidences
    
    def get_normalization_info(self, model: str, raw_pred: float) -> Dict:
        """
        Get detailed normalization information for debugging/logging.
        
        Args:
            model: Model name
            raw_pred: Raw prediction value
            
        Returns:
            Dict with normalization details
        """
        # Current stats
        current_stats = self.tracker.get_statistics(model)
        current_mean = current_stats.get('mean', 0.25)
        current_std = current_stats.get('std', 0.3)
        sample_count = current_stats.get('count', 0)
        
        # Training stats
        training_stats = TRAINING_STATISTICS.get(model, {})
        training_mean = training_stats.get('mean', 0.25)
        training_std = training_stats.get('std', 0.3)
        
        # Normalized value
        if sample_count >= self.min_samples_for_normalization:
            z_score = (raw_pred - current_mean) / max(current_std, 0.01)
            z_score = np.clip(z_score, -3.0, 3.0)
            normalized = z_score * training_std + training_mean
            normalized = np.clip(normalized, 0.0, 1.0)
        else:
            normalized = raw_pred
            z_score = 0.0
        
        # Confidence
        confidence = self.calculate_confidence(model)
        
        # Blended
        blended = confidence * normalized + (1 - confidence) * raw_pred
        
        return {
            'model': model,
            'raw_prediction': raw_pred,
            'normalized_prediction': normalized,
            'blended_prediction': blended,
            'confidence': confidence,
            'z_score': z_score,
            'current_mean': current_mean,
            'current_std': current_std,
            'training_mean': training_mean,
            'training_std': training_std,
            'sample_count': sample_count
        }
    
    def should_normalize(self, model: str) -> bool:
        """
        Check if normalization should be applied for a model.
        
        Args:
            model: Model name
            
        Returns:
            True if enough samples collected, False otherwise
        """
        stats = self.tracker.get_statistics(model)
        sample_count = stats.get('count', 0)
        return sample_count >= self.min_samples_for_normalization
    
    def get_all_normalization_info(self) -> Dict:
        """
        Get normalization summary for all models.
        
        Returns:
            Dict with sample counts and normalization status
        """
        info = {
            'sample_counts': {},
            'should_normalize': {},
            'confidences': {}
        }
        
        for model in self.tracker.predictions_history.keys():
            stats = self.tracker.get_statistics(model)
            info['sample_counts'][model] = stats.get('count', 0)
            info['should_normalize'][model] = self.should_normalize(model)
            info['confidences'][model] = self.calculate_confidence(model)
        
        return info
