"""
VARSHA-Q Scientific Evaluation Runner (evaluate.py)
Generates comprehensive verification evaluation reports comparing Raw NWP vs VARSHA-Q across all regimes.
"""
import sys
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from backend.app.services.verification_service import verification_service


def main():
    print("=" * 60)
    print("VARSHA-Q: SCIENTIFIC VERIFICATION EVALUATION")
    print("=" * 60)

    results = verification_service.evaluate_all_regimes()
    overall = results["overall"]
    print("\nOVERALL EVALUATION RESULTS:")
    print(f"Total Evaluation Samples: {overall['total_samples']}")
    print(f"Raw NWP RMSE:   {overall['raw_nwp_rmse']:.2f} mm")
    print(f"VARSHA-Q RMSE:  {overall['corrected_rmse']:.2f} mm")
    print(f"RMSE Reduction: {overall['rmse_reduction_pct']}%")
    print(f"CSI @ 25mm:     {overall['csi_25']:.3f}")
    print(f"POD @ 25mm:     {overall['pod_25']:.3f}")
    print(f"FAR @ 25mm:     {overall['far_25']:.3f}")
    print(f"ETS @ 25mm:     {overall['ets_25']:.3f}")
    print(f"FSS @ 25mm:     {overall['fss_25']:.3f}")

    print("\nREGIME-WISE BREAKDOWN:")
    print(f"{'Regime':<20} | {'Samples':<7} | {'Raw RMSE':<9} | {'Corr RMSE':<9} | {'Red %':<6} | {'CSI':<5} | {'FSS':<5}")
    print("-" * 75)
    for r in results["regime_wise"]:
        print(f"{r['title']:<20} | {r['sample_count']:<7} | {r['raw_rmse']:<9.2f} | {r['corrected_rmse']:<9.2f} | {r['rmse_reduction_pct']:<6.1f} | {r['csi_25']:<5.3f} | {r['fss_25']:<5.3f}")

    out_json = BASE_DIR / "reports" / "verification_evaluation.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved evaluation metrics to {out_json}")


if __name__ == "__main__":
    main()
