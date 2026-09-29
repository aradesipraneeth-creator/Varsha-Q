"""
VARSHA-Q Demo & Replay Data Engine
Generates physically consistent, scientifically defensible synthetic meteorological datasets
simulating the 5 fundamental Indian weather regimes with realistic NWP systematic biases.
Enables 100% offline demonstration, testing, training, and verification without Internet connectivity.

LABELING:
All outputs from this engine are explicitly stamped as:
"SYNTHETIC DEMONSTRATION DATA / REPLAY"
"""
import math
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from .provider_base import WeatherDataProvider
from data.geo.districts_metadata import DISTRICTS_DATA


class DemoProvider(WeatherDataProvider):
    """
    Supplies realistic spatiotemporal meteorological datasets for Indian districts across 5 regimes.
    Known systematic bias characteristics:
    - ACTIVE_MONSOON: NWP convective underprediction along central trough (-15 to -35 mm)
    - BREAK_MONSOON: NWP false-alarm overprediction over peninsula (+10 to +25 mm), real rain confined to north
    - DEPRESSION_LOW: NWP core intensity underprediction & track displacement (-40 to -70 mm in coastal core)
    - COASTAL: NWP sea-breeze diurnal timing phase errors (+-15 mm)
    - OROGRAPHIC: NWP elevation-smoothing underprediction along Western Ghats & Northeast (-30 to -60 mm)
    """
    def __init__(self, random_seed: int = 42):
        self.rng = np.random.default_rng(random_seed)
        self.districts = DISTRICTS_DATA
        self.n_districts = len(self.districts)
        self.district_id_map = {d["id"]: idx for idx, d in enumerate(self.districts)}

    def get_source_name(self) -> str:
        return "VARSHA-Q Replay & Demonstration Engine"

    def get_mode(self) -> str:
        return "DEMO"

    def get_adjacency_matrix(self) -> np.ndarray:
        """Constructs binary spatial adjacency matrix between districts."""
        adj = np.zeros((self.n_districts, self.n_districts), dtype=np.float32)
        for i, d in enumerate(self.districts):
            for neighbor_id in d.get("neighbors", []):
                if neighbor_id in self.district_id_map:
                    j = self.district_id_map[neighbor_id]
                    adj[i, j] = 1.0
                    adj[j, i] = 1.0
        return adj

    def generate_scenario_data(self, regime: str = "ACTIVE_MONSOON", seed: int = 42) -> Dict[str, Any]:
        """
        Generates full spatiotemporal fields for a selected weather regime:
        - raw_nwp_rainfall
        - observed_rainfall (ground truth)
        - temporal_sequences (seq_len=6, 8 features)
        - spatial_node_features (7 features)
        - synoptic_features (10 features)
        """
        local_rng = np.random.default_rng(seed)
        N = self.n_districts

        raw_nwp = np.zeros(N, dtype=np.float64)
        observed = np.zeros(N, dtype=np.float64)
        
        # Base regime atmospheric parameters
        if regime == "ACTIVE_MONSOON":
            synoptic = np.array([
                35.0,  # nwp_mean_rain
                75.0,  # nwp_max_rain
                0.88,  # moisture_convergence
                88.0,  # relative_humidity
                -4.2,  # surface_pressure_anomaly (hPa)
                12.5,  # wind_speed (m/s)
                2.8,   # vorticity_850hpa (1e-5 s^-1)
                240.0, # mean_elevation
                3.5,   # mean_slope
                0.45   # coastal_proximity
            ], dtype=np.float64)

            # Central India and trough districts get high rain; NWP underpredicts
            for i, d in enumerate(self.districts):
                base = 25.0 + 35.0 * math.sin(math.radians(d["lat"]) * 2.0) + local_rng.normal(0, 5)
                base = max(5.0, base)
                raw_nwp[i] = round(base, 2)
                # Active monsoon bias: NWP underestimates deep convective cells
                underprediction = 15.0 + 0.4 * base + local_rng.normal(0, 4)
                observed[i] = round(max(0.0, raw_nwp[i] + underprediction), 2)

        elif regime == "BREAK_MONSOON":
            synoptic = np.array([
                8.0,   # nwp_mean_rain
                45.0,  # nwp_max_rain
                0.32,  # moisture_convergence (weak)
                62.0,  # relative_humidity (dry)
                +3.5,  # surface_pressure_anomaly (positive anomaly over peninsula)
                5.2,   # wind_speed (weak westerlies)
                0.4,   # vorticity_850hpa
                240.0,
                3.5,
                0.45
            ], dtype=np.float64)

            # Rainfall suppressed over peninsula, but active along Himalayan foothills / Northeast
            for i, d in enumerate(self.districts):
                is_foothill = d["state"] in ["Assam", "Meghalaya"] or d["id"] in ["WB_DJL", "WB_JPG"]
                if is_foothill:
                    raw_nwp[i] = round(45.0 + local_rng.normal(0, 8), 2)
                    observed[i] = round(raw_nwp[i] + 20.0 + local_rng.normal(0, 5), 2)
                else:
                    # Peninsular dry spell: NWP often has false alarms!
                    raw_nwp[i] = round(max(0.0, 15.0 + local_rng.normal(0, 4)), 2)
                    observed[i] = round(max(0.0, 1.5 + local_rng.normal(0, 1.0)), 2)  # Actual rain is near zero

        elif regime == "DEPRESSION_LOW":
            synoptic = np.array([
                48.0,  # nwp_mean_rain
                160.0, # nwp_max_rain
                0.95,  # moisture_convergence (extreme)
                94.0,  # relative_humidity
                -8.5,  # surface_pressure_anomaly (deep low)
                18.5,  # wind_speed (gale force)
                5.8,   # vorticity_850hpa (strong vortex)
                240.0,
                3.5,
                0.60
            ], dtype=np.float64)

            # Heavy core along Odisha & North Andhra coast
            for i, d in enumerate(self.districts):
                is_depression_core = d["state"] in ["Odisha", "Andhra Pradesh", "West Bengal"] and d["coastal_dist_km"] < 120
                if is_depression_core:
                    raw_nwp[i] = round(65.0 + local_rng.normal(0, 15), 2)
                    # Real depression core is torrential (120 - 180 mm)
                    observed[i] = round(raw_nwp[i] + 45.0 + local_rng.normal(0, 10), 2)
                else:
                    raw_nwp[i] = round(max(2.0, 20.0 + local_rng.normal(0, 6)), 2)
                    observed[i] = round(max(0.0, raw_nwp[i] + local_rng.normal(0, 5)), 2)

        elif regime == "COASTAL":
            synoptic = np.array([
                28.0,
                65.0,
                0.78,
                89.0,
                -1.2,
                9.5,
                1.5,
                240.0,
                3.5,
                0.85   # High coastal factor
            ], dtype=np.float64)

            for i, d in enumerate(self.districts):
                coastal_dist = d["coastal_dist_km"]
                if coastal_dist < 40.0:
                    raw_nwp[i] = round(22.0 + local_rng.normal(0, 5), 2)
                    # Sea-breeze convergence enhancement
                    observed[i] = round(raw_nwp[i] + 18.0 + local_rng.normal(0, 4), 2)
                else:
                    raw_nwp[i] = round(max(1.0, 12.0 + local_rng.normal(0, 4)), 2)
                    observed[i] = round(max(0.0, raw_nwp[i] - 3.0 + local_rng.normal(0, 3)), 2)

        elif regime == "OROGRAPHIC":
            synoptic = np.array([
                42.0,
                145.0,
                0.85,
                91.0,
                -2.0,
                14.0,
                2.1,
                650.0, # High elevation
                12.5,  # Steep slope
                0.40
            ], dtype=np.float64)

            for i, d in enumerate(self.districts):
                elev = d["elevation_m"]
                if elev > 600.0 or d["id"] in ["KL_WYD", "KL_IDK", "MH_RTG", "ML_SO", "WB_DJL"]:
                    raw_nwp[i] = round(45.0 + local_rng.normal(0, 12), 2)
                    # Mountain mechanical lifting creates massive precipitation underestimation in NWP
                    lifting_bias = 40.0 + 0.03 * elev + local_rng.normal(0, 8)
                    observed[i] = round(raw_nwp[i] + lifting_bias, 2)
                else:
                    raw_nwp[i] = round(max(2.0, 18.0 + local_rng.normal(0, 5)), 2)
                    observed[i] = round(max(0.0, raw_nwp[i] + local_rng.normal(0, 4)), 2)

        else: # UNKNOWN_TRANSITION
            synoptic = np.array([15.0, 35.0, 0.45, 70.0, 0.0, 6.0, 0.8, 240.0, 3.5, 0.45], dtype=np.float64)
            for i in range(N):
                raw_nwp[i] = round(max(0.0, 12.0 + local_rng.normal(0, 5)), 2)
                observed[i] = round(max(0.0, raw_nwp[i] + local_rng.normal(0, 4)), 2)

        # 2. Generate Temporal sequences for LNN: (N_districts, Seq_len=6, Features=8)
        # Features: [nwp_rain, obs_lag, temp, humidity, pressure, wind_u, wind_v, elevation_norm]
        seq_len = 6
        temporal_seq = np.zeros((N, seq_len, 8), dtype=np.float32)
        for i, d in enumerate(self.districts):
            elev_norm = min(1.0, d["elevation_m"] / 2000.0)
            base_r = raw_nwp[i]
            for t in range(seq_len):
                # Evolving temporal ramp
                t_factor = 0.5 + 0.5 * (t / (seq_len - 1))
                temporal_seq[i, t, 0] = max(0.0, base_r * t_factor + local_rng.normal(0, 2))
                temporal_seq[i, t, 1] = max(0.0, temporal_seq[i, max(0, t - 1), 0] * 0.9)
                temporal_seq[i, t, 2] = 28.0 - 0.006 * d["elevation_m"] + local_rng.normal(0, 0.5)
                temporal_seq[i, t, 3] = synoptic[3] + local_rng.normal(0, 2)
                temporal_seq[i, t, 4] = 1008.0 + synoptic[4] - (d["elevation_m"] / 10.0)
                temporal_seq[i, t, 5] = synoptic[5] * 0.8 + local_rng.normal(0, 1)
                temporal_seq[i, t, 6] = synoptic[5] * 0.5 + local_rng.normal(0, 1)
                temporal_seq[i, t, 7] = elev_norm

        # 3. Generate Spatial node features for GNN: (N_districts, Features=7)
        # Features: [raw_nwp, elevation, coastal_dist, slope, lat, lon, humidity]
        spatial_features = np.zeros((N, 7), dtype=np.float32)
        for i, d in enumerate(self.districts):
            spatial_features[i, 0] = raw_nwp[i] / 100.0  # Normalized rain
            spatial_features[i, 1] = min(1.0, d["elevation_m"] / 2000.0)
            spatial_features[i, 2] = min(1.0, d["coastal_dist_km"] / 500.0)
            spatial_features[i, 3] = 0.1 if d["elevation_m"] < 100 else 0.6
            spatial_features[i, 4] = (d["lat"] - 8.0) / 25.0
            spatial_features[i, 5] = (d["lon"] - 68.0) / 30.0
            spatial_features[i, 6] = synoptic[3] / 100.0

        adj_matrix = self.get_adjacency_matrix()

        return {
            "mode": "DEMO",
            "provenance": {
                "source": "VARSHA-Q Synthetic Replay Data Engine",
                "disclaimer": "SYNTHETIC DEMONSTRATION DATA / REPLAY. Not official IMD observations.",
                "valid_time": datetime.now(timezone.utc).isoformat(),
                "cycle": "00Z GFS Replay Scenario",
                "scenario_regime": regime
            },
            "regime": regime,
            "synoptic_features": synoptic,
            "raw_nwp_rainfall": raw_nwp.tolist(),
            "observed_rainfall": observed.tolist(),
            "temporal_sequences": temporal_seq,
            "spatial_features": spatial_features,
            "adjacency_matrix": adj_matrix,
            "districts": self.districts
        }

    async def fetch_forecast(self, district_ids: Optional[List[str]] = None, horizon_hours: int = 24) -> Dict[str, Any]:
        return self.generate_scenario_data("ACTIVE_MONSOON")

    async def fetch_observations(self, district_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        data = self.generate_scenario_data("ACTIVE_MONSOON")
        return {"observations": data["observed_rainfall"], "districts": self.districts}

    async def get_status(self) -> Dict[str, Any]:
        return {
            "source": self.get_source_name(),
            "mode": self.get_mode(),
            "status": "ONLINE (Offline Replay Engine Ready)",
            "scenarios_available": ["ACTIVE_MONSOON", "BREAK_MONSOON", "DEPRESSION_LOW", "COASTAL", "OROGRAPHIC"],
            "districts_count": self.n_districts
        }
