"""
Unit tests for Machine Learning Architectures (LNN, GNN, Regime, Correction, Probability)
"""
import pytest
import torch
import numpy as np
from pathlib import Path
from backend.app.ml.lnn_model import LiquidNeuralNetwork
from backend.app.ml.gnn_model import GraphNeuralNetwork, SpatiotemporalFusion
from backend.app.ml.regime_classifier import WeatherRegimeClassifier
from backend.app.ml.bias_correction import RegimeBiasCorrectionModel
from backend.app.ml.probability_estimator import ProbabilityAndUncertaintyEstimator


def test_lnn_forward_pass():
    # Batch=4, Seq_len=6, In_features=8
    x_seq = torch.randn(4, 6, 8)
    lnn = LiquidNeuralNetwork(input_dim=8, hidden_dim=32, num_layers=2)
    out = lnn(x_seq)
    assert out.shape == (4, 32)
    assert not torch.isnan(out).any()

def test_gnn_and_fusion_forward_pass():
    # 5 nodes, 7 node features
    x_nodes = torch.randn(5, 7)
    adj = torch.tensor([
        [0, 1, 0, 0, 0],
        [1, 0, 1, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 1, 0, 1],
        [0, 0, 0, 1, 0]
    ], dtype=torch.float32)

    gnn = GraphNeuralNetwork(node_in_dim=7, hidden_dim=32, num_layers=2)
    h_spatial = gnn(x_nodes, adj)
    assert h_spatial.shape == (5, 32)

    h_temporal = torch.randn(5, 32)
    fusion = SpatiotemporalFusion(d_temp=32, d_spat=32, d_fused=32)
    z_fused = fusion(h_temporal, h_spatial)
    assert z_fused.shape == (5, 32)

def test_regime_classifier():
    # Test trained model loaded from models/
    models_dir = Path(__file__).resolve().parents[1] / "models"
    model_path = models_dir / "regime_classifier.pkl"
    if model_path.exists():
        clf = WeatherRegimeClassifier()
        clf.load(model_path)
        # Mock synoptic vector
        feat = np.array([35.0, 75.0, 0.88, 88.0, -4.2, 12.5, 2.8, 240.0, 3.5, 0.45])
        res = clf.predict(feat)
        assert "regime" in res
        assert "confidence" in res
        assert 0.0 <= res["confidence"] <= 1.0
        assert "probabilities" in res

def test_probability_and_uncertainty():
    estimator = ProbabilityAndUncertaintyEstimator()
    res = estimator.estimate_district(corrected_rainfall=65.0, regime="DEPRESSION_LOW")
    assert res["corrected_rainfall_mm"] == 65.0
    assert res["risk_category"] in ["MODERATE", "HIGH", "VERY HIGH"]
    assert res["heavy_rain_probabilities"]["p_gt_25mm"] > 0.5
    assert res["uncertainty"]["lower_bound_p10_mm"] < res["uncertainty"]["upper_bound_p90_mm"]
