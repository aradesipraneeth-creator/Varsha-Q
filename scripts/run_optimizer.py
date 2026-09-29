"""
VARSHA-Q Optimization Runner (run_optimizer.py)
Benchmarks Classical Simulated Annealing vs Simulated Quantum Annealing on feature selection QUBO.
"""
import sys
from pathlib import Path
import numpy as np

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from backend.app.optimization.qubo_optimizer import run_benchmark_optimization


def main():
    print("=" * 65)
    print("VARSHA-Q: QUANTUM-INSPIRED OPTIMIZATION BENCHMARK")
    print("Objective: QUBO Binary Feature Selection for Forecast Bias Correction")
    print("=" * 65)

    features = [
        "nwp_rainfall",
        "lag1_rainfall",
        "relative_humidity",
        "surface_pressure_anomaly",
        "moisture_convergence",
        "terrain_elevation",
        "coastal_distance",
        "monsoon_phase"
    ]
    errors = np.array([3.8, 4.9, 6.7, 7.5, 5.9, 7.1, 7.8, 8.4])
    corr = np.eye(len(features))
    corr[0, 1] = corr[1, 0] = 0.75
    corr[2, 4] = corr[4, 2] = 0.68

    res = run_benchmark_optimization(features, errors, corr)

    print(f"\nOptimization Results:")
    print(f"Classical Baseline (CSA): Energy = {res['classical_baseline']['objective_energy']:.4f}, Runtime = {res['classical_baseline']['runtime_ms']} ms")
    print(f"Selected ({res['classical_baseline']['num_selected']}): {', '.join(res['classical_baseline']['selected_features'])}")

    print(f"\nQuantum-Inspired (SQA):  Energy = {res['quantum_inspired']['objective_energy']:.4f}, Runtime = {res['quantum_inspired']['runtime_ms']} ms")
    print(f"Selected ({res['quantum_inspired']['num_selected']}): {', '.join(res['quantum_inspired']['selected_features'])}")

    print(f"\nEnergy Difference: {res['energy_delta']:+0.4f}")
    print(f"Scientific Disclaimer: {res['scientific_disclaimer']}")


if __name__ == "__main__":
    main()
