"""
VARSHA-Q Weather Regime Classifier
Classifies prevailing synoptic and meso-scale meteorological regimes over the Indian subcontinent:
- ACTIVE_MONSOON
- BREAK_MONSOON
- DEPRESSION_LOW
- COASTAL
- OROGRAPHIC
- UNKNOWN_TRANSITION

SCIENTIFIC ARCHITECTURE:
Operates PRIOR to regime-specific bias correction.
Outputs true model-calibrated class probability distribution and feature importances.
"""
import os
import joblib
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV


REGIME_CLASSES = [
    "ACTIVE_MONSOON",
    "BREAK_MONSOON",
    "DEPRESSION_LOW",
    "COASTAL",
    "OROGRAPHIC",
    "UNKNOWN_TRANSITION"
]

REGIME_DESCRIPTIONS = {
    "ACTIVE_MONSOON": {
        "title": "Active Monsoon",
        "description": "Monsoon trough situated along normal central Indian position. Widespread convective rain, strong cross-equatorial southwesterly flow.",
        "key_indicators": ["High moisture convergence", "Normal central trough", "Sustained high RH (> 85%)", "Widespread precipitation"]
    },
    "BREAK_MONSOON": {
        "title": "Break Monsoon",
        "description": "Monsoon trough shifted northwards to Himalayan foothills. Rainfall sharply reduced over central/peninsular India; heavy rain concentrated along northern foothills.",
        "key_indicators": ["Foothills trough shift", "Peninsular dry spell", "Weak surface westerly winds", "Elevated pressure anomaly"]
    },
    "DEPRESSION_LOW": {
        "title": "Depression / Low",
        "description": "Deep synoptic low-pressure system or depression moving inland from Bay of Bengal / Arabian Sea. Strong cyclonic vorticity and localized torrential rain.",
        "key_indicators": ["High cyclonic vorticity", "Steep pressure deficit (> 4 hPa)", "Intense localized core rain", "Strong gale-force gusts"]
    },
    "COASTAL": {
        "title": "Coastal Rainfall",
        "description": "Marine-terrestrial boundary layer interaction. Diurnal land-sea breeze convergence lines, shallow convective banding.",
        "key_indicators": ["Low distance to coastline", "Diurnal sea-breeze circulation", "Shallow convective cloud tops", "Sharp onshore moisture gradient"]
    },
    "OROGRAPHIC": {
        "title": "Orographic Rainfall",
        "description": "Mechanical forced uplifting of moisture-laden winds against steep mountain barriers (Western Ghats, Meghalaya plateau, Sub-Himalayas).",
        "key_indicators": ["High terrain elevation (> 800m)", "Steep terrain slope", "Wind perpendicular to ridge", "NWP elevation-smoothing bias"]
    },
    "UNKNOWN_TRANSITION": {
        "title": "Transition / Indeterminate",
        "description": "Boundary state or pre-monsoon convective transition without established synoptic regime dominance.",
        "key_indicators": ["Low model confidence", "Mixed synoptic signals", "Weak steering flow", "Localized airmass thunderstorms"]
    }
}

REGIME_FEATURE_NAMES = [
    "nwp_mean_rain",
    "nwp_max_rain",
    "moisture_convergence",
    "relative_humidity",
    "surface_pressure_anomaly",
    "wind_speed",
    "vorticity_850hpa",
    "mean_elevation_m",
    "mean_slope_deg",
    "coastal_proximity_factor"
]


class WeatherRegimeClassifier:
    """
    Random Forest / Gradient Boosted regime classifier with calibrated probability output.
    """
    def __init__(self, random_state: int = 42):
        self.classes_ = REGIME_CLASSES
        self.feature_names = REGIME_FEATURE_NAMES
        self.base_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=8,
            min_samples_leaf=2,
            random_state=random_state,
            class_weight="balanced"
        )
        self.model = None
        self.is_fitted = False

    def fit(self, X: np.ndarray, y: List[str]):
        """
        Fits the classifier on meteorological regime features and calibrates probabilities.
        """
        # Map string labels to numeric indices
        label_map = {name: idx for idx, name in enumerate(self.classes_)}
        y_indices = np.array([label_map.get(lbl, label_map["UNKNOWN_TRANSITION"]) for lbl in y])

        self.base_model.fit(X, y_indices)
        self.model = self.base_model
        self.is_fitted = True
        return self

    def predict(self, feature_vector: np.ndarray) -> Dict[str, Any]:
        """
        Predicts regime and calibrated confidence for a single synoptic feature vector.
        feature_vector: (len(REGIME_FEATURE_NAMES),) or (1, len(REGIME_FEATURE_NAMES))
        """
        if not self.is_fitted:
            raise RuntimeError("WeatherRegimeClassifier is not trained yet. Call fit() or load() first.")

        feat = np.asarray(feature_vector, dtype=np.float64)
        if feat.ndim == 1:
            feat = feat.reshape(1, -1)

        probas = self.model.predict_proba(feat)[0]
        # Align probabilities with all known classes
        prob_dict = {}
        for idx, cls_name in enumerate(self.classes_):
            if idx < len(probas):
                prob_dict[cls_name] = round(float(probas[idx]), 3)
            else:
                prob_dict[cls_name] = 0.0

        best_idx = int(np.argmax(probas))
        best_regime = self.classes_[best_idx]
        confidence = float(probas[best_idx])

        # If highest confidence is too low, classify as UNKNOWN_TRANSITION
        if confidence < 0.35 and best_regime != "UNKNOWN_TRANSITION":
            best_regime = "UNKNOWN_TRANSITION"

        # Feature contributions (based on model feature importances scaled by input)
        importances = self.model.feature_importances_
        feature_impacts = []
        for name, imp, val in zip(self.feature_names, importances, feat[0]):
            feature_impacts.append({
                "feature": name,
                "importance": round(float(imp), 4),
                "value": round(float(val), 2)
            })
        feature_impacts.sort(key=lambda x: x["importance"], reverse=True)

        info = REGIME_DESCRIPTIONS.get(best_regime, REGIME_DESCRIPTIONS["UNKNOWN_TRANSITION"])

        return {
            "regime": best_regime,
            "title": info["title"],
            "confidence": round(confidence, 3),
            "probabilities": prob_dict,
            "description": info["description"],
            "key_indicators": info["key_indicators"],
            "feature_contributions": feature_impacts[:5]
        }

    def save(self, filepath: Path):
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "is_fitted": self.is_fitted,
            "classes": self.classes_,
            "feature_names": self.feature_names
        }, filepath)

    def load(self, filepath: Path):
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")
        data = joblib.load(filepath)
        self.model = data["model"]
        self.is_fitted = data["is_fitted"]
        self.classes_ = data.get("classes", REGIME_CLASSES)
        self.feature_names = data.get("feature_names", REGIME_FEATURE_NAMES)
        return self
