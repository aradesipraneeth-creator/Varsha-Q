"""
VARSHA-Q Regime Classifier Training Script (train_regime_classifier.py)
"""
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

import numpy as np
from backend.app.data.demo_provider import DemoProvider
from backend.app.ml.regime_classifier import WeatherRegimeClassifier

def main():
    print("Training Weather Regime Classifier...")
    provider = DemoProvider(random_seed=42)
    regimes = ["ACTIVE_MONSOON", "BREAK_MONSOON", "DEPRESSION_LOW", "COASTAL", "OROGRAPHIC"]
    X, y = [], []
    for reg in regimes:
        for s in range(30):
            data = provider.generate_scenario_data(reg, seed=s*13+1)
            X.append(data["synoptic_features"] + np.random.normal(0, 0.05, size=data["synoptic_features"].shape))
            y.append(reg)
    clf = WeatherRegimeClassifier(random_state=42)
    clf.fit(np.array(X), y)
    out_path = BASE_DIR / "models" / "regime_classifier.pkl"
    clf.save(out_path)
    print(f"Saved trained Weather Regime Classifier to {out_path}")

if __name__ == "__main__":
    main()
