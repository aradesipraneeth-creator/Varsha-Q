"""
VARSHA-Q Spatiotemporal Feature Engineering Pipeline
Constructs meteorological, terrain, and temporal cyclic features for ML models:
- Lags & rolling precipitation statistics
- Monsoon phase indicators and Day-Of-Year harmonics
- Terrain elevation, slope, and marine-coastal distance
"""
import math
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional


class FeatureEngineeringPipeline:
    """
    Transforms aligned raw data into ML-ready tensor representations.
    """
    def __init__(self):
        pass

    @staticmethod
    def get_monsoon_phase(doy: int) -> Dict[str, Any]:
        """
        Determines Indian Southwest Monsoon seasonal phase from Day-Of-Year:
        - Pre-monsoon: DOY 60 - 151 (March - May)
        - Onset: DOY 152 - 181 (June)
        - Peak Active: DOY 182 - 243 (July - August)
        - Withdrawal / Post-monsoon: DOY 244 - 304 (September - October)
        - Winter / Dry: DOY 305 - 59 (November - February)
        """
        if 152 <= doy <= 181:
            phase_name = "ONSET"
            phase_weight = 0.7
        elif 182 <= doy <= 243:
            phase_name = "PEAK_ACTIVE"
            phase_weight = 1.0
        elif 244 <= doy <= 304:
            phase_name = "WITHDRAWAL"
            phase_weight = 0.6
        elif 60 <= doy < 152:
            phase_name = "PRE_MONSOON"
            phase_weight = 0.3
        else:
            phase_name = "DRY_WINTER"
            phase_weight = 0.1

        sin_doy = math.sin(2.0 * math.pi * doy / 365.25)
        cos_doy = math.cos(2.0 * math.pi * doy / 365.25)

        return {
            "phase": phase_name,
            "weight": phase_weight,
            "sin_doy": round(sin_doy, 4),
            "cos_doy": round(cos_doy, 4)
        }

    def create_features(
        self,
        raw_nwp: np.ndarray,
        districts_meta: List[Dict[str, Any]],
        dt: Optional[datetime] = None
    ) -> Dict[str, np.ndarray]:
        """
        Constructs features for GNN and LNN components.
        """
        now = dt if dt else datetime.now()
        doy = now.timetuple().tm_yday
        monsoon_info = self.get_monsoon_phase(doy)

        N = len(districts_meta)
        spatial_feats = np.zeros((N, 7), dtype=np.float32)

        for i, d in enumerate(districts_meta):
            spatial_feats[i, 0] = raw_nwp[i] / 100.0
            spatial_feats[i, 1] = min(1.0, d.get("elevation_m", 50.0) / 2000.0)
            spatial_feats[i, 2] = min(1.0, d.get("coastal_dist_km", 100.0) / 500.0)
            spatial_feats[i, 3] = monsoon_info["weight"]
            spatial_feats[i, 4] = (d.get("lat", 20.0) - 8.0) / 25.0
            spatial_feats[i, 5] = (d.get("lon", 80.0) - 68.0) / 30.0
            spatial_feats[i, 6] = monsoon_info["sin_doy"]

        return {
            "spatial_features": spatial_feats,
            "monsoon_phase": monsoon_info
        }
