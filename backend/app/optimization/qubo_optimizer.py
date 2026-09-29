"""
VARSHA-Q Quantum-Inspired Evolutionary Optimizer (QEA) & Pipeline Integration
Implements Q-bit amplitude representation and quantum rotation gates for multi-parameter continuous/discrete search.
"""
import time
import math
import numpy as np
from typing import Dict, Any, List, Optional, Callable
from .quantum_annealer import QUBOFeatureSelector, SimulatedQuantumAnnealer, ClassicalSimulatedAnnealer


class QuantumInspiredEvolutionaryOptimizer:
    """
    Quantum-Inspired Evolutionary Algorithm (QEA) for model parameter and loss weight tuning.
    Each individual is represented by a string of Q-bits:
    q_i = [alpha_i, beta_i]^T, where |alpha_i|^2 + |beta_i|^2 = 1.
    alpha_i is probability amplitude for 0, beta_i for 1.
    Updated via quantum rotation gate:
    [alpha'; beta'] = [cos(theta) -sin(theta); sin(theta) cos(theta)] * [alpha; beta]
    """
    def __init__(
        self,
        param_bounds: List[Tuple[float, float]],
        param_names: List[str],
        bits_per_param: int = 8,
        population_size: int = 12,
        generations: int = 35,
        rotation_angle_base: float = 0.05 * math.pi,
        random_seed: Optional[int] = 42
    ):
        self.bounds = param_bounds
        self.param_names = param_names
        self.num_params = len(param_bounds)
        self.bits_per_param = bits_per_param
        self.total_bits = self.num_params * self.bits_per_param
        self.pop_size = population_size
        self.generations = generations
        self.rot_base = rotation_angle_base
        self.rng = np.random.default_rng(random_seed)

    def _decode_individual(self, bitstring: np.ndarray) -> np.ndarray:
        """Decodes binary string into continuous parameter vector within bounds."""
        params = []
        for i, (low, high) in enumerate(self.bounds):
            chunk = bitstring[i * self.bits_per_param : (i + 1) * self.bits_per_param]
            # Convert binary chunk to integer in [0, 2^B - 1]
            val_int = 0
            for bit in chunk:
                val_int = (val_int << 1) | int(bit)
            max_int = (1 << self.bits_per_param) - 1
            scaled = low + (high - low) * (val_int / max_int)
            params.append(scaled)
        return np.array(params, dtype=np.float64)

    def optimize(self, objective_func: Callable[[np.ndarray], float]) -> Dict[str, Any]:
        """
        Minimizes objective_func(params).
        Returns best parameters, objective, and convergence history.
        """
        start_time = time.perf_counter()

        # Initialize population of Q-bits with equal superposition alpha = beta = 1/sqrt(2)
        # Shape: (pop_size, total_bits, 2)
        q_pop = np.full((self.pop_size, self.total_bits, 2), 1.0 / math.sqrt(2.0), dtype=np.float64)

        best_params = None
        best_obj = float("inf")
        best_binary = None
        history = []

        for gen in range(self.generations):
            # Step 1: Collapse Q-bits into classical binary states via observation: P(1) = |beta|^2
            binary_pop = np.zeros((self.pop_size, self.total_bits), dtype=int)
            scores = np.zeros(self.pop_size, dtype=np.float64)
            param_pop = []

            for p in range(self.pop_size):
                prob_one = q_pop[p, :, 1] ** 2
                rand_vals = self.rng.random(self.total_bits)
                binary_pop[p] = (rand_vals < prob_one).astype(int)
                
                params = self._decode_individual(binary_pop[p])
                param_pop.append(params)
                scores[p] = objective_func(params)

                if scores[p] < best_obj:
                    best_obj = scores[p]
                    best_params = params.copy()
                    best_binary = binary_pop[p].copy()

            # Step 2: Update Q-bits using quantum rotation gates guided by the best found individual
            gen_best_idx = int(np.argmin(scores))
            target_binary = best_binary if best_binary is not None else binary_pop[gen_best_idx]

            for p in range(self.pop_size):
                for b in range(self.total_bits):
                    x_pb = binary_pop[p, b]
                    x_tb = target_binary[b]
                    
                    # Direction of rotation towards target state
                    if x_pb == 0 and x_tb == 1:
                        # Rotate towards state 1
                        theta = self.rot_base
                    elif x_pb == 1 and x_tb == 0:
                        # Rotate towards state 0
                        theta = -self.rot_base
                    else:
                        theta = 0.0

                    if theta != 0.0:
                        cos_t = math.cos(theta)
                        sin_t = math.sin(theta)
                        a = q_pop[p, b, 0]
                        beta = q_pop[p, b, 1]
                        q_pop[p, b, 0] = cos_t * a - sin_t * beta
                        q_pop[p, b, 1] = sin_t * a + cos_t * beta

            history.append({
                "generation": gen + 1,
                "best_objective": round(float(best_obj), 4),
                "mean_objective": round(float(np.mean(scores)), 4)
            })

        runtime_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        
        result_params = {
            self.param_names[i]: round(float(best_params[i]), 4)
            for i in range(self.num_params)
        }

        return {
            "optimizer": "Quantum-Inspired Evolutionary Algorithm (QEA)",
            "optimized_parameters": result_params,
            "best_objective": round(float(best_obj), 4),
            "runtime_ms": runtime_ms,
            "generations": self.generations,
            "population_size": self.pop_size,
            "history": history
        }


def run_benchmark_optimization(
    feature_names: List[str], 
    feature_errors: np.ndarray, 
    feature_correlations: np.ndarray
) -> Dict[str, Any]:
    """
    Executes a side-by-side benchmark comparing:
    1. Classical Simulated Annealing (Baseline)
    2. Simulated Quantum Annealing (Quantum-Inspired)
    """
    selector = QUBOFeatureSelector(feature_names, lambda_sparsity=0.08, lambda_redundancy=0.15)
    Q = selector.build_qubo_matrix(feature_errors, feature_correlations)

    csa = ClassicalSimulatedAnnealer(Q, num_iterations=120, random_seed=42)
    csa_result = csa.solve()

    sqa = SimulatedQuantumAnnealer(Q, num_trotter_replicas=8, num_sweeps=120, random_seed=42)
    sqa_result = sqa.solve()

    # Map selected bits to feature names
    csa_selected = [feature_names[i] for i, bit in enumerate(csa_result["selected_bits"]) if bit == 1]
    sqa_selected = [feature_names[i] for i, bit in enumerate(sqa_result["selected_bits"]) if bit == 1]

    # Calculate real objective improvement (never fabricate)
    csa_energy = csa_result["best_energy"]
    sqa_energy = sqa_result["best_energy"]
    diff = csa_energy - sqa_energy

    return {
        "status": "COMPLETED",
        "scientific_disclaimer": "Experimental optimization result on classical simulation. Does not claim quantum supremacy.",
        "classical_baseline": {
            "name": "Classical Simulated Annealing (CSA)",
            "objective_energy": csa_energy,
            "selected_features": csa_selected,
            "num_selected": len(csa_selected),
            "runtime_ms": csa_result["runtime_ms"],
            "convergence": csa_result["convergence_history"]
        },
        "quantum_inspired": {
            "name": "Simulated Quantum Annealing (SQA with Trotter Replicas)",
            "objective_energy": sqa_energy,
            "selected_features": sqa_selected,
            "num_selected": len(sqa_selected),
            "runtime_ms": sqa_result["runtime_ms"],
            "convergence": sqa_result["convergence_history"]
        },
        "energy_delta": round(float(diff), 5),
        "qubo_dimension": len(feature_names)
    }
