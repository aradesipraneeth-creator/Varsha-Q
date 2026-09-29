# VARSHA-Q Model Card

**Model Family:** VARSHA-Q Spatiotemporal Meteorological Ensemble  
**Developer:** Team QUANTUM LEAPERS  
**License:** MIT License  

---

## 1. Model Details

### 1.1. Weather Regime Classifier
- **Model Type:** Balanced Calibrated Random Forest Classifier
- **Input Features:** 10 synoptic variables (mean rain, max rain, moisture convergence, relative humidity, surface pressure anomaly, wind speed, 850 hPa vorticity, mean elevation, slope, coastal proximity)
- **Target Output:** 6 discrete regimes (`ACTIVE_MONSOON`, `BREAK_MONSOON`, `DEPRESSION_LOW`, `COASTAL`, `OROGRAPHIC`, `UNKNOWN_TRANSITION`) with calibrated posterior probabilities.
- **Intended Use:** Synoptic regime pre-classification operating *prior* to bias correction.

### 1.2. Liquid Neural Network (LNN) Temporal Dynamics
- **Model Type:** Multi-layer Liquid Time-Constant (LTC) continuous-time network
- **Architecture:** 2 liquid layers, 32 hidden dimensions, semi-implicit Euler integration ($\Delta t = 0.5$)
- **Input Dimensions:** $(N_{\text{districts}}, 6, 8)$ sequence tensor
- **Role:** Captures evolving non-linear memory and precipitation onset rates.

### 1.3. Graph Neural Network (GNN) Spatial Modeling
- **Model Type:** Symmetric Normalized Graph Convolution with residual skip connections
- **Architecture:** 2 layers, 32 hidden dimensions, LeakyReLU activation, LayerNorm
- **Graph Topology:** 37 node districts, spatial adjacency and topographic continuity edges
- **Role:** Propagates terrain elevation lifting and marine moisture boundaries across neighborhoods.

### 1.4. Regime-Specific Bias Correction Models
- **Model Type:** Regime-conditioned Gradient Boosted Regressors + Global Fallback
- **Target:** Systematic error offset: $\Delta = y_{\text{Observed}} - y_{\text{NWP}}$
- **Physical Constraint:** Output clamped at $\hat{y} \ge 0.0 \text{ mm}$ (no negative rain).

---

## 2. Evaluation Summary

Empirical held-out verification across 5 standard regimes (from `reports/training_summary.md`):

| Regime | Raw NWP RMSE (mm) | VARSHA-Q RMSE (mm) | RMSE Reduction | CSI (> 25mm) |
|---|---|---|---|---|
| **Active Monsoon** | 33.27 | 3.68 | **88.9%** | 1.000 |
| **Break Monsoon** | 15.73 | 1.43 | **90.9%** | 1.000 |
| **Depression / Low** | 21.76 | 5.32 | **75.6%** | 0.875 |
| **Coastal Rainfall** | 10.31 | 2.76 | **73.3%** | 1.000 |
| **Orographic Lifting** | 30.36 | 3.89 | **87.2%** | 0.818 |

---

## 3. Limitations & Ethical Positioning

1. **Research Prototype:** VARSHA-Q is an academic research prototype and not an operational meteorological agency. It must not supersede official warnings issued by the India Meteorological Department (IMD) or the National Disaster Management Authority (NDMA).
2. **Quantum Demystification:** Quantum-inspired search is strictly used for binary feature selection and hyperparameter tuning. No quantum supremacy or advantage is claimed.
