"""
VARSHA-Q End-to-End Machine Learning Pipeline
Orchestrates:
Data Ingestion -> LNN Temporal -> GNN Spatial -> Spatiotemporal Fusion
-> Weather Regime Classification -> Regime-Specific Bias Correction
-> Quantum-Inspired Optimization -> Probability & Uncertainty -> Verification
"""
import os
import torch
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional

from .lnn_model import LiquidNeuralNetwork
from .gnn_model import GraphNeuralNetwork, SpatiotemporalFusion
from .regime_classifier import WeatherRegimeClassifier, REGIME_CLASSES, REGIME_FEATURE_NAMES
from .bias_correction import RegimeBiasCorrectionModel, CORRECTION_FEATURES
from .probability_estimator import ProbabilityAndUncertaintyEstimator
from ..verification.metrics import calculate_full_verification_suite
from ..optimization.qubo_optimizer import run_benchmark_optimization


class VarshaQPipeline:
    """
    Unified operational pipeline for VARSHA-Q.
    Handles inference, training, scenario simulation, and verification.
    """
    def __init__(self, models_dir: Optional[Path] = None, device: str = "auto"):
        if device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        self.models_dir = Path(models_dir) if models_dir else Path(__file__).resolve().parents[3] / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)

        # PyTorch components
        self.lnn = LiquidNeuralNetwork(input_dim=8, hidden_dim=32, num_layers=2).to(self.device)
        self.gnn = GraphNeuralNetwork(node_in_dim=7, hidden_dim=32, num_layers=2).to(self.device)
        self.fusion = SpatiotemporalFusion(d_temp=32, d_spat=32, d_fused=32).to(self.device)

        # Sklearn / custom components
        self.regime_classifier = WeatherRegimeClassifier()
        self.bias_corrector = RegimeBiasCorrectionModel()
        self.prob_estimator = ProbabilityAndUncertaintyEstimator()

        self.is_loaded = False
        self._try_load_checkpoints()

    def _try_load_checkpoints(self):
        """Loads pretrained weights if present on disk."""
        regime_path = self.models_dir / "regime_classifier.pkl"
        bias_path = self.models_dir / "bias_correction.pkl"
        torch_path = self.models_dir / "spatiotemporal_weights.pt"

        try:
            if regime_path.exists():
                self.regime_classifier.load(regime_path)
            if bias_path.exists():
                self.bias_corrector.load(bias_path)
            if torch_path.exists():
                state_dict = torch.load(torch_path, map_location=self.device)
                self.lnn.load_state_dict(state_dict["lnn"])
                self.gnn.load_state_dict(state_dict["gnn"])
                self.fusion.load_state_dict(state_dict["fusion"])
            self.is_loaded = (
                self.regime_classifier.is_fitted and 
                self.bias_corrector.is_global_fitted
            )
        except Exception as e:
            print(f"Warning: Could not load saved weights ({e}). Pipeline needs training or demo data.")
            self.is_loaded = False

    def run_inference(
        self,
        synoptic_features: np.ndarray,
        district_spatial_features: np.ndarray,
        district_temporal_seq: np.ndarray,
        adjacency_matrix: np.ndarray,
        raw_nwp_rainfall: List[float],
        districts_meta: List[Dict[str, Any]],
        observed_rainfall: Optional[List[float]] = None,
        forced_regime: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes complete end-to-end forward pass.
        Returns:
          regime classification, spatiotemporal embeddings, corrected forecasts,
          heavy rain probabilities, uncertainty intervals, district intelligence,
          and verification metrics (if observations provided).
        """
        self.lnn.eval()
        self.gnn.eval()
        self.fusion.eval()

        with torch.no_grad():
            # 1. Temporal LNN: (N_districts, Seq_len, Features) -> (N_districts, 32)
            t_tensor = torch.tensor(district_temporal_seq, dtype=torch.float32, device=self.device)
            h_temporal = self.lnn(t_tensor)

            # 2. Spatial GNN: (N_districts, Node_features) -> (N_districts, 32)
            s_tensor = torch.tensor(district_spatial_features, dtype=torch.float32, device=self.device)
            adj_tensor = torch.tensor(adjacency_matrix, dtype=torch.float32, device=self.device)
            h_spatial = self.gnn(s_tensor, adj_tensor)

            # 3. Spatiotemporal Fusion: (N_districts, 32)
            h_fused = self.fusion(h_temporal, h_spatial)
            fused_np = h_fused.cpu().numpy()

        # 4. Weather Regime Classification (BEFORE correction)
        if self.regime_classifier.is_fitted:
            regime_out = self.regime_classifier.predict(synoptic_features)
        else:
            # Fallback if not yet trained
            regime_out = {
                "regime": "ACTIVE_MONSOON",
                "title": "Active Monsoon (Untrained Fallback)",
                "confidence": 0.50,
                "probabilities": {c: 0.2 for c in REGIME_CLASSES[:5]},
                "description": "Untrained fallback regime",
                "key_indicators": ["Fallback mode active"],
                "feature_contributions": []
            }

        # Support forced scenario override for judge demo testing
        active_regime = forced_regime if forced_regime else regime_out["regime"]
        if forced_regime and forced_regime != regime_out["regime"]:
            regime_out["regime"] = forced_regime
            regime_out["title"] = f"{forced_regime.replace('_', ' ').title()} (Demonstration Override)"

        # 5. Build features for Regime-Specific Bias Correction
        # Features: [nwp, fused_mean, elevation, coastal_dist, humidity, wind, lag1]
        N_districts = len(raw_nwp_rainfall)
        correction_features = np.zeros((N_districts, len(CORRECTION_FEATURES)), dtype=np.float64)

        for i in range(N_districts):
            d_meta = districts_meta[i] if i < len(districts_meta) else {}
            correction_features[i, 0] = raw_nwp_rainfall[i]
            correction_features[i, 1] = float(np.mean(fused_np[i]))
            correction_features[i, 2] = float(d_meta.get("elevation_m", 50.0))
            correction_features[i, 3] = float(d_meta.get("coastal_dist_km", 100.0))
            correction_features[i, 4] = float(synoptic_features[3])  # relative humidity
            correction_features[i, 5] = float(synoptic_features[5])  # wind speed
            correction_features[i, 6] = float(district_temporal_seq[i, -1, 0])  # lag1 rain

        # 6. Regime-Specific Bias Correction
        if self.bias_corrector.is_global_fitted:
            correction_res = self.bias_corrector.predict_correction(
                active_regime, correction_features, np.array(raw_nwp_rainfall)
            )
        else:
            # Fallback simple baseline if weights missing
            raw_arr = np.array(raw_nwp_rainfall, dtype=np.float64)
            # Default mild adjustment
            correction_res = {
                "strategy": "Uncalibrated Baseline Fallback",
                "is_fallback": True,
                "fallback_reason": "No trained correction checkpoint found.",
                "raw_nwp_mm": [round(float(v), 2) for v in raw_arr],
                "corrected_mm": [round(float(v), 2) for v in raw_arr],
                "correction_delta_mm": [0.0] * N_districts,
                "mean_correction_mm": 0.0
            }

        corrected_rain = correction_res["corrected_mm"]

        # 7. Heavy Rain Probabilities & Uncertainty
        district_forecasts = []
        for i in range(N_districts):
            d_meta = districts_meta[i] if i < len(districts_meta) else {}
            c_val = corrected_rain[i]
            r_val = raw_nwp_rainfall[i]
            coastal_dist = d_meta.get("coastal_dist_km", 100.0)
            elevation = d_meta.get("elevation_m", 50.0)

            prob_res = self.prob_estimator.estimate_district(
                corrected_rainfall=c_val,
                regime=active_regime,
                coastal_factor=1.0 if coastal_dist < 30.0 else 0.2,
                elevation_m=elevation
            )

            d_entry = {
                "district_id": d_meta.get("id", f"D_{i}"),
                "name": d_meta.get("name", f"District {i}"),
                "state": d_meta.get("state", "India"),
                "lat": d_meta.get("lat", 20.0),
                "lon": d_meta.get("lon", 80.0),
                "elevation_m": elevation,
                "coastal_dist_km": coastal_dist,
                "raw_nwp_rainfall_mm": r_val,
                "corrected_rainfall_mm": c_val,
                "delta_mm": round(c_val - r_val, 2),
                "regime": active_regime,
                "heavy_rain_probabilities": prob_res["heavy_rain_probabilities"],
                "uncertainty": prob_res["uncertainty"],
                "risk_category": prob_res["risk_category"],
                "risk_label": prob_res["risk_label"]
            }
            if observed_rainfall is not None and i < len(observed_rainfall):
                d_entry["observed_rainfall_mm"] = round(float(observed_rainfall[i]), 2)
            district_forecasts.append(d_entry)

        # 8. Verification Metrics (if ground truth observed rainfall is available)
        verification_results = None
        if observed_rainfall is not None and len(observed_rainfall) == N_districts:
            verification_results = calculate_full_verification_suite(
                observed=observed_rainfall,
                raw_nwp=raw_nwp_rainfall,
                corrected=corrected_rain,
                thresholds=[15.0, 25.0, 50.0, 100.0]
            )

        return {
            "regime_intelligence": regime_out,
            "correction_summary": {
                "strategy": correction_res["strategy"],
                "is_fallback": correction_res["is_fallback"],
                "fallback_reason": correction_res["fallback_reason"],
                "mean_nwp_mm": round(float(np.mean(raw_nwp_rainfall)), 2),
                "mean_corrected_mm": round(float(np.mean(corrected_rain)), 2),
                "mean_delta_mm": correction_res["mean_correction_mm"]
            },
            "spatiotemporal_representation": {
                "device": str(self.device),
                "num_districts": N_districts,
                "temporal_embedding_dim": 32,
                "spatial_embedding_dim": 32,
                "fused_embedding_dim": 32
            },
            "district_forecasts": district_forecasts,
            "verification": verification_results
        }
