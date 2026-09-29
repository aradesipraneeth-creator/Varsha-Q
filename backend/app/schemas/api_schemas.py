"""
VARSHA-Q Pydantic API Schemas
Strongly-typed data contracts for FastAPI endpoints and WebSocket streams.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime


class SystemStatusResponse(BaseModel):
    project_name: str = "VARSHA-Q"
    full_title: str
    version: str
    team: str = "QUANTUM LEAPERS"
    mode: str = "DEMO"  # LIVE, RESEARCH, DEMO
    device: str
    is_healthy: bool = True
    data_sources: Dict[str, Any]
    active_scenario: Optional[str] = None
    last_update: str


class ProbabilityBreakdown(BaseModel):
    p_gt_15mm: float = 0.0
    p_gt_25mm: float = 0.0
    p_gt_50mm: float = 0.0
    p_gt_100mm: float = 0.0
    p_gt_150mm: float = 0.0


class UncertaintyInterval(BaseModel):
    lower_bound_p10_mm: float
    median_p50_mm: float
    upper_bound_p90_mm: float
    uncertainty_spread_mm: float
    uncertainty_level: str  # LOW, MODERATE, HIGH


class DistrictForecastItem(BaseModel):
    district_id: str
    name: str
    state: str
    lat: float
    lon: float
    elevation_m: float
    coastal_dist_km: float
    raw_nwp_rainfall_mm: float
    corrected_rainfall_mm: float
    delta_mm: float
    observed_rainfall_mm: Optional[float] = None
    regime: str
    heavy_rain_probabilities: Dict[str, float]
    uncertainty: UncertaintyInterval
    risk_category: str  # LOW, MODERATE, HIGH, VERY HIGH
    risk_label: str


class RegimeIntelligence(BaseModel):
    regime: str
    title: str
    confidence: float
    probabilities: Dict[str, float]
    description: str
    key_indicators: List[str]
    feature_contributions: List[Dict[str, Any]]


class ForecastResponse(BaseModel):
    run_id: Optional[int] = None
    timestamp: str
    mode: str
    provenance: Dict[str, Any]
    regime_intelligence: RegimeIntelligence
    correction_summary: Dict[str, Any]
    spatiotemporal_representation: Dict[str, Any]
    district_forecasts: List[DistrictForecastItem]
    verification: Optional[Dict[str, Any]] = None


class RunInferenceRequest(BaseModel):
    scenario: Optional[str] = "ACTIVE_MONSOON"  # ACTIVE_MONSOON, BREAK_MONSOON, DEPRESSION_LOW, COASTAL, OROGRAPHIC
    force_mode: Optional[str] = None  # LIVE, RESEARCH, DEMO
    horizon_hours: int = 24


class OptimizationRunResponse(BaseModel):
    status: str
    scientific_disclaimer: str
    classical_baseline: Dict[str, Any]
    quantum_inspired: Dict[str, Any]
    energy_delta: float
    qubo_dimension: int


class RegimeEvaluationItem(BaseModel):
    regime: str
    sample_count: int
    raw_rmse: float
    corrected_rmse: float
    rmse_reduction_pct: float
    csi_25: float
    pod_25: float
    far_25: float
    ets_25: float
    fss_25: float


class FullVerificationResponse(BaseModel):
    overall: Dict[str, Any]
    regime_wise: List[RegimeEvaluationItem]
    status: str
    scientific_note: str
