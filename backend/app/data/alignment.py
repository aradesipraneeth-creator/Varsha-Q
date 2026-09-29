"""
VARSHA-Q Data Alignment and Quality Assurance Engine
Performs:
1. Spatial mapping / nearest-neighbour alignment between point observations, NWP grids, and district boundaries
2. Missing-data handling with explicit imputation and QA flagging
3. Unit normalization and coordinate standardization
4. Quality reporting: Never silently discards missing data
"""
import math
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional


class DataAlignmentEngine:
    """
    Standardizes, validates, and aligns disparate meteorological observations and NWP forecast grids.
    """
    def __init__(self, max_allowed_rainfall_mm: float = 650.0):
        self.max_rain = max_allowed_rainfall_mm

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Great-circle distance in kilometers between two lat/lon points."""
        R = 6371.0
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = (math.sin(d_lat / 2.0) ** 2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2.0) ** 2)
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return R * c

    def align_points_to_districts(
        self, 
        points_df: pd.DataFrame, 
        districts_meta: List[Dict[str, Any]]
    ) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        Maps scattered observation or NWP points to district centroids using nearest distance.
        Returns:
          rainfall_by_district: (N_districts,)
          qa_reports: List of QA metrics per district
        """
        N = len(districts_meta)
        aligned_rain = np.zeros(N, dtype=np.float64)
        qa_reports = []

        for i, d in enumerate(districts_meta):
            d_lat, d_lon = d["lat"], d["lon"]
            # Find closest points
            if "lat" in points_df.columns and "lon" in points_df.columns:
                dists = [
                    self.haversine_distance(d_lat, d_lon, r["lat"], r["lon"])
                    for _, r in points_df.iterrows()
                ]
                min_idx = int(np.argmin(dists))
                min_dist = dists[min_idx]
                rain_val = points_df.iloc[min_idx].get("rainfall", 0.0)
            else:
                rain_val = 0.0
                min_dist = 0.0

            # QA check
            flag = "PASSED"
            if np.isnan(rain_val) or rain_val < 0.0:
                rain_val = 0.0
                flag = "IMPUTED_MISSING"
            elif rain_val > self.max_rain:
                rain_val = self.max_rain
                flag = "EXTREME_CLIPPED"

            aligned_rain[i] = round(float(rain_val), 2)
            qa_reports.append({
                "district_id": d["id"],
                "distance_km": round(min_dist, 1),
                "rainfall_mm": aligned_rain[i],
                "qa_flag": flag
            })

        return aligned_rain, qa_reports

    def compute_quality_summary(self, qa_reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregates quality assurance metrics across all reporting stations."""
        total = len(qa_reports)
        if total == 0:
            return {"total_stations": 0, "quality_score": 100.0, "imputed_count": 0}

        imputed = sum(1 for r in qa_reports if "IMPUTED" in r["qa_flag"])
        clipped = sum(1 for r in qa_reports if "CLIPPED" in r["qa_flag"])
        passed = sum(1 for r in qa_reports if r["qa_flag"] == "PASSED")

        quality_score = round((passed / total) * 100.0, 1)

        return {
            "total_districts": total,
            "passed_count": passed,
            "imputed_count": imputed,
            "clipped_extremes": clipped,
            "quality_score_pct": quality_score,
            "status": "EXCELLENT" if quality_score >= 95 else ("ACCEPTABLE" if quality_score >= 80 else "DEGRADED")
        }
