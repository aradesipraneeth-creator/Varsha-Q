# VARSHA-Q REST & WebSocket API Reference

**Project:** VARSHA-Q  
**Base URL:** `http://localhost:8000`  
**OpenAPI Interactive Docs:** `http://localhost:8000/docs`  
**Redoc:** `http://localhost:8000/redoc`  

---

## 1. System & Health Endpoints

### `GET /health`
Returns system liveness, device information, and active mode.
```json
{
  "status": "healthy",
  "service": "VARSHA-Q",
  "team": "QUANTUM LEAPERS",
  "mode": "DEMO",
  "device": "cpu",
  "timestamp": "2026-09-29T09:15:00Z"
}
```

### `GET /api/system/status`
Comprehensive operational status of all data pipelines, models, and checkpoints.

---

## 2. Forecast Endpoints

### `GET /api/forecast/latest`
Returns the most recent bias-corrected rainfall forecast, regime intelligence, and verification metrics.

### `GET /api/forecast/districts?state={state}`
Returns district-level forecasts, optionally filtered by state.

### `GET /api/forecast/district/{district_id}`
Returns granular telemetry for a single district including exceedance probabilities, uncertainty bounds, and physical attribution priors.

### `POST /api/inference/run?scenario={scenario}&mode={mode}`
Triggers an end-to-end forward pass for a chosen weather regime scenario (`ACTIVE_MONSOON`, `BREAK_MONSOON`, `DEPRESSION_LOW`, `COASTAL`, `OROGRAPHIC`) or live stream.

---

## 3. Weather Regime Endpoints

### `GET /api/regime/current`
Returns current synoptic regime, confidence, and key meteorological indicators.

### `GET /api/regimes`
Lists all supported meteorological regimes, synoptic definitions, and feature names.

---

## 4. Geospatial & Map Endpoints

### `GET /api/districts/geojson`
Returns official GeoJSON polygon boundaries and centroids for Indian districts.

---

## 5. Quantum-Inspired Optimization Endpoints

### `GET /api/optimization/latest`
Returns the latest benchmark comparison between Classical Simulated Annealing (CSA) and Simulated Quantum Annealing (SQA).

### `POST /api/optimization/run`
Executes an on-demand optimization benchmark over the meteorological feature QUBO Hamiltonian.

---

## 6. Scientific Verification Endpoints

### `GET /api/verification`
Returns multi-regime empirical verification metrics:
- Continuous: RMSE, MAE, Bias, Correlation
- Categorical: CSI, POD, FAR, ETS @ 25mm threshold
- Spatial: Fractions Skill Score (FSS)

### `GET /api/verification/regime`
Returns regime-wise performance breakdown.

---

## 7. Real-Time WebSocket Streaming

### `WS /ws/forecast`
WebSocket endpoint streaming live forecast events, stage-by-stage pipeline progress notifications, and Judge Demo updates.
```json
{
  "action": "RUN_DEMO",
  "scenario": "OROGRAPHIC",
  "mode": "DEMO"
}
```
Client receives:
- `PIPELINE_STAGE_UPDATE` (`INGESTING`, `ANALYZING`, `CLASSIFYING`, `CORRECTING`, `OPTIMIZING`, `QUANTIFYING`, `VERIFYING`)
- `FORECAST_COMPLETE` with full payload.
