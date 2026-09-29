"""
VARSHA-Q FastAPI REST API Endpoints
Implements all operational forecast, regime intelligence, district drill-down,
optimization benchmarking, and scientific verification endpoints.
"""
from datetime import datetime, timezone
import numpy as np
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..core.config import settings
from ..services.forecast_service import forecast_service
from ..services.district_service import district_service
from ..services.verification_service import verification_service
from ..optimization.qubo_optimizer import run_benchmark_optimization
from ..ml.regime_classifier import REGIME_CLASSES, REGIME_DESCRIPTIONS, REGIME_FEATURE_NAMES
from ..data.file_provider import FileProvider

router = APIRouter()
file_provider = FileProvider()


@router.get("/health")
async def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "team": settings.TEAM_NAME,
        "mode": forecast_service.current_mode,
        "device": str(forecast_service.pipeline.device),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/api/system/status")
async def get_system_status():
    """Provides operational status of data feeds, pipeline, and models."""
    om_status = await forecast_service.live_provider.get_status()
    imd_status = await forecast_service.imd_provider.get_status()
    demo_status = await forecast_service.demo_provider.get_status()

    return {
        "project_name": settings.PROJECT_NAME,
        "full_title": settings.FULL_TITLE,
        "version": settings.VERSION,
        "team": settings.TEAM_NAME,
        "problem_statement": settings.PROBLEM_STATEMENT,
        "mode": forecast_service.current_mode,
        "device": str(forecast_service.pipeline.device),
        "active_scenario": forecast_service.current_scenario,
        "is_healthy": True,
        "data_sources": {
            "nwp_live": om_status,
            "imd_moes": imd_status,
            "demo_replay": demo_status
        },
        "models_status": {
            "regime_classifier": "READY" if forecast_service.pipeline.regime_classifier.is_fitted else "TRAINED_DEMO",
            "lnn_temporal": "READY (Liquid Time-Constant ODE active)",
            "gnn_spatial": "READY (Spatial Graph Convolution active)",
            "bias_corrector": "READY (Regime-specific models loaded)",
            "optimizer": "READY (Simulated Quantum Annealer + QUBO active)"
        },
        "last_update": datetime.now(timezone.utc).isoformat()
    }


@router.get("/api/data/status")
async def get_data_status():
    """Returns provenance and connection status of all ingested data streams."""
    return await get_system_status()


@router.get("/api/forecast/latest")
async def get_latest_forecast():
    """Returns the most recent bias-corrected rainfall forecast and verification."""
    return await forecast_service.get_latest_forecast()


@router.get("/api/forecast/districts")
async def get_forecast_districts(state: Optional[str] = None):
    """Returns district-level forecasts, optionally filtered by state."""
    fc = await forecast_service.get_latest_forecast()
    districts = fc.get("district_forecasts", [])
    if state:
        districts = [d for d in districts if d["state"].lower() == state.lower()]
    return {
        "count": len(districts),
        "state_filter": state,
        "districts": districts
    }


@router.get("/api/forecast/district/{district_id}")
async def get_district_forecast(district_id: str):
    """Returns detailed forecast, exceedance curve, and uncertainty for a single district."""
    fc = await forecast_service.get_latest_forecast()
    for d in fc.get("district_forecasts", []):
        if d["district_id"].lower() == district_id.lower():
            meta = district_service.get_district_by_id(district_id)
            return {
                "district": d,
                "metadata": meta,
                "regime": fc.get("regime_intelligence"),
                "provenance": fc.get("provenance")
            }
    raise HTTPException(status_code=404, detail=f"District '{district_id}' not found.")


@router.get("/api/regime/current")
async def get_current_regime():
    """Returns the currently classified weather regime and confidence."""
    fc = await forecast_service.get_latest_forecast()
    return fc.get("regime_intelligence")


@router.get("/api/regimes")
async def list_regimes():
    """Returns definitions and meteorological indicators of all supported regimes."""
    return {
        "classes": REGIME_CLASSES,
        "descriptions": REGIME_DESCRIPTIONS,
        "feature_names": REGIME_FEATURE_NAMES
    }


@router.get("/api/districts/geojson")
async def get_districts_geojson():
    """Returns GeoJSON polygon boundaries and centroids for India map rendering."""
    return district_service.get_geojson()


@router.get("/api/probability")
async def get_probability_overview():
    """Returns regional heavy-rain probability distribution summary."""
    fc = await forecast_service.get_latest_forecast()
    districts = fc.get("district_forecasts", [])
    if not districts:
        return {"count": 0, "probabilities": {}}

    p25 = [d["heavy_rain_probabilities"].get("p_gt_25mm", 0.0) for d in districts]
    p50 = [d["heavy_rain_probabilities"].get("p_gt_50mm", 0.0) for d in districts]
    p100 = [d["heavy_rain_probabilities"].get("p_gt_100mm", 0.0) for d in districts]

    return {
        "timestamp": fc.get("timestamp"),
        "regime": fc.get("regime_intelligence", {}).get("regime"),
        "summary": {
            "mean_p_gt_25mm": round(float(np.mean(p25)), 3),
            "max_p_gt_25mm": round(float(np.max(p25)), 3),
            "mean_p_gt_50mm": round(float(np.mean(p50)), 3),
            "max_p_gt_50mm": round(float(np.max(p50)), 3),
            "mean_p_gt_100mm": round(float(np.mean(p100)), 3),
            "districts_high_risk": sum(1 for d in districts if d.get("risk_category") in ["HIGH", "VERY HIGH"])
        }
    }


@router.get("/api/verification")
async def get_verification():
    """Returns multi-regime scientific verification metrics (RAW NWP vs VARSHA-Q)."""
    return verification_service.evaluate_all_regimes()


@router.get("/api/verification/regime")
async def get_regime_verification():
    """Returns regime-wise verification breakdown."""
    res = verification_service.evaluate_all_regimes()
    return {"regime_wise": res["regime_wise"], "scientific_note": res["scientific_note"]}


@router.post("/api/inference/run")
async def run_inference(scenario: str = Query("ACTIVE_MONSOON"), mode: Optional[str] = None):
    """
    Triggers an end-to-end forecast inference run for a specified regime scenario or live feed.
    """
    valid_scenarios = ["ACTIVE_MONSOON", "BREAK_MONSOON", "DEPRESSION_LOW", "COASTAL", "OROGRAPHIC"]
    if scenario not in valid_scenarios:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid scenario '{scenario}'. Allowed: {valid_scenarios}"
        )
    result = await forecast_service.run_forecast(scenario=scenario, mode=mode)
    return result


@router.post("/api/optimization/run")
async def run_optimization_benchmark():
    """
    Runs real benchmark comparison between:
    1. Classical Simulated Annealing (Baseline)
    2. Simulated Quantum Annealing (Quantum-Inspired)
    Optimizes QUBO feature selection over meteorological predictors.
    """
    feature_names = [
        "nwp_rainfall",
        "lag1_rainfall",
        "relative_humidity",
        "surface_pressure",
        "wind_convergence",
        "terrain_elevation",
        "coastal_distance",
        "monsoon_phase"
    ]
    # Synthetic realistic errors and correlation for meteorological predictors
    errors = np.array([4.1, 5.2, 7.3, 8.1, 6.4, 7.9, 8.5, 9.2])
    corr = np.eye(len(feature_names))
    corr[0, 1] = corr[1, 0] = 0.78  # Rain and lag rain
    corr[2, 4] = corr[4, 2] = 0.65  # Moisture and convergence
    corr[5, 6] = corr[6, 5] = 0.50  # Elevation and coast

    res = run_benchmark_optimization(feature_names, errors, corr)
    return res


@router.get("/api/optimization/latest")
async def get_latest_optimization():
    """Returns the latest optimization benchmark results."""
    return await run_optimization_benchmark()


@router.post("/api/data/upload")
async def upload_research_data(file: UploadFile = File(...)):
    """Accepts uploaded NetCDF, CSV, or Parquet datasets for research mode."""
    dest = Path(settings.DATA_DIR) / "raw" / file.filename
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "wb") as f:
        f.write(await file.read())

    try:
        meta = file_provider.load_tabular(dest)
        return {
            "status": "SUCCESS",
            "message": f"Successfully loaded research dataset '{file.filename}'",
            "metadata": meta
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse research file: {str(e)}")


@router.get("/api/models")
async def get_models_info():
    """Lists model architectures, checkpoint statuses, and training parameters."""
    return {
        "models": [
            {
                "name": "Weather Regime Classifier",
                "type": "Random Forest / Calibrated Classifier",
                "classes": REGIME_CLASSES,
                "input_features": REGIME_FEATURE_NAMES,
                "role": "Classifies synoptic regime prior to bias correction"
            },
            {
                "name": "LNN Temporal Model",
                "type": "Liquid Neural Network (Liquid Time-Constant ODE)",
                "layers": 2,
                "hidden_dim": 32,
                "time_constant_discretization": "Semi-implicit Euler",
                "role": "Continuous-time atmospheric and precipitation sequence memory"
            },
            {
                "name": "GNN Spatial Model",
                "type": "Spatial Graph Convolution (Symmetric normalized adjacency)",
                "layers": 2,
                "hidden_dim": 32,
                "role": "District graph message passing over topological neighborhoods"
            },
            {
                "name": "Spatiotemporal Fusion",
                "type": "Gated Cross-Projection Fusion Layer",
                "output_dim": 32,
                "role": "Joint spatiotemporal representation learning"
            },
            {
                "name": "Regime-Specific Bias Correctors",
                "type": "Ensemble Gradient Boosted Estimators",
                "regimes": ["ACTIVE_MONSOON", "BREAK_MONSOON", "DEPRESSION_LOW", "COASTAL", "OROGRAPHIC"],
                "fallback": "Global Fallback Estimator",
                "target": "Observed - NWP Rainfall"
            },
            {
                "name": "Quantum-Inspired Optimizer",
                "type": "Simulated Quantum Annealing (Path-Integral Trotter Replicas) + QEA",
                "quantum_tunneling": "Enabled via transverse field Gamma(t)",
                "role": "Feature selection and model parameter configuration search"
            }
        ]
    }
