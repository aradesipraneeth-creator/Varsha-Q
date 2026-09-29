"""
VARSHA-Q Single-Run Inference Script (run_inference.py)
Executes a single regime scenario or live inference pass and prints district-level forecast table.
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from backend.app.data.demo_provider import DemoProvider
from backend.app.ml.pipeline import VarshaQPipeline


def main(scenario: str = "ACTIVE_MONSOON"):
    print(f"Running VARSHA-Q Inference for Scenario: {scenario}")
    provider = DemoProvider(random_seed=42)
    pipeline = VarshaQPipeline(models_dir=BASE_DIR / "models")

    data = provider.generate_scenario_data(scenario, seed=77)
    res = pipeline.run_inference(
        synoptic_features=data["synoptic_features"],
        district_spatial_features=data["spatial_features"],
        district_temporal_seq=data["temporal_sequences"],
        adjacency_matrix=data["adjacency_matrix"],
        raw_nwp_rainfall=data["raw_nwp_rainfall"],
        districts_meta=data["districts"],
        observed_rainfall=data["observed_rainfall"],
        forced_regime=scenario
    )

    reg = res["regime_intelligence"]
    print(f"\nRegime: {reg['regime']} (Confidence: {reg['confidence'] * 100:.1f}%)")
    print(f"Correction Strategy: {res['correction_summary']['strategy']}")
    print("\nDistrict Sample Forecasts:")
    print(f"{'District':<20} | {'State':<15} | {'Raw NWP':<8} | {'Corrected':<9} | {'P(>50mm)':<8} | {'Risk':<10}")
    print("-" * 80)
    for d in res["district_forecasts"][:10]:
        p50 = d["heavy_rain_probabilities"].get("p_gt_50mm", 0.0)
        print(f"{d['name']:<20} | {d['state']:<15} | {d['raw_nwp_rainfall_mm']:<8.1f} | {d['corrected_rainfall_mm']:<9.1f} | {p50:<8.2f} | {d['risk_category']:<10}")


if __name__ == "__main__":
    scenario = sys.argv[1] if len(sys.argv) > 1 else "ACTIVE_MONSOON"
    main(scenario)
