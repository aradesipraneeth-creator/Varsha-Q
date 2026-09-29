# VARSHA-Q System Architecture

**Project:** VARSHA-Q  
**Subtitle:** Quantum-Inspired Spatiotemporal AI for Regime-Aware Rainfall Forecast Correction  
**Team:** QUANTUM LEAPERS  

---

## 1. High-Level Architecture Diagram

```mermaid
flowchart TD
    subgraph Data Sources
        A1[NWP Forecasts: GFS / ECMWF]
        A2[Observational Data: IMD AWS / Rain Gauges / Satellite]
        A3[Terrain Rasters: SRTM 30m Elevation & Slope]
    end

    subgraph Data Processing
        B1[Data Alignment & QA Engine]
        B2[Spatiotemporal Feature Engineering]
    end

    subgraph Spatiotemporal Representation
        C1[LNN Temporal Dynamics: Continuous-Time ODE]
        C2[GNN Spatial Modeling: District Graph Convolution]
        C3[Gated Spatiotemporal Fusion Layer]
    end

    subgraph Regime-Aware Post-Processing
        D1[Weather Regime Classifier: Active / Break / Depression / Coastal / Orographic]
        D2[Regime-Specific Bias Correction Models: Delta = Obs - NWP]
        D3[Global Fallback Estimator: Automatic Degradation Safety]
    end

    subgraph Optimization Layer
        E1[QUBO Feature Selection Formulation]
        E2[Simulated Quantum Annealing: SQA with Trotter Replicas]
        E3[Classical Simulated Annealing Baseline]
    end

    subgraph Probabilistic & Verification Output
        F1[Heteroscedastic Exceedance Probabilities: P > 15, 25, 50, 100mm]
        F2[Quantile Uncertainty Bounds: P10 / P50 / P90]
        F3[Verification Engine: RMSE, CSI, POD, FAR, ETS, Spatial FSS]
    end

    subgraph User Experience
        G1[FastAPI High-Performance REST API]
        G2[Real-Time WebSocket Streaming Engine]
        G3[Editorial Scientific Web Application: React + Vite + Leaflet]
    end

    A1 --> B1
    A2 --> B1
    A3 --> B1
    B1 --> B2
    B2 --> C1
    B2 --> C2
    C1 --> C3
    C2 --> C3
    B2 --> D1
    D1 --> D2
    C3 --> D2
    D2 -.-> D3
    B2 --> E1
    E1 --> E2
    E1 --> E3
    E2 --> D2
    D2 --> F1
    D2 --> F2
    D2 --> F3
    F1 --> G1
    F2 --> G1
    F3 --> G1
    G1 --> G3
    G2 <--> G3
```

---

## 2. Directory Structure

```
varsha-q/
│
├── backend/
│   ├── app/
│   │   ├── api/             # REST endpoints & WebSocket streams
│   │   ├── core/            # Database engine & environment configurations
│   │   ├── models/          # SQLAlchemy async database models
│   │   ├── schemas/         # Pydantic request/response validation schemas
│   │   ├── services/        # Orchestration services (Forecast, District, Verification)
│   │   ├── data/            # Data providers (IMD, Open-Meteo, Demo, File) & Alignment
│   │   ├── ml/              # LNN ODE, Spatial GNN, Fusion, Regime Classifier, Bias Correction
│   │   ├── optimization/    # QUBO matrix builder, SQA Trotter annealer, CSA baseline, QEA
│   │   └── verification/    # Continuous RMSE/MAE, Categorical CSI/POD/FAR/ETS, Spatial FSS
│   └── tests/
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── components/      # Editorial Navbar, Hero, Forecast, Regimes, Map, Verification, Modal
│   │   ├── services/        # Frontend API client
│   │   └── types/           # TypeScript data interfaces
│
├── data/
│   ├── demo/                # Synthetic multi-regime replay scenarios
│   ├── geo/                 # India district GeoJSON & topographic metadata
│   └── raw/                 # Uploaded research datasets
│
├── models/                  # Checkpoints: regime_classifier.pkl, bias_correction.pkl, weights.pt
├── configs/                 # Hyperparameters (train.yaml)
├── scripts/                 # Standalone reproducible CLI tools (train_all.py, run_demo.py, etc.)
├── reports/                 # Empirical validation reports & training summaries
├── tests/                   # Full pytest suite (22 unit & integration tests)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## 3. Graceful Failure & Offline Reliability

1. **Live Feed Disconnection:** If Open-Meteo or IMD servers are unreachable or encounter network timeouts, the system transitions gracefully to the synchronized `DemoProvider` replay dataset without throwing unhandled exceptions.
2. **Missing Checkpoints:** If a specialized regime model has insufficient training samples, the pipeline automatically routes inference through the global fallback model, signaling `"Regime-specific model unavailable -> global fallback"`.
3. **Hardware Agnosticism:** Automatic PyTorch device detection routes tensor operations to CUDA GPUs if present, or degrades cleanly to multi-threaded CPU execution.
