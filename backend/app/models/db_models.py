"""
VARSHA-Q Database Models
Stores locations, observations, NWP forecasts, corrected forecasts, weather regimes,
verification metrics, and optimization runs.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ..core.database import Base


class District(Base):
    __tablename__ = "districts"

    id = Column(String(32), primary_key=True, index=True)
    name = Column(String(128), nullable=False, index=True)
    state = Column(String(64), nullable=False, index=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    elevation_m = Column(Float, default=0.0)
    coastal_dist_km = Column(Float, default=100.0)
    typical_regime = Column(String(64), default="ACTIVE_MONSOON")
    neighbors = Column(JSON, default=list)


class ForecastRun(Base):
    __tablename__ = "forecast_runs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    mode = Column(String(16), default="DEMO", index=True)  # LIVE, RESEARCH, DEMO
    regime = Column(String(64), nullable=False)
    confidence = Column(Float, default=0.0)
    strategy = Column(String(128), default="Regime-Specific")
    is_fallback = Column(Boolean, default=False)
    mean_nwp_mm = Column(Float, default=0.0)
    mean_corrected_mm = Column(Float, default=0.0)
    rmse_reduction_pct = Column(Float, default=0.0)
    data_source = Column(String(128), default="VARSHA-Q Provider")
    notes = Column(Text, nullable=True)

    district_forecasts = relationship("DistrictForecast", back_populates="run", cascade="all, delete-orphan")


class DistrictForecast(Base):
    __tablename__ = "district_forecasts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    run_id = Column(Integer, ForeignKey("forecast_runs.id"), nullable=False, index=True)
    district_id = Column(String(32), ForeignKey("districts.id"), nullable=False, index=True)
    
    raw_nwp_mm = Column(Float, default=0.0)
    corrected_mm = Column(Float, default=0.0)
    observed_mm = Column(Float, nullable=True)
    delta_mm = Column(Float, default=0.0)

    # Uncertainty bounds
    lower_bound_p10_mm = Column(Float, default=0.0)
    median_p50_mm = Column(Float, default=0.0)
    upper_bound_p90_mm = Column(Float, default=0.0)
    uncertainty_level = Column(String(16), default="LOW")

    # Exceedance probabilities
    p_gt_15mm = Column(Float, default=0.0)
    p_gt_25mm = Column(Float, default=0.0)
    p_gt_50mm = Column(Float, default=0.0)
    p_gt_100mm = Column(Float, default=0.0)

    risk_category = Column(String(32), default="LOW")

    run = relationship("ForecastRun", back_populates="district_forecasts")


class Observation(Base):
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    district_id = Column(String(32), ForeignKey("districts.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    rainfall_mm = Column(Float, nullable=False)
    source = Column(String(64), default="RainGauge/AWS")
    quality_flag = Column(String(32), default="PASSED")


class VerificationRecord(Base):
    __tablename__ = "verification_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    regime = Column(String(64), nullable=False, index=True)
    mode = Column(String(16), default="DEMO")
    sample_count = Column(Integer, default=0)

    # Continuous
    raw_rmse = Column(Float, default=0.0)
    corrected_rmse = Column(Float, default=0.0)
    rmse_reduction_pct = Column(Float, default=0.0)

    # Categorical @ 25mm threshold
    csi_25 = Column(Float, default=0.0)
    pod_25 = Column(Float, default=0.0)
    far_25 = Column(Float, default=0.0)
    ets_25 = Column(Float, default=0.0)
    fss_25 = Column(Float, default=0.0)

    full_payload = Column(JSON, nullable=True)


class OptimizationRun(Base):
    __tablename__ = "optimization_runs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    optimizer_name = Column(String(128), nullable=False)
    initial_energy = Column(Float, default=0.0)
    optimized_energy = Column(Float, default=0.0)
    delta_energy = Column(Float, default=0.0)
    selected_features = Column(JSON, default=list)
    runtime_ms = Column(Float, default=0.0)
    details = Column(JSON, nullable=True)
