"""
VARSHA-Q Bias Correction Models Training Script (train_correction_models.py)
"""
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

import numpy as np
from backend.app.data.demo_provider import DemoProvider
from backend.app.ml.bias_correction import RegimeBiasCorrectionModel

def main():
    print("Training Regime-Specific Bias Correction Models...")
    provider = DemoProvider(random_seed=42)
    regimes = ["ACTIVE_MONSOON", "BREAK_MONSOON", "DEPRESSION_LOW", "COASTAL", "OROGRAPHIC"]

    corrector = RegimeBiasCorrectionModel(random_state=42)
    all_X, all_y = [], []

    for reg in regimes:
        X_reg, y_reg = [], []
        for s in range(30):
            data = provider.generate_scenario_data(reg, seed=s*19+7)
            obs = np.array(data["observed_rainfall"])
            nwp = np.array(data["raw_nwp_rainfall"])
            bias = obs - nwp
            for i, d in enumerate(data["districts"]):
                feat = [
                    nwp[i],
                    float(np.mean(data["spatial_features"][i])),
                    d["elevation_m"],
                    d["coastal_dist_km"],
                    data["synoptic_features"][3],
                    data["synoptic_features"][5],
                    data["temporal_sequences"][i, -1, 0]
                ]
                X_reg.append(feat)
                y_reg.append(bias[i])
                all_X.append(feat)
                all_y.append(bias[i])

        corrector.fit_regime(reg, np.array(X_reg), np.array(y_reg))
        print(f" - Regime {reg} trained with {len(y_reg)} samples.")

    corrector.fit_global(np.array(all_X), np.array(all_y))
    out_path = BASE_DIR / "models" / "bias_correction.pkl"
    corrector.save(out_path)
    print(f"Saved Bias Correction models to {out_path}")

if __name__ == "__main__":
    main()
