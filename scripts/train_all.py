"""
VARSHA-Q Master Training Pipeline (train_all.py)
Executes end-to-end training of:
1. Weather Regime Classifier (Random Forest / Calibrated Classifier)
2. Spatiotemporal Models (Continuous-Time LNN + Spatial GNN + Gated Fusion)
3. Regime-Specific Bias Correction Models + Global Fallback
Saves trained artifacts to models/ and verification reports to reports/.
"""
import sys
import time
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from backend.app.data.demo_provider import DemoProvider
from backend.app.ml.regime_classifier import WeatherRegimeClassifier, REGIME_CLASSES
from backend.app.ml.bias_correction import RegimeBiasCorrectionModel, CORRECTION_FEATURES
from backend.app.ml.lnn_model import LiquidNeuralNetwork
from backend.app.ml.gnn_model import GraphNeuralNetwork, SpatiotemporalFusion
from backend.app.verification.metrics import calculate_continuous_metrics, calculate_categorical_metrics


def train_all():
    print("=" * 60)
    print("VARSHA-Q: TRAINING PIPELINE INITIALIZATION")
    print(f"Device: {'CUDA GPU' if torch.cuda.is_available() else 'CPU'}")
    print("=" * 60)

    models_dir = BASE_DIR / "models"
    reports_dir = BASE_DIR / "reports"
    models_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    provider = DemoProvider(random_seed=42)
    regimes = ["ACTIVE_MONSOON", "BREAK_MONSOON", "DEPRESSION_LOW", "COASTAL", "OROGRAPHIC"]

    # -------------------------------------------------------------
    # 1. Synthesize multi-regime training datasets
    # -------------------------------------------------------------
    print("\n[1/4] Generating multi-regime atmospheric training datasets...")
    X_regime = []
    y_regime = []

    correction_data_by_regime = {r: {"X": [], "y": []} for r in regimes}
    all_correction_X = []
    all_correction_y = []

    # Generate 40 synthetic episodes per regime with varied perturbation seeds
    for reg in regimes:
        for seed_idx in range(40):
            data = provider.generate_scenario_data(regime=reg, seed=seed_idx * 17 + 3)
            # Synoptic feature with slight noise
            syn_feat = data["synoptic_features"] + np.random.normal(0, 0.05, size=data["synoptic_features"].shape)
            X_regime.append(syn_feat)
            y_regime.append(reg)

            # District correction samples
            obs = np.array(data["observed_rainfall"])
            nwp = np.array(data["raw_nwp_rainfall"])
            bias = obs - nwp

            for i, d in enumerate(data["districts"]):
                feat = [
                    nwp[i],
                    float(np.mean(data["spatial_features"][i])),
                    d["elevation_m"],
                    d["coastal_dist_km"],
                    syn_feat[3],  # humidity
                    syn_feat[5],  # wind
                    data["temporal_sequences"][i, -1, 0]  # lag1 rain
                ]
                correction_data_by_regime[reg]["X"].append(feat)
                correction_data_by_regime[reg]["y"].append(bias[i])
                all_correction_X.append(feat)
                all_correction_y.append(bias[i])

    X_regime = np.array(X_regime)
    print(f"Generated {len(y_regime)} synoptic regime episodes and {len(all_correction_y)} district correction samples.")

    # -------------------------------------------------------------
    # 2. Train Weather Regime Classifier
    # -------------------------------------------------------------
    print("\n[2/4] Training Weather Regime Classifier...")
    clf = WeatherRegimeClassifier(random_state=42)
    clf.fit(X_regime, y_regime)
    regime_path = models_dir / "regime_classifier.pkl"
    clf.save(regime_path)
    print(f"Weather Regime Classifier saved to {regime_path}")

    # -------------------------------------------------------------
    # 3. Train LNN & GNN Spatiotemporal Models
    # -------------------------------------------------------------
    print("\n[3/4] Training Spatiotemporal Models (Continuous-Time LNN + Spatial GNN)...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    lnn = LiquidNeuralNetwork(input_dim=8, hidden_dim=32, num_layers=2).to(device)
    gnn = GraphNeuralNetwork(node_in_dim=7, hidden_dim=32, num_layers=2).to(device)
    fusion = SpatiotemporalFusion(d_temp=32, d_spat=32, d_fused=32).to(device)
    head = nn.Linear(32, 1).to(device)

    params = list(lnn.parameters()) + list(gnn.parameters()) + list(fusion.parameters()) + list(head.parameters())
    optimizer = optim.AdamW(params, lr=0.005, weight_decay=1e-4)
    criterion = nn.MSELoss()

    # Pre-train on sample batches
    demo_sample = provider.generate_scenario_data("ACTIVE_MONSOON", seed=42)
    t_seq = torch.tensor(demo_sample["temporal_sequences"], dtype=torch.float32, device=device)
    s_feat = torch.tensor(demo_sample["spatial_features"], dtype=torch.float32, device=device)
    adj = torch.tensor(demo_sample["adjacency_matrix"], dtype=torch.float32, device=device)
    targets = torch.tensor(demo_sample["observed_rainfall"], dtype=torch.float32, device=device).unsqueeze(-1)

    lnn.train()
    gnn.train()
    fusion.train()

    epochs = 20
    for epoch in range(epochs):
        optimizer.zero_grad()
        h_temp = lnn(t_seq)
        h_spat = gnn(s_feat, adj)
        fused = fusion(h_temp, h_spat)
        pred = head(fused)
        loss = criterion(pred, targets)
        loss.backward()
        optimizer.step()

    torch_path = models_dir / "spatiotemporal_weights.pt"
    torch.save({
        "lnn": lnn.state_dict(),
        "gnn": gnn.state_dict(),
        "fusion": fusion.state_dict(),
        "head": head.state_dict()
    }, torch_path)
    print(f"Spatiotemporal weights saved to {torch_path} (Final training loss: {loss.item():.4f})")

    # -------------------------------------------------------------
    # 4. Train Regime-Specific Bias Correction Models
    # -------------------------------------------------------------
    print("\n[4/4] Training Regime-Specific Bias Correction Models & Global Fallback...")
    corrector = RegimeBiasCorrectionModel(random_state=42)

    # Train global fallback
    corrector.fit_global(np.array(all_correction_X), np.array(all_correction_y))

    # Train individual regime models
    for reg in regimes:
        X_r = np.array(correction_data_by_regime[reg]["X"])
        y_r = np.array(correction_data_by_regime[reg]["y"])
        corrector.fit_regime(reg, X_r, y_r)
        print(f" - Trained specialized model for regime: {reg} ({len(y_r)} samples)")

    bias_path = models_dir / "bias_correction.pkl"
    corrector.save(bias_path)
    print(f"Bias correction models saved to {bias_path}")

    # -------------------------------------------------------------
    # Validation Evaluation Summary
    # -------------------------------------------------------------
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE: RUNNING VALIDATION SUITE")
    print("=" * 60)

    report_lines = [
        "# VARSHA-Q Training & Verification Report",
        f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"Device: {device}",
        "",
        "## Regime Model Performance",
        "| Regime | Samples | Raw NWP RMSE (mm) | Corrected RMSE (mm) | RMSE Reduction | CSI (>25mm) |",
        "|---|---|---|---|---|---|"
    ]

    for reg in regimes:
        val_data = provider.generate_scenario_data(reg, seed=999)
        val_obs = np.array(val_data["observed_rainfall"])
        val_nwp = np.array(val_data["raw_nwp_rainfall"])

        # Predict with regime model
        val_features = []
        for i, d in enumerate(val_data["districts"]):
            val_features.append([
                val_nwp[i],
                float(np.mean(val_data["spatial_features"][i])),
                d["elevation_m"],
                d["coastal_dist_km"],
                val_data["synoptic_features"][3],
                val_data["synoptic_features"][5],
                val_data["temporal_sequences"][i, -1, 0]
            ])
        corr_res = corrector.predict_correction(reg, np.array(val_features), val_nwp)
        val_cor = np.array(corr_res["corrected_mm"])

        m_raw = calculate_continuous_metrics(val_obs, val_nwp)
        m_cor = calculate_continuous_metrics(val_obs, val_cor)
        m_cat = calculate_categorical_metrics(val_obs, val_cor, threshold=25.0)

        red_pct = round((m_raw["rmse"] - m_cor["rmse"]) / max(1e-5, m_raw["rmse"]) * 100.0, 1)
        line = f"| {reg} | {len(val_obs)} | {m_raw['rmse']:.2f} | {m_cor['rmse']:.2f} | **{red_pct}%** | {m_cat['csi']:.3f} |"
        report_lines.append(line)
        print(line)

    report_file = reports_dir / "training_summary.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"\nSaved verification report to {report_file}")
    print("=" * 60)


if __name__ == "__main__":
    train_all()
