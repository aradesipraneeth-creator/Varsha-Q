# VARSHA-Q: Quantum-Inspired Optimization Architecture

**Document:** Mathematical Formulation and Boundary Definitions of Quantum-Inspired Search  
**Target:** Feature Selection & Forecast Configuration Optimization  
**Team:** QUANTUM LEAPERS  

---

## 1. Critical Scientific Positioning

> [!IMPORTANT]
> **Quantum computing does NOT predict rainfall.**  
> Atmospheric thermodynamic equations and fluid dynamics are simulated using classical Numerical Weather Prediction (NWP) and machine learning models (Liquid Neural Networks & Graph Neural Networks).  
> **Quantum-inspired optimization is strictly a combinatorial search technique** for finding optimal predictor subsets and model hyperparameters.

VARSHA-Q does **not** claim:
- Quantum supremacy
- Quantum advantage
- Proven polynomial or exponential quantum speedup
- Requirement of physical quantum hardware

All quantum-inspired algorithms in VARSHA-Q run deterministically on **classical CPUs and GPUs** using simulated quantum tunneling dynamics.

---

## 2. What is Optimized?

In regime-conditioned rainfall post-processing, including irrelevant or collinear meteorological predictors degrades generalizeability and causes overfitting on rare heavy-rain tails.

VARSHA-Q optimizes a binary decision vector:

$$\mathbf{x} = [x_1, x_2, \dots, x_N]^T \in \{0, 1\}^N$$

where $x_i = 1$ indicates that predictor $i$ (e.g., NWP rainfall, moisture convergence, terrain slope, wind vorticity, or temporal lag) is selected, and $x_i = 0$ indicates exclusion.

---

## 3. Objective Function Formulation (QUBO)

The feature selection problem is mapped onto a Quadratic Unconstrained Binary Optimization (QUBO) Hamiltonian:

$$\min_{\mathbf{x} \in \{0, 1\}^N} E(\mathbf{x}) = \mathbf{x}^T Q \mathbf{x}$$

where the symmetric matrix $Q \in \mathbb{R}^{N \times N}$ is constructed from empirical validation statistics:

### 3.1. Diagonal Terms (Individual Feature Relevance & Regularization)
$$Q_{ii} = - \left( 1.0 - \frac{\text{RMSE}_i - \min(\text{RMSE})}{\max(\text{RMSE}) - \min(\text{RMSE})} \right) + \lambda_{\text{sparsity}}$$
- Features with lower individual validation RMSE have negative diagonal penalties, encouraging selection.
- $\lambda_{\text{sparsity}} > 0$ penalizes excessively large feature sets, favoring compact, interpretable models.

### 3.2. Off-Diagonal Terms (Collinear Redundancy Penalty)
$$Q_{ij} = \lambda_{\text{redundancy}} \cdot |\rho_{ij}|, \quad \forall i \ne j$$
- $\rho_{ij}$ is the Pearson correlation between feature $i$ and feature $j$.
- Penalizes simultaneous selection of highly correlated predictors (e.g., relative humidity and moisture convergence, or raw NWP and short-lag NWP).

---

## 4. Quantum-Inspired vs. Classical Baseline

| Dimension | Classical Simulated Annealing (CSA) | Simulated Quantum Annealing (SQA) |
|---|---|---|
| **Underlying Physics** | Thermal fluctuations (Metropolis-Hastings) | Quantum tunneling via Transverse-Field Ising Model |
| **State Representation** | Single spin configuration $\mathbf{\sigma} \in \{-1, +1\}^N$ | $P$ Trotter replicas interacting along imaginary time |
| **Barrier Crossing** | Must climb *over* energy barriers $\Delta E$ | Can tunnel *through* tall, narrow energy barriers |
| **Cooling Schedule** | Temperature $T(t) = T_0 \alpha^t \rightarrow 0$ | Transverse magnetic field $\Gamma(t) \rightarrow 0$ |
| **Coupling Parameter** | Thermal noise $k_B T$ | Inter-replica coupling $J_{\perp} = -\frac{T}{2} \ln(\tanh(\frac{\Gamma}{PT}))$ |

### 4.1. Suzuki-Trotter Hamiltonian
Through the Suzuki-Trotter transformation, the $d$-dimensional quantum transverse Ising system is mapped to a $(d+1)$-dimensional classical system with $P$ Trotter replicas:

$$H_{\text{eff}} = \sum_{k=1}^P \left[ \frac{1}{P} H_{\text{classical}}(\mathbf{\sigma}^{(k)}) - J_{\perp} \sum_{i=1}^N \sigma_i^{(k)} \sigma_i^{(k+1)} \right]$$

During early sweeps, high transverse field $\Gamma$ permits aggressive tunneling between distinct combinatorial topologies. As $\Gamma \rightarrow 0$, replicas collapse into an identical, low-energy classical configuration.

---

## 5. Empirical Evaluation Protocol

Both algorithms are executed over identical QUBO matrices with recorded:
1. **Initial Energy:** $E(\mathbf{x}_0)$
2. **Optimized Energy:** $E(\mathbf{x}^*)$
3. **Runtime in Milliseconds:** $t_{\text{exec}}$
4. **Selected Feature Subsets**
5. **Convergence History Curve**

If classical simulated annealing occasionally achieves equivalent or marginally better energy on small problem sizes ($N \le 8$), the system honestly displays the exact difference:
$$\text{"Energy Delta: } E_{\text{CSA}} - E_{\text{SQA}}\text{"}$$
Never fabricating an artificial "quantum advantage".
