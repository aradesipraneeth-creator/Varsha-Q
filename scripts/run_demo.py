"""
VARSHA-Q Standalone Offline Demonstration Script (run_demo.py)
Executes the full pipeline end-to-end on CPU without requiring internet, GPU, or paid APIs:
1. Loads demonstration meteorological dataset
2. Aligns and normalizes spatiotemporal fields
3. Classifies weather regime (BEFORE correction)
4. Executes Continuous-Time LNN + Spatial GNN spatiotemporal representation
5. Runs regime-specific bias correction
6. Benchmarks Quantum-Inspired Optimization vs Classical Simulated Annealing
7. Estimates heavy rain exceedance probabilities and quantile uncertainty intervals
8. Computes full verification suite (Continuous RMSE + Categorical CSI/POD/FAR/ETS + Spatial FSS)
9. Displays a clear summary to console and writes artifacts to reports/
"""
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

import numpy as np
from backend.app.data.demo_provider import DemoProvider
from backend.app.ml.pipeline import VarshaQPipeline
from backend.app.optimization.qubo_optimizer import run_benchmark_optimization
from backend.app.verification.metrics import calculate_full_verification_suite


def run_demo(scenario: str = "OROGRAPHIC"):
    print("=" * 70)
    print(f"VARSHA-Q: OFFLINE DEMONSTRATION RUN (Scenario: {scenario})")
    print("Full Title: Quantum-Inspired Spatiotemporal AI for Regime-Aware Rainfall")
    print("Team: QUANTUM LEAPERS | Problem Statement: SIH PS 26080")
    print("=" * 70)

    # 1. Load Demo Data
    print("\n[Stage 1/7] Ingesting Demonstration Dataset...")
    provider = DemoProvider(random_seed=42)
    demo_data = provider.generate_scenario_data(regime=scenario, seed=123)
    districts = demo_data["districts"]
    n_districts = len(districts)
    print(f"Ingested {n_districts} Indian districts across 6 synoptic states.")
    print("Provenance: SYNTHETIC DEMONSTRATION DATA / REPLAY. Offline Mode.")

    # 2. Initialize ML Pipeline
    print("\n[Stage 2/7] Initializing Spatiotemporal AI Pipeline (LNN + GNN)...")
    pipeline = VarshaQPipeline(models_dir=BASE_DIR / "models")
    print(f"Execution Device: {pipeline.device}")

    # 3. Execute End-to-End Pipeline
    print("\n[Stage 3/7] Running Forward Pass:")
    print(" - Continuous-Time Liquid Neural Network (LNN) Temporal Dynamics")
    print(" - Spatial Graph Neural Network (GNN) Message Passing")
    print(" - Spatiotemporal Gated Fusion Layer")
    print(" - Weather Regime Classification (BEFORE correction)")
    print(" - Regime-Specific Bias Correction Model")

    res = pipeline.run_inference(
        synoptic_features=demo_data["synoptic_features"],
        district_spatial_features=demo_data["spatial_features"],
        district_temporal_seq=demo_data["temporal_sequences"],
        adjacency_matrix=demo_data["adjacency_matrix"],
        raw_nwp_rainfall=demo_data["raw_nwp_rainfall"],
        districts_meta=districts,
        observed_rainfall=demo_data["observed_rainfall"],
        forced_regime=scenario
    )

    regime_info = res["regime_intelligence"]
    print(f"\n >>> CLASSIFIED REGIME: {regime_info['regime']} (Confidence: {regime_info['confidence']*100:.1f}%)")
    print(f"     Title: {regime_info['title']}")
    print(f"     Key Indicators: {', '.join(regime_info['key_indicators'])}")

    corr_summary = res["correction_summary"]
    print(f"\n >>> BIAS CORRECTION STRATEGY: {corr_summary['strategy']}")
    print(f"     Mean Raw NWP: {corr_summary['mean_nwp_mm']} mm | Mean Corrected: {corr_summary['mean_corrected_mm']} mm")
    print(f"     Mean Correction Delta: {corr_summary['mean_delta_mm']:+0.2f} mm")

    # 4. Quantum-Inspired Optimization Benchmark
    print("\n[Stage 4/7] Benchmarking Quantum-Inspired Optimization vs Classical Baseline...")
    feature_names = [
        "nwp_rainfall", "lag1_rainfall", "relative_humidity", "surface_pressure",
        "wind_convergence", "terrain_elevation", "coastal_distance", "monsoon_phase"
    ]
    errors = np.array([4.1, 5.2, 7.3, 8.1, 6.4, 7.9, 8.5, 9.2])
    corr_mat = np.eye(len(feature_names))
    corr_mat[0, 1] = corr_mat[1, 0] = 0.78
    corr_mat[2, 4] = corr_mat[4, 2] = 0.65

    opt_res = run_benchmark_optimization(feature_names, errors, corr_mat)
    csa = opt_res["classical_baseline"]
    sqa = opt_res["quantum_inspired"]

    print(f" - Classical Simulated Annealing: Best Energy = {csa['objective_energy']:.4f} in {csa['runtime_ms']} ms")
    print(f" - Simulated Quantum Annealing:   Best Energy = {sqa['objective_energy']:.4f} in {sqa['runtime_ms']} ms")
    print(f" - SQA Selected Features ({len(sqa['selected_features'])}): {', '.join(sqa['selected_features'])}")
    print(f" - Energy Improvement (Delta): {opt_res['energy_delta']:+0.4f}")
    print(f" - Scientific Disclaimer: {opt_res['scientific_disclaimer']}")

    # 5. Heavy Rain Probability & Quantile Uncertainty
    print("\n[Stage 5/7] Estimating Heavy-Rain Probabilities & Uncertainty Bounds...")
    sample_district = res["district_forecasts"][0]
    print(f"Sample District: {sample_district['name']} ({sample_district['state']})")
    print(f" - Raw NWP: {sample_district['raw_nwp_rainfall_mm']} mm -> Corrected: {sample_district['corrected_rainfall_mm']} mm")
    print(f" - P10 Lower: {sample_district['uncertainty']['lower_bound_p10_mm']} mm | P90 Upper: {sample_district['uncertainty']['upper_bound_p90_mm']} mm")
    print(f" - Uncertainty Level: {sample_district['uncertainty']['uncertainty_level']}")
    print(f" - Exceedance: P(>25mm)={sample_district['heavy_rain_probabilities']['p_gt_25mm']:.2f}, P(>50mm)={sample_district['heavy_rain_probabilities']['p_gt_50mm']:.2f}, P(>100mm)={sample_district['heavy_rain_probabilities']['p_gt_100mm']:.2f}")
    print(f" - Risk Category: {sample_district['risk_category']} [{sample_district['risk_label']}]")

    # 6. Verification Engine
    print("\n[Stage 6/7] Scientific Verification against Ground Truth Observations...")
    ver = res["verification"]
    c_raw = ver["continuous"]["raw_nwp"]
    c_cor = ver["continuous"]["corrected"]
    red = ver["continuous"]["rmse_reduction_pct"]
    print(f"Continuous Verification (mm):")
    print(f" - Raw NWP RMSE:   {c_raw['rmse']} mm | MAE: {c_raw['mae']} mm | Bias: {c_raw['bias']:+0.2f} mm")
    print(f" - Corrected RMSE: {c_cor['rmse']} mm | MAE: {c_cor['mae']} mm | Bias: {c_cor['bias']:+0.2f} mm")
    print(f" - RMSE Reduction: {red}%")

    print("\nThreshold Verification @ 25mm:")
    t25 = ver["thresholds"]["25mm"]
    print(f" - Raw NWP:   CSI = {t25['raw_nwp']['csi']:.3f} | POD = {t25['raw_nwp']['pod']:.3f} | FAR = {t25['raw_nwp']['far']:.3f} | ETS = {t25['raw_nwp']['ets']:.3f} | FSS = {t25['fss']['raw_nwp']:.3f}")
    print(f" - Corrected: CSI = {t25['corrected']['csi']:.3f} | POD = {t25['corrected']['pod']:.3f} | FAR = {t25['corrected']['far']:.3f} | ETS = {t25['corrected']['ets']:.3f} | FSS = {t25['fss']['corrected']:.3f}")

    # 7. Write Demo Output Artifact
    print("\n[Stage 7/7] Generating Demonstration Summary Artifact...")
    reports_dir = BASE_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    out_file = reports_dir / f"demo_result_{scenario.lower()}.txt"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"VARSHA-Q Demonstration Run Output\n")
        f.write(f"Scenario: {scenario}\n")
        f.write(f"Regime: {regime_info['regime']} (Confidence: {regime_info['confidence']})\n")
        f.write(f"Raw NWP RMSE: {c_raw['rmse']} mm -> Corrected RMSE: {c_cor['rmse']} mm ({red}% reduction)\n")
        f.write(f"CSI @ 25mm: {t25['corrected']['csi']:.3f}\n")
        f.write(f"Simulated Quantum Annealing Energy Delta: {opt_res['energy_delta']:+0.4f}\n")
    print(f"Demonstration artifact saved to {out_file}")

    print("\n" + "=" * 70)
    print("DEMO EXECUTION COMPLETED SUCCESSFULLY WITH ZERO ERRORS.")
    print("=" * 70)


if __name__ == "__main__":
    scenario = sys.argv[1] if len(sys.argv) > 1 else "OROGRAPHIC"
    run_demo(scenario)
