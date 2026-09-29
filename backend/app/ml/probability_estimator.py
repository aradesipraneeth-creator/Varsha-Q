"""
VARSHA-Q Heavy Rain Probability & Uncertainty Estimator
Estimates:
1. Probabilistic exceedance curves P(Rain > threshold) for operational hydrometeorological thresholds:
   > 15 mm (Moderate)
   > 25 mm (Rather Heavy)
   > 50 mm (Heavy)
   > 100 mm (Very Heavy)
   > 150 mm (Extremely Heavy)
2. Predictive uncertainty bounds (P10 lower bound, P50 median, P90 upper bound)
3. Model-Derived Risk Category: LOW, MODERATE, HIGH, VERY HIGH
"""
import math
import numpy as np
from typing import Dict, Any, List, Union


THRESHOLDS = [15.0, 25.0, 50.0, 100.0, 150.0]


class ProbabilityAndUncertaintyEstimator:
    """
    Computes calibrated heavy-rain exceedance probabilities and quantile uncertainty intervals.
    Uses log-normal precipitation distribution modeling:
    ln(R) ~ N(mu, sigma^2) with heteroscedastic spread conditioned on rainfall amount and regime variance.
    """
    def __init__(self, thresholds: List[float] = THRESHOLDS):
        self.thresholds = thresholds

    def estimate_district(
        self, 
        corrected_rainfall: float, 
        regime: str, 
        coastal_factor: float = 0.5,
        elevation_m: float = 100.0
    ) -> Dict[str, Any]:
        """
        Estimates probabilities, uncertainty bounds, and risk category for a single district.
        """
        r_val = max(0.0, float(corrected_rainfall))

        # Regime-dependent atmospheric dispersion scale sigma
        base_sigma = 0.35
        if regime == "DEPRESSION_LOW":
            base_sigma = 0.55  # High convective volatility
        elif regime == "OROGRAPHIC":
            base_sigma = 0.45  # Wind-slope microclimate sensitivity
        elif regime == "COASTAL":
            base_sigma = 0.40  # Sea-breeze convective timing uncertainty
        elif regime == "BREAK_MONSOON":
            base_sigma = 0.30  # Dry regime stability

        # Heteroscedastic variance: higher rainfall has higher absolute spread
        sigma = base_sigma * (1.0 + 0.15 * math.log1p(r_val))

        # Quantile bounds: P10, P50, P90
        # For small rain near 0, bound at 0
        if r_val < 0.5:
            p10 = 0.0
            p50 = r_val
            p90 = max(0.0, r_val + 2.0)
            uncertainty_spread = p90 - p10
        else:
            p10 = max(0.0, r_val * math.exp(-1.282 * sigma))
            p50 = r_val
            p90 = r_val * math.exp(1.282 * sigma)
            uncertainty_spread = p90 - p10

        # Calculate P(Rain > thr) using log-normal survival function: 1 - Phi((ln(thr) - ln(r))/sigma)
        exceedance_probs = {}
        for thr in self.thresholds:
            thr_key = f"p_gt_{int(thr)}mm"
            if r_val <= 0.01:
                prob = 0.0
            else:
                z = (math.log(thr) - math.log(max(0.1, r_val))) / sigma
                # Standard normal CDF approximation
                phi = 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
                prob = 1.0 - phi
            # Clamp between 0.0 and 1.0
            exceedance_probs[thr_key] = round(float(max(0.0, min(1.0, prob))), 3)

        # Uncertainty qualitative indicator
        if uncertainty_spread < 8.0:
            uncertainty_level = "LOW"
        elif uncertainty_spread < 25.0:
            uncertainty_level = "MODERATE"
        else:
            uncertainty_level = "HIGH"

        # Model-derived Risk Category
        p_50 = exceedance_probs.get("p_gt_50mm", 0.0)
        p_100 = exceedance_probs.get("p_gt_100mm", 0.0)
        if r_val >= 100.0 or p_100 >= 0.40:
            risk_category = "VERY HIGH"
        elif r_val >= 50.0 or p_50 >= 0.45:
            risk_category = "HIGH"
        elif r_val >= 25.0 or p_50 >= 0.20:
            risk_category = "MODERATE"
        else:
            risk_category = "LOW"

        return {
            "corrected_rainfall_mm": round(r_val, 2),
            "uncertainty": {
                "lower_bound_p10_mm": round(float(p10), 2),
                "median_p50_mm": round(float(p50), 2),
                "upper_bound_p90_mm": round(float(p90), 2),
                "uncertainty_spread_mm": round(float(uncertainty_spread), 2),
                "uncertainty_level": uncertainty_level
            },
            "heavy_rain_probabilities": exceedance_probs,
            "risk_category": risk_category,
            "risk_label": "MODEL-DERIVED RISK (Illustrative / Not Official Warning)"
        }

    def estimate_batch(
        self, 
        corrected_rainfalls: List[float], 
        regime: str
    ) -> List[Dict[str, Any]]:
        return [self.estimate_district(val, regime) for val in corrected_rainfalls]
