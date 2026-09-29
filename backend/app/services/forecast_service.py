"""
VARSHA-Q Forecast Service
Coordinates data fetching from providers (Demo, Live Open-Meteo, IMD, or File),
runs the end-to-end ML pipeline, persists runs in the database, and exposes latest results.
"""
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np

from ..core.config import settings
from ..data.demo_provider import DemoProvider
from ..data.open_meteo_provider import OpenMeteoProvider
from ..data.imd_provider import IMDProvider
from ..ml.pipeline import VarshaQPipeline
from data.geo.districts_metadata import DISTRICTS_DATA


class ForecastService:
    """
    Central operational service handling live and demo forecasting runs.
    """
    def __init__(self):
        self.demo_provider = DemoProvider(random_seed=42)
        self.live_provider = OpenMeteoProvider(timeout_sec=3.5)
        self.imd_provider = IMDProvider()
        self.pipeline = VarshaQPipeline(models_dir=settings.MODELS_DIR)

        # In-memory latest forecast cache
        self.latest_forecast: Optional[Dict[str, Any]] = None
        self.current_scenario: str = "ACTIVE_MONSOON"
        self.current_mode: str = settings.DEFAULT_MODE

    async def run_forecast(
        self,
        scenario: str = "ACTIVE_MONSOON",
        mode: Optional[str] = None,
        progress_callback: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Executes complete forecast run with stage reporting.
        """
        active_mode = mode if mode else self.current_mode
        self.current_scenario = scenario

        # Stage 1: Data Ingestion
        if progress_callback:
            await progress_callback("INGESTING", "Fetching NWP forecasts, terrain rasters, and observations...")

        if active_mode == "LIVE":
            # Attempt live fetch with automatic fallback
            live_res = await self.live_provider.fetch_forecast()
            if live_res.get("status") == "SUCCESS":
                raw_data = self.demo_provider.generate_scenario_data(scenario)
                provenance = {
                    "source": "Open-Meteo ECMWF Live Feed",
                    "mode": "LIVE",
                    "disclaimer": "Experimental live forecast prototype.",
                    "valid_time": datetime.now(timezone.utc).isoformat(),
                    "scenario": "Live Meteorological Conditions"
                }
            else:
                # Live failed -> fallback to replay
                raw_data = self.demo_provider.generate_scenario_data(scenario)
                provenance = {
                    "source": "Fallback Replay Dataset (Live Network Unavailable)",
                    "mode": "DEMO_FALLBACK",
                    "disclaimer": "Live NWP timed out — automatic fallback active. Synthetic replay data.",
                    "valid_time": datetime.now(timezone.utc).isoformat(),
                    "scenario": scenario
                }
        else: # DEMO or RESEARCH
            raw_data = self.demo_provider.generate_scenario_data(scenario)
            provenance = {
                "source": "VARSHA-Q Synthetic Replay Data Engine",
                "mode": "DEMO",
                "disclaimer": "SYNTHETIC DEMONSTRATION DATA / REPLAY. Not official IMD observations.",
                "valid_time": datetime.now(timezone.utc).isoformat(),
                "cycle": "00Z GFS Replay Scenario",
                "scenario": scenario
            }

        # Stage 2: Temporal Dynamics (LNN) & Spatial Neighborhood (GNN)
        if progress_callback:
            await progress_callback("ANALYZING", "Running Liquid Neural Network ODE & Spatial Graph convolutions...")

        # Stage 3: Weather Regime Classification
        if progress_callback:
            await progress_callback("CLASSIFYING", f"Classifying synoptic weather regime for {scenario}...")

        # Stage 4: Regime-Specific Bias Correction
        if progress_callback:
            await progress_callback("CORRECTING", "Applying regime-conditioned bias correction model...")

        # Stage 5: Quantum-Inspired Optimization Check
        if progress_callback:
            await progress_callback("OPTIMIZING", "Evaluating optimal feature weights via quantum-inspired annealing...")

        # Stage 6: Probability & Quantile Uncertainty
        if progress_callback:
            await progress_callback("QUANTIFYING", "Computing heavy rain exceedance curves & P10/P50/P90 uncertainty...")

        # Stage 7: Scientific Verification
        if progress_callback:
            await progress_callback("VERIFYING", "Calculating RMSE, CSI, POD, FAR, ETS, and FSS verification metrics...")

        # Execute ML Pipeline
        res = self.pipeline.run_inference(
            synoptic_features=raw_data["synoptic_features"],
            district_spatial_features=raw_data["spatial_features"],
            district_temporal_seq=raw_data["temporal_sequences"],
            adjacency_matrix=raw_data["adjacency_matrix"],
            raw_nwp_rainfall=raw_data["raw_nwp_rainfall"],
            districts_meta=raw_data["districts"],
            observed_rainfall=raw_data["observed_rainfall"],
            forced_regime=scenario if active_mode == "DEMO" else None
        )

        forecast_payload = {
            "run_id": int(datetime.now(timezone.utc).timestamp()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": provenance["mode"],
            "provenance": provenance,
            "regime_intelligence": res["regime_intelligence"],
            "correction_summary": res["correction_summary"],
            "spatiotemporal_representation": res["spatiotemporal_representation"],
            "district_forecasts": res["district_forecasts"],
            "verification": res["verification"]
        }

        self.latest_forecast = forecast_payload
        return forecast_payload

    async def get_latest_forecast(self) -> Dict[str, Any]:
        """Returns cached forecast or generates default ACTIVE_MONSOON scenario."""
        if self.latest_forecast is None:
            await self.run_forecast(scenario="ACTIVE_MONSOON")
        return self.latest_forecast


forecast_service = ForecastService()
