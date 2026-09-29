"""
Unit tests for VARSHA-Q Data Ingestion and Alignment
"""
import pytest
import numpy as np
import pandas as pd
from backend.app.data.demo_provider import DemoProvider
from backend.app.data.alignment import DataAlignmentEngine
from backend.app.data.feature_engineering import FeatureEngineeringPipeline


def test_demo_provider_scenarios():
    provider = DemoProvider(random_seed=42)
    regimes = ["ACTIVE_MONSOON", "BREAK_MONSOON", "DEPRESSION_LOW", "COASTAL", "OROGRAPHIC"]

    for r in regimes:
        data = provider.generate_scenario_data(r, seed=10)
        assert data["regime"] == r
        assert len(data["raw_nwp_rainfall"]) == len(provider.districts)
        assert len(data["observed_rainfall"]) == len(provider.districts)
        assert data["temporal_sequences"].shape == (len(provider.districts), 6, 8)
        assert data["spatial_features"].shape == (len(provider.districts), 7)
        assert data["adjacency_matrix"].shape == (len(provider.districts), len(provider.districts))

def test_data_alignment_qa_flags():
    engine = DataAlignmentEngine()
    points_df = pd.DataFrame([
        {"lat": 17.68, "lon": 83.21, "rainfall": 25.5},  # Near Vizag
        {"lat": 20.29, "lon": 85.82, "rainfall": -5.0},  # Invalid -> should impute
        {"lat": 18.52, "lon": 73.85, "rainfall": 999.0}  # Extreme -> should clip
    ])
    districts = [
        {"id": "D1", "lat": 17.6868, "lon": 83.2185},
        {"id": "D2", "lat": 20.2961, "lon": 85.8245},
        {"id": "D3", "lat": 18.5204, "lon": 73.8567}
    ]

    aligned_rain, qa_reports = engine.align_points_to_districts(points_df, districts)
    assert len(aligned_rain) == 3
    assert qa_reports[0]["qa_flag"] == "PASSED"
    assert qa_reports[1]["qa_flag"] == "IMPUTED_MISSING"
    assert qa_reports[2]["qa_flag"] == "EXTREME_CLIPPED"

    summary = engine.compute_quality_summary(qa_reports)
    assert summary["imputed_count"] == 1
    assert summary["clipped_extremes"] == 1
    assert summary["passed_count"] == 1

def test_feature_engineering_monsoon_phases():
    pipe = FeatureEngineeringPipeline()
    july_info = pipe.get_monsoon_phase(200) # July -> Peak active
    assert july_info["phase"] == "PEAK_ACTIVE"
    assert july_info["weight"] == 1.0

    jan_info = pipe.get_monsoon_phase(15) # Jan -> Dry winter
    assert jan_info["phase"] == "DRY_WINTER"
    assert jan_info["weight"] == 0.1
