"""
Distribution Shift Detector for Adaptive Meta-Learning
=======================================================
Detects significant shifts in prediction distributions using statistical tests.
Automatically adjusts adaptation rate when shifts are detected.

Part of the Adaptive Meta-Layer research contribution.

Author: Hybrid Fraud Shield Team
Date: November 11, 2025
"""

import numpy as np
from scipy import stats
from typing import Dict, Tuple, List, Optional
from datetime import datetime, timedelta
from .prediction_tracker import PredictionTracker


class DistributionShiftDetector:
    """
    Detects distribution shifts in model predictions using statistical tests.
    
    Features:
    - Kolmogorov-Smirnov test for distribution comparison
    - Configurable sensitivity (p-value threshold)
    - Automatic adaptation rate adjustment on shift detection
    - Shift history tracking
    - Multiple detection windows
    
    When a shift is detected:
    1. Log the shift event
    2. Increase adaptation rate (alpha) temporarily
    3. Optionally reset statistics
    """
    
    def __init__(
        self,
        prediction_tracker: PredictionTracker,
        p_value_threshold: float = 0.05,
        window_size: int = 100,
        comparison_window_size: int = 200
    ):
        """
        Initialize distribution shift detector.
        
        Args:
            prediction_tracker: PredictionTracker instance
            p_value_threshold: Significance level for shift detection (default 0.05)
            window_size: Size of recent window for comparison
            comparison_window_size: Size of baseline window for comparison
        """
        self.tracker = prediction_tracker
        self.p_value_threshold = p_value_threshold
        self.window_size = window_size
        self.comparison_window_size = comparison_window_size
        
        # Shift detection history
        self.shift_events: Dict[str, List[Dict]] = {
            model: [] for model in prediction_tracker.predictions_history.keys()
        }
        
        # Temporary adaptation rate boost
        self.adaptation_boost_duration = 100  # predictions
        self.boosted_models: Dict[str, int] = {}  # model -> countdown
    
    def detect_shift(self, model: str) -> Tuple[bool, float, str]:
        """
        Detect if prediction distribution has shifted significantly.
        
        Uses Kolmogorov-Smirnov two-sample test:
        - Compares recent predictions vs older predictions
        - Null hypothesis: distributions are the same
        - If p-value < threshold → reject null → shift detected
        
        Args:
            model: Model name
            
        Returns:
            Tuple of (shift_detected, test_statistic, shift_type)
        """
        # Get prediction history
        history = self.tracker.get_history(model)
        
        # Need enough samples
        min_samples_needed = self.window_size + self.comparison_window_size
        if len(history) < min_samples_needed:
            return False, 0.0, 'insufficient_data'
        
        # Split into recent and older windows
        recent_predictions = history[-self.window_size:]
        older_predictions = history[-(self.window_size + self.comparison_window_size):-self.window_size]
        
        # Kolmogorov-Smirnov two-sample test
        statistic, p_value = stats.ks_2samp(recent_predictions, older_predictions)
        
        # Detect shift
        shift_detected = p_value < self.p_value_threshold
        
        # Determine shift type
        if shift_detected:
            recent_mean = np.mean(recent_predictions)
            older_mean = np.mean(older_predictions)
            
            if recent_mean > older_mean + 0.1:
                shift_type = 'upward_shift'  # Predictions increasing
            elif recent_mean < older_mean - 0.1:
                shift_type = 'downward_shift'  # Predictions decreasing
            else:
                shift_type = 'variance_shift'  # Variance change
        else:
            shift_type = 'no_shift'
        
        return shift_detected, float(statistic), shift_type
    
    def detect_all_shifts(self) -> Dict[str, Tuple[bool, float, str]]:
        """
        Detect shifts for all models.
        
        Returns:
            Dict mapping model names to (shift_detected, statistic, shift_type)
        """
        results = {}
        for model in self.tracker.predictions_history.keys():
            results[model] = self.detect_shift(model)
        return results
    
    def handle_shift(self, model: str, shift_type: str, statistic: float):
        """
        Handle detected distribution shift.
        
        Actions:
        1. Log shift event
        2. Increase adaptation rate temporarily
        3. Mark model for enhanced monitoring
        
        Args:
            model: Model name
            shift_type: Type of shift detected
            statistic: KS test statistic
        """
        # Log shift event
        shift_event = {
            'timestamp': datetime.now().isoformat(),
            'shift_type': shift_type,
            'test_statistic': statistic,
            'p_value_threshold': self.p_value_threshold
        }
        self.shift_events[model].append(shift_event)
        
        # Keep only recent shift events (last 50)
        if len(self.shift_events[model]) > 50:
            self.shift_events[model] = self.shift_events[model][-50:]
        
        # Increase adaptation rate
        self.tracker.increase_adaptation_rate(model, factor=5.0)
        
        # Set boost countdown
        self.boosted_models[model] = self.adaptation_boost_duration
        
        print(f"🚨 Distribution shift detected for {model}: {shift_type} (KS={statistic:.4f})")
    
    def update_boost_countdown(self, model: str):
        """
        Decrease boost countdown after each prediction.
        Reset adaptation rate when countdown reaches 0.
        
        Args:
            model: Model name
        """
        if model in self.boosted_models:
            self.boosted_models[model] -= 1
            
            if self.boosted_models[model] <= 0:
                # Reset to normal adaptation rate
                self.tracker.alpha[model] = 0.01
                del self.boosted_models[model]
                print(f"✅ Adaptation rate normalized for {model}")
    
    def check_and_handle_shifts(self) -> Dict[str, bool]:
        """
        Check all models for shifts and handle automatically.
        
        Returns:
            Dict mapping model names to shift detection status
        """
        shift_status = {}
        
        for model in self.tracker.predictions_history.keys():
            shift_detected, statistic, shift_type = self.detect_shift(model)
            shift_status[model] = shift_detected
            
            if shift_detected:
                self.handle_shift(model, shift_type, statistic)
            
            # Update boost countdown
            self.update_boost_countdown(model)
        
        return shift_status
    
    def get_shift_history(self, model: str, n: Optional[int] = 10) -> List[Dict]:
        """
        Get recent shift events for a model.
        
        Args:
            model: Model name
            n: Number of recent events to return
            
        Returns:
            List of shift event dicts
        """
        events = self.shift_events.get(model, [])
        if n is not None:
            return events[-n:]
        return events
    
    def get_all_shift_history(self, n: Optional[int] = 5) -> Dict[str, List[Dict]]:
        """
        Get shift history for all models.
        
        Args:
            n: Number of recent events per model
            
        Returns:
            Dict mapping model names to their shift histories
        """
        return {
            model: self.get_shift_history(model, n)
            for model in self.shift_events.keys()
        }
    
    def get_shift_summary(self) -> str:
        """
        Get a formatted summary of shift detection status.
        
        Returns:
            Formatted summary string
        """
        summary = "\n🚨 Distribution Shift Detector Summary:\n"
        summary += f"   P-value threshold: {self.p_value_threshold}\n"
        summary += f"   Window size: {self.window_size}\n"
        summary += f"   Comparison window: {self.comparison_window_size}\n\n"
        
        # Check current shifts
        shift_results = self.detect_all_shifts()
        
        summary += "   Current Shift Status:\n"
        for model, (detected, statistic, shift_type) in shift_results.items():
            status = "🔴 SHIFT" if detected else "🟢 STABLE"
            summary += f"   {model:25s} | {status} | KS={statistic:.4f} | {shift_type}\n"
        
        # Boosted models
        if self.boosted_models:
            summary += "\n   Models with Boosted Adaptation:\n"
            for model, countdown in self.boosted_models.items():
                summary += f"   {model:25s} | {countdown} predictions remaining\n"
        
        return summary
    
    def reset_shift_history(self, model: Optional[str] = None):
        """
        Reset shift detection history.
        
        Args:
            model: Model name to reset (None = reset all)
        """
        if model is not None:
            self.shift_events[model] = []
            if model in self.boosted_models:
                del self.boosted_models[model]
            print(f"🔄 Reset shift history for {model}")
        else:
            for m in self.shift_events.keys():
                self.shift_events[m] = []
            self.boosted_models.clear()
            print(f"🔄 Reset all shift histories")
