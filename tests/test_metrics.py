"""
Unit tests for the VARSHA-Q Verification Engine
"""
import pytest
import numpy as np
from backend.app.verification.metrics import (
    calculate_continuous_metrics,
    calculate_categorical_metrics,
    calculate_fractions_skill_score,
    calculate_full_verification_suite,
)

def test_continuous_metrics_perfect_match():
    obs = [10.0, 25.0, 50.0, 0.0]
    fct = [10.0, 25.0, 50.0, 0.0]
    res = calculate_continuous_metrics(obs, fct)
    assert res["rmse"] == 0.0
    assert res["mae"] == 0.0
    assert res["bias"] == 0.0
    assert res["corr"] == 1.0
    assert res["count"] == 4

def test_continuous_metrics_with_bias():
    obs = [10.0, 20.0, 30.0]
    fct = [15.0, 25.0, 35.0]
    res = calculate_continuous_metrics(obs, fct)
    assert res["bias"] == 5.0
    assert res["mae"] == 5.0
    assert res["rmse"] == 5.0
    assert res["corr"] == 1.0

def test_categorical_metrics():
    # Obs: [T, T, F, F] for thr=25 (values >= 25)
    # Fct: [T, F, T, F]
    # Hits: index 0 (1)
    # Misses: index 1 (1)
    # False alarms: index 2 (1)
    # Correct negatives: index 3 (1)
    obs = [30.0, 28.0, 10.0, 5.0]
    fct = [40.0, 15.0, 26.0, 2.0]
    res = calculate_categorical_metrics(obs, fct, threshold=25.0)
    assert res["hits"] == 1
    assert res["misses"] == 1
    assert res["false_alarms"] == 1
    assert res["correct_negatives"] == 1
    # POD = 1 / (1 + 1) = 0.5
    assert res["pod"] == 0.5
    # FAR = 1 / (1 + 1) = 0.5
    assert res["far"] == 0.5
    # CSI = 1 / (1 + 1 + 1) = 0.333
    assert abs(res["csi"] - 0.333) < 0.01
    # a_ref = (1+1)*(1+1)/4 = 1.0. ETS = (1 - 1) / (3 - 1) = 0.0
    assert res["ets"] == 0.0

def test_fractions_skill_score():
    obs = np.array([0, 0, 30, 35, 40, 0, 0])
    fct_perfect = np.array([0, 0, 30, 35, 40, 0, 0])
    fss_perfect = calculate_fractions_skill_score(obs, fct_perfect, threshold=25.0, window_size=3)
    assert fss_perfect == 1.0

    fct_shifted = np.array([0, 30, 35, 40, 0, 0, 0])
    fss_shifted = calculate_fractions_skill_score(obs, fct_shifted, threshold=25.0, window_size=3)
    assert 0.0 <= fss_shifted <= 1.0

def test_full_verification_suite():
    obs = [5.0, 20.0, 35.0, 60.0]
    raw_nwp = [2.0, 10.0, 20.0, 30.0] # Systematic underprediction
    corrected = [4.5, 18.0, 34.0, 58.0] # Near ground truth
    suite = calculate_full_verification_suite(obs, raw_nwp, corrected, thresholds=[25.0, 50.0])
    assert "continuous" in suite
    assert "thresholds" in suite
    assert suite["continuous"]["corrected"]["rmse"] < suite["continuous"]["raw_nwp"]["rmse"]
    assert suite["continuous"]["rmse_reduction_pct"] > 0
