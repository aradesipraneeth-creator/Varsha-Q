"""
Unit tests for the Quantum-Inspired Optimization Engine
"""
import numpy as np
import pytest
from backend.app.optimization.quantum_annealer import (
    QUBOFeatureSelector,
    SimulatedQuantumAnnealer,
    ClassicalSimulatedAnnealer,
)
from backend.app.optimization.qubo_optimizer import (
    QuantumInspiredEvolutionaryOptimizer,
    run_benchmark_optimization,
)

def test_qubo_matrix_construction():
    features = ["nwp_rain", "lag1_rain", "humidity", "wind_u", "elevation"]
    errors = np.array([4.2, 5.1, 7.8, 8.5, 9.0])
    corr = np.eye(5)
    corr[0, 1] = corr[1, 0] = 0.8  # Strong correlation between rain and lag

    selector = QUBOFeatureSelector(features, lambda_sparsity=0.05, lambda_redundancy=0.2)
    Q = selector.build_qubo_matrix(errors, corr)

    assert Q.shape == (5, 5)
    assert Q[0, 1] > 0.1  # Collinear penalty present
    assert Q[0, 0] < Q[4, 4]  # Lower error feature has lower diagonal penalty

def test_simulated_quantum_annealer():
    # Simple 4-variable problem
    Q = np.array([
        [-2.0,  1.5,  0.2,  0.1],
        [ 1.5, -1.8,  0.5,  0.0],
        [ 0.2,  0.5, -0.9,  0.2],
        [ 0.1,  0.0,  0.2, -0.4]
    ])
    sqa = SimulatedQuantumAnnealer(Q, num_trotter_replicas=4, num_sweeps=50, random_seed=42)
    res = sqa.solve()

    assert res["optimizer"] == "Simulated Quantum Annealing (SQA)"
    assert len(res["selected_bits"]) == 4
    assert sum(res["selected_bits"]) >= 1
    assert "best_energy" in res
    assert "runtime_ms" in res
    assert len(res["convergence_history"]) > 0

def test_classical_simulated_annealer():
    Q = np.array([
        [-2.0, 1.5],
        [ 1.5, -1.8]
    ])
    csa = ClassicalSimulatedAnnealer(Q, num_iterations=40, random_seed=42)
    res = csa.solve()

    assert res["optimizer"] == "Classical Simulated Annealing (CSA)"
    assert len(res["selected_bits"]) == 2
    assert sum(res["selected_bits"]) >= 1

def test_benchmark_comparison():
    features = ["f1", "f2", "f3", "f4"]
    errors = np.array([3.0, 3.5, 6.0, 7.0])
    corr = np.eye(4)
    benchmark = run_benchmark_optimization(features, errors, corr)

    assert "classical_baseline" in benchmark
    assert "quantum_inspired" in benchmark
    assert len(benchmark["quantum_inspired"]["selected_features"]) > 0
    assert len(benchmark["classical_baseline"]["selected_features"]) > 0
