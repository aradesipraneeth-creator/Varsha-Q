# VARSHA-Q: Scientific Methodology & Mathematical Formulations

**Project Title:** Quantum-Inspired Spatiotemporal AI for Regime-Aware Rainfall Forecast Correction  
**Problem Statement:** Smart India Hackathon 2026 — PS ID: 26080  
**Team:** QUANTUM LEAPERS  

---

## 1. Meteorological Context & Problem Formulation

Numerical Weather Prediction (NWP) models (e.g., GFS, NCUM, ECMWF IFS) are the foundation of operational meteorological forecasting in India. However, due to finite grid resolutions (typically 12 km to 25 km), parameterization of sub-grid cumulus convection, and smoothed digital elevation topography, raw NWP precipitation forecasts suffer from severe systematic errors:

1. **Convective Underprediction in the Central Monsoon Trough:** Deep mesoscale convective systems (MCS) produce extreme localized rainfall rates that coarse-grid hydrostatic models consistently smooth out.
2. **False-Alarm Orographic Leeward Smoothing:** Over the Western Ghats (e.g., Wayanad, Idukki, Mahabaleshwar) and Northeast India (Meghalaya Plateau), steep mountain barriers produce mechanical forced lifting. NWP models with smoothed terrain underestimate ridge-crest precipitation by 30% to 60%, while overestimating rainfall in the rain-shadow interior.
3. **Regime Non-Stationarity:** A single static statistical post-processing method (e.g., simple Model Output Statistics or linear regression) fails because NWP error structures are **regime-dependent**. During an *Active Monsoon*, NWP underpredicts heavy rainfall along the monsoon trough. During a *Break Monsoon*, the trough shifts to the Himalayan foothills, causing NWP models to erroneously forecast rain over the dry southern peninsula while missing the intense foothill rainfall.

---

## 2. Core Architectural Flow

```
NWP FORECAST + OBSERVATIONS + TERRAIN
                 ↓
      DATA ALIGNMENT & QA ENGINE
                 ↓
     SPATIOTEMPORAL FEATURE TENSORS
                 ↓
       WEATHER REGIME CLASSIFIER   (Crucial: Operates BEFORE correction!)
                 ↓
   REGIME-SPECIFIC BIAS CORRECTION   (Specialized models with Global Fallback)
                 ↓
    QUANTUM-INSPIRED OPTIMIZATION    (QUBO Feature & Parameter Tuning)
                 ↓
      CORRECTED RAINFALL FIELD
                 ↓
  HEAVY RAIN PROBABILITY & UNCERTAINTY  (P10/P50/P90 Quantile Bounds)
                 ↓
    DISTRICT DECISION INTELLIGENCE   (Model-Derived Threat Categories)
                 ↓
         VERIFICATION ENGINE         (RMSE, CSI, POD, FAR, ETS, FSS)
```

---

## 3. Spatiotemporal Neural Architectures

### 3.1. Liquid Neural Network (LNN) Temporal Dynamics
Traditional Recurrent Neural Networks (LSTM/GRU) operate in discrete, fixed clock steps and suffer from vanishing gradients over variable meteorological lead times. VARSHA-Q employs a continuous-time **Liquid Time-Constant (LTC) Neural Network** (Hasani et al., 2021).

The state trajectory $x(t) \in \mathbb{R}^{D_{temp}}$ evolves according to the non-linear ordinary differential equation (ODE):

$$\frac{dx(t)}{dt} = -\left[ \frac{1}{\tau} + f(x(t), u(t)) \right] x(t) + A \cdot f(x(t), u(t))$$

where:
- $\tau > 0$ is the base biophysical time constant,
- $u(t) \in \mathbb{R}^{D_{in}}$ is the incoming meteorological feature vector (precipitation, humidity, pressure anomaly, wind components),
- $f(x(t), u(t)) = \sigma(W_{in} u(t) + W_{rec} x(t) + b)$ is the dynamic synaptic conductance,
- $A$ is the reversal driving potential ceiling.

We discretize this ODE using a numerically stable semi-implicit Euler integration step:

$$x_{t+\Delta t} = \frac{x_t + \Delta t \cdot A \cdot f(x_t, u_t)}{1 + \Delta t \left( \frac{1}{\tau} + f(x_t, u_t) \right)}$$

This guarantees that the internal time constant shrinks during rapid convective onset (allowing fast adaptation) and expands during quiescent synoptic phases.

### 3.2. Graph Neural Network (GNN) Spatial Neighborhood
Meteorological processes do not respect arbitrary administrative boundaries. Districts form an undirected spatial graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$, where nodes $\mathcal{V}$ represent districts and edges $\mathcal{E}$ represent geographic adjacency and topographic continuity.

The spatial message passing layer is formulated as:

$$H^{(l+1)} = \text{LeakyReLU}\left( \tilde{D}^{-\frac{1}{2}} \tilde{A} \tilde{D}^{-\frac{1}{2}} H^{(l)} W^{(l)} + H^{(l)} W_{res} \right)$$

where $\tilde{A} = A + I_N$ is the adjacency matrix with self-loops, and $\tilde{D}_{ii} = \sum_j \tilde{A}_{ij}$ is the diagonal degree matrix. This allows elevation gradients and marine boundary fluxes from coastal districts to propagate smoothly into adjacent inland districts.

### 3.3. Joint Spatiotemporal Gated Fusion
To fuse the temporal representation $H_{temp} \in \mathbb{R}^{N \times 32}$ with the spatial embedding $H_{spat} \in \mathbb{R}^{N \times 32}$, VARSHA-Q employs an adaptive gating mechanism:

$$G = \sigma\left( W_g [H_{temp} \,\|\, H_{spat}] + b_g \right) \in (0, 1)^{N \times 32}$$

$$Z_{ST} = \text{LayerNorm}\left( G \odot \text{Proj}_{temp}(H_{temp}) + (1 - G) \odot \text{Proj}_{spat}(H_{spat}) \right)$$

---

## 4. Weather Regime Classification

The synoptic classifier identifies 5 principal meteorological regimes over India:
1. `ACTIVE_MONSOON`: Low-pressure trough across central India, sustained moisture convergence, widespread heavy rain.
2. `BREAK_MONSOON`: Trough shifts northwards to the Himalayan foothills; peninsular rainfall suppressed.
3. `DEPRESSION_LOW`: Intense cyclonic vortex originating in the Bay of Bengal/Arabian Sea with concentrated torrential core precipitation.
4. `COASTAL`: Strong marine-land boundary interaction, diurnal sea-breeze convection lines.
5. `OROGRAPHIC`: Mechanical forced lifting along Western Ghats and Meghalaya Plateau.

The classifier is calibrated using Platt scaling / isotonic calibration to output true probability distributions:

$$P(\text{Regime} = k \mid \mathbf{x}_{synoptic}) \in [0, 1], \quad \sum_{k=1}^K P(k) = 1$$

---

## 5. Regime-Specific Bias Correction

The target variable for bias correction is defined strictly as systematic NWP error:

$$\Delta y_i = y_i^{\text{Observed}} - y_i^{\text{NWP}}$$

Individual gradient boosted regressors are trained per regime:

$$\hat{y}_i^{\text{Corrected}} = \max\left( 0.0, \, y_i^{\text{NWP}} + \hat{\Delta y}_i^{(k)} \right)$$

If an unrecognized regime or insufficient training samples occur, the system automatically falls back to a global bias correction estimator:
$$\text{"Regime-specific model unavailable} \rightarrow \text{global fallback"}$$

---

## 6. Heavy Rain Probability & Quantile Uncertainty

Precipitation is non-negative and heavily right-skewed. VARSHA-Q models conditional rainfall distribution using a heteroscedastic log-normal survival model:

$$\ln(R) \sim \mathcal{N}(\mu, \sigma^2)$$

Exceedance probability for operational threshold $T \in \{15, 25, 50, 100, 150\} \text{ mm}$ is calculated as:

$$P(R > T) = 1 - \Phi\left( \frac{\ln(T) - \ln(\hat{y}^{\text{Corrected}})}{\sigma_{\text{regime}}} \right)$$

Uncertainty intervals are derived analytically:
- **P10 (Lower Bound):** $\hat{y} \cdot \exp(-1.282 \cdot \sigma)$
- **P50 (Median Forecast):** $\hat{y}$
- **P90 (Upper Bound):** $\hat{y} \cdot \exp(+1.282 \cdot \sigma)$

---

## 7. Verification Metrics Engine

### 7.1. Continuous Error Metrics
- **Root Mean Squared Error (RMSE):**
  $$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^N (f_i - o_i)^2}$$
- **Mean Absolute Error (MAE):**
  $$\text{MAE} = \frac{1}{N} \sum_{i=1}^N |f_i - o_i|$$

### 7.2. Categorical Contingency Metrics (Threshold $T \ge 25 \text{ mm}$)
From a $2 \times 2$ contingency table with Hits ($a$), False Alarms ($b$), Misses ($c$), and Correct Negatives ($d$):
- **Probability of Detection (Hit Rate):**
  $$\text{POD} = \frac{a}{a + c}$$
- **False Alarm Ratio:**
  $$\text{FAR} = \frac{b}{a + b}$$
- **Critical Success Index (Threat Score):**
  $$\text{CSI} = \frac{a}{a + b + c}$$
- **Equitable Threat Score (ETS):**
  $$\text{ETS} = \frac{a - a_{\text{ref}}}{a + b + c - a_{\text{ref}}}, \quad a_{\text{ref}} = \frac{(a + b)(a + c)}{N_{\text{total}}}$$

### 7.3. Spatial Fractions Skill Score (FSS)
Evaluates spatial pattern placement within sliding neighborhood boxes:
$$\text{FSS} = 1 - \frac{\text{MSE}}{\text{MSE}_{\text{ref}}} = 1 - \frac{\sum (P_{\text{fct}} - P_{\text{obs}})^2}{\sum P_{\text{fct}}^2 + \sum P_{\text{obs}}^2}$$
