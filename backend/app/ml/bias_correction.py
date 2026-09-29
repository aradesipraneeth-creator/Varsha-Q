"""
VARSHA-Q Regime-Specific Bias Correction Engine
Learns regime-conditioned systematic errors in Numerical Weather Prediction (NWP):
Target: Error_bias = Observed_Rainfall - NWP_Rainfall
Corrected = max(0.0, NWP_Rainfall + Predicted_Bias)

Architecture:
- Separate specialized estimators for each meteorological regime:
    model_active, model_break, model_depression, model_coastal, model_orographic
- Global fallback model if regime-specific model is uncalibrated or has insufficient samples
- Explicit status tracking: "Regime-specific model active" vs "Global fallback"
"""
import joblib
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import Ridge


CORRECTION_FEATURES = [
    "nwp_rainfall",
    "spatiotemporal_embedding_mean",
    "elevation_m",
    "coastal_dist_km",
    "humidity_pct",
    "wind_speed_ms",
    "lag1_rainfall_mm"
]


class RegimeBiasCorrectionModel:
    """
    Regime-aware bias correction pipeline managing individual regime models and a global fallback.
    """
    def __init__(self, random_state: int = 42):
        self.feature_names = CORRECTION_FEATURES
        self.random_state = random_state
        # Models per regime
        self.regime_models: Dict[str, Any] = {}
        # Global fallback model
        self.global_model = GradientBoostingRegressor(
            n_estimators=80, max_depth=4, learning_rate=0.08, random_state=random_state
        )
        self.is_global_fitted = False
        self.sample_counts: Dict[str, int] = {}

    def _create_regime_estimator(self, regime: str):
        # Slightly tune estimators for regime characteristics
        if regime in ["OROGRAPHIC", "DEPRESSION_LOW"]:
            # High non-linearity in extreme lifting & cyclonic core
            return GradientBoostingRegressor(
                n_estimators=90, max_depth=5, learning_rate=0.06, random_state=self.random_state
            )
        else:
            return GradientBoostingRegressor(
                n_estimators=70, max_depth=4, learning_rate=0.08, random_state=self.random_state
            )

    def fit_regime(self, regime: str, X: np.ndarray, y_bias: np.ndarray):
        """
        Trains bias correction model for a specific regime.
        y_bias = Observed - NWP (target to learn)
        """
        if len(y_bias) < 5:
            # Insufficient samples for regime-specific model
            self.sample_counts[regime] = len(y_bias)
            return

        model = self._create_regime_estimator(regime)
        model.fit(X, y_bias)
        self.regime_models[regime] = model
        self.sample_counts[regime] = len(y_bias)

    def fit_global(self, X_all: np.ndarray, y_bias_all: np.ndarray):
        """Trains global fallback model across all combined regimes."""
        self.global_model.fit(X_all, y_bias_all)
        self.is_global_fitted = True

    def predict_correction(
        self, 
        regime: str, 
        features: np.ndarray, 
        raw_nwp: np.ndarray
    ) -> Dict[str, Any]:
        """
        features: (N_districts, len(CORRECTION_FEATURES))
        raw_nwp: (N_districts,)
        Returns:
          corrected_rainfall, raw_nwp, correction_delta, fallback_flag
        """
        N = len(raw_nwp)
        X = np.asarray(features, dtype=np.float64)
        if X.ndim == 1:
            X = X.reshape(1, -1)

        is_fallback = False
        fallback_reason = ""

        if regime in self.regime_models:
            model = self.regime_models[regime]
            strategy_name = f"Regime-Specific Model ({regime})"
        else:
            if not self.is_global_fitted:
                raise RuntimeError("Neither regime-specific nor global correction model is fitted.")
            model = self.global_model
            is_fallback = True
            strategy_name = "Global Fallback Model"
            fallback_reason = f"Regime '{regime}' model unavailable or insufficient training samples -> Global fallback active."

        # Predict bias correction: delta = Obs - NWP
        bias_pred = model.predict(X)

        # Corrected rainfall = raw_nwp + bias_pred, bounded at 0.0 (rain cannot be negative)
        raw_arr = np.asarray(raw_nwp, dtype=np.float64)
        corrected = np.maximum(0.0, raw_arr + bias_pred)

        return {
            "strategy": strategy_name,
            "is_fallback": is_fallback,
            "fallback_reason": fallback_reason,
            "raw_nwp_mm": [round(float(v), 2) for v in raw_arr],
            "corrected_mm": [round(float(v), 2) for v in corrected],
            "correction_delta_mm": [round(float(v), 2) for v in (corrected - raw_arr)],
            "mean_correction_mm": round(float(np.mean(corrected - raw_arr)), 2)
        }

    def save(self, filepath: Path):
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "regime_models": self.regime_models,
            "global_model": self.global_model,
            "is_global_fitted": self.is_global_fitted,
            "sample_counts": self.sample_counts,
            "feature_names": self.feature_names
        }, filepath)

    def load(self, filepath: Path):
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")
        data = joblib.load(filepath)
        self.regime_models = data["regime_models"]
        self.global_model = data["global_model"]
        self.is_global_fitted = data["is_global_fitted"]
        self.sample_counts = data.get("sample_counts", {})
        self.feature_names = data.get("feature_names", CORRECTION_FEATURES)
        return self
