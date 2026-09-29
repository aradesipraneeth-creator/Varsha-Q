"""
VARSHA-Q Verification Engine
Meteorologically rigorous forecast verification metrics for precipitation fields.
Calculates continuous (RMSE, MAE, Correlation) and categorical / threshold metrics (CSI, POD, FAR, ETS),
as well as spatial field metrics (FSS - Fractions Skill Score).
"""
import numpy as np
from typing import Dict, Any, Union, List, Optional


def calculate_continuous_metrics(
    observed: Union[np.ndarray, List[float]], 
    forecast: Union[np.ndarray, List[float]]
) -> Dict[str, float]:
    """
    Computes continuous verification metrics:
    - RMSE: Root Mean Squared Error (mm)
    - MAE: Mean Absolute Error (mm)
    - BIAS: Mean Error (Forecast - Observed) (mm)
    - CORR: Pearson Correlation Coefficient [-1, 1]
    """
    y_true = np.asarray(observed, dtype=np.float64)
    y_pred = np.asarray(forecast, dtype=np.float64)

    # Valid mask for missing data / NaNs
    valid = np.isfinite(y_true) & np.isfinite(y_pred)
    if not np.any(valid):
        return {"rmse": 0.0, "mae": 0.0, "bias": 0.0, "corr": 0.0, "count": 0}

    y_t = y_true[valid]
    y_p = y_pred[valid]
    n = len(y_t)

    error = y_p - y_t
    rmse = float(np.sqrt(np.mean(error ** 2)))
    mae = float(np.mean(np.abs(error)))
    bias = float(np.mean(error))

    # Pearson correlation
    std_t = np.std(y_t)
    std_p = np.std(y_p)
    if std_t > 1e-6 and std_p > 1e-6:
        corr = float(np.corrcoef(y_t, y_p)[0, 1])
    else:
        corr = 0.0

    return {
        "rmse": round(rmse, 3),
        "mae": round(mae, 3),
        "bias": round(bias, 3),
        "corr": round(corr, 3),
        "count": int(n)
    }


def calculate_contingency_table(
    observed: np.ndarray, 
    forecast: np.ndarray, 
    threshold: float
) -> Dict[str, int]:
    """
    Constructs 2x2 contingency table for rain >= threshold:
    - Hits (a): Obs >= thr & Fct >= thr
    - False Alarms (b): Obs < thr & Fct >= thr
    - Misses (c): Obs >= thr & Fct < thr
    - Correct Negatives (d): Obs < thr & Fct < thr
    """
    obs_event = observed >= threshold
    fct_event = forecast >= threshold

    hits = int(np.sum(obs_event & fct_event))
    false_alarms = int(np.sum((~obs_event) & fct_event))
    misses = int(np.sum(obs_event & (~fct_event)))
    correct_negatives = int(np.sum((~obs_event) & (~fct_event)))

    return {
        "hits": hits,
        "false_alarms": false_alarms,
        "misses": misses,
        "correct_negatives": correct_negatives,
        "total": hits + false_alarms + misses + correct_negatives
    }


def calculate_categorical_metrics(
    observed: Union[np.ndarray, List[float]], 
    forecast: Union[np.ndarray, List[float]], 
    threshold: float = 25.0
) -> Dict[str, float]:
    """
    Computes categorical threshold metrics:
    - POD: Probability of Detection (Hit Rate) = a / (a + c)
    - FAR: False Alarm Ratio = b / (a + b)
    - CSI: Critical Success Index (Threat Score) = a / (a + b + c)
    - ETS: Equitable Threat Score = (a - a_ref) / (a + b + c - a_ref)
      where a_ref = (a + b)(a + c) / n
    """
    y_true = np.asarray(observed, dtype=np.float64)
    y_pred = np.asarray(forecast, dtype=np.float64)

    valid = np.isfinite(y_true) & np.isfinite(y_pred)
    if not np.any(valid):
        return {"pod": 0.0, "far": 0.0, "csi": 0.0, "ets": 0.0, "threshold": threshold}

    ct = calculate_contingency_table(y_true[valid], y_pred[valid], threshold)
    a = ct["hits"]
    b = ct["false_alarms"]
    c = ct["misses"]
    d = ct["correct_negatives"]
    n = ct["total"]

    # POD: hits / (hits + misses)
    pod = a / (a + c) if (a + c) > 0 else 0.0

    # FAR: false_alarms / (hits + false_alarms)
    far = b / (a + b) if (a + b) > 0 else 0.0

    # CSI: hits / (hits + false_alarms + misses)
    denom_csi = a + b + c
    csi = a / denom_csi if denom_csi > 0 else (1.0 if (a == 0 and b == 0 and c == 0) else 0.0)

    # ETS: (a - a_ref) / (a + b + c - a_ref)
    a_ref = ((a + b) * (a + c)) / n if n > 0 else 0.0
    denom_ets = (a + b + c - a_ref)
    if abs(denom_ets) > 1e-6:
        ets = (a - a_ref) / denom_ets
    else:
        ets = 0.0

    return {
        "pod": round(float(pod), 3),
        "far": round(float(far), 3),
        "csi": round(float(csi), 3),
        "ets": round(float(ets), 3),
        "hits": a,
        "false_alarms": b,
        "misses": c,
        "correct_negatives": d,
        "threshold": threshold
    }


def calculate_fractions_skill_score(
    observed: np.ndarray, 
    forecast: np.ndarray, 
    threshold: float = 25.0, 
    window_size: int = 3
) -> float:
    """
    Calculates spatial Fractions Skill Score (FSS) (Roberts and Lean, 2008).
    Supports 1D spatial district vectors or 2D grid fields.
    FSS = 1 - (MSE / MSE_ref)
    """
    obs = np.asarray(observed, dtype=np.float64)
    fct = np.asarray(forecast, dtype=np.float64)

    # Binary binary fields at threshold
    I_obs = (obs >= threshold).astype(np.float64)
    I_fct = (fct >= threshold).astype(np.float64)

    if I_obs.ndim == 1:
        # 1D sliding neighborhood window
        half_w = window_size // 2
        N = len(I_obs)
        frac_obs = np.zeros(N)
        frac_fct = np.zeros(N)
        for i in range(N):
            start = max(0, i - half_w)
            end = min(N, i + half_w + 1)
            frac_obs[i] = np.mean(I_obs[start:end])
            frac_fct[i] = np.mean(I_fct[start:end])
    elif I_obs.ndim == 2:
        from scipy.ndimage import uniform_filter
        frac_obs = uniform_filter(I_obs, size=window_size, mode="constant", cval=0.0)
        frac_fct = uniform_filter(I_fct, size=window_size, mode="constant", cval=0.0)
    else:
        return 0.0

    mse = np.mean((frac_fct - frac_obs) ** 2)
    mse_ref = np.mean(frac_fct ** 2) + np.mean(frac_obs ** 2)

    if mse_ref < 1e-9:
        # Both fields have 0 events in region -> perfect agreement on absence
        return 1.0

    fss = 1.0 - (mse / mse_ref)
    return round(float(max(0.0, min(1.0, fss))), 3)


def calculate_full_verification_suite(
    observed: Union[np.ndarray, List[float]], 
    raw_nwp: Union[np.ndarray, List[float]], 
    corrected: Union[np.ndarray, List[float]],
    thresholds: List[float] = [15.0, 25.0, 50.0, 100.0]
) -> Dict[str, Any]:
    """
    Executes complete verification comparing RAW NWP vs VARSHA-Q Corrected against Observations.
    Returns continuous metrics, threshold categorical metrics, and spatial FSS.
    """
    obs = np.asarray(observed, dtype=np.float64)
    nwp = np.asarray(raw_nwp, dtype=np.float64)
    cor = np.asarray(corrected, dtype=np.float64)

    # 1. Continuous
    cont_nwp = calculate_continuous_metrics(obs, nwp)
    cont_cor = calculate_continuous_metrics(obs, cor)

    # Compute percentage RMSE improvement (actual calculation!)
    if cont_nwp["rmse"] > 1e-6:
        rmse_reduction_pct = round(
            float((cont_nwp["rmse"] - cont_cor["rmse"]) / cont_nwp["rmse"] * 100.0), 1
        )
    else:
        rmse_reduction_pct = 0.0

    # 2. Categorical per threshold
    cat_nwp = {}
    cat_cor = {}
    fss_scores = {}

    for thr in thresholds:
        thr_key = f"{int(thr)}mm"
        cat_nwp[thr_key] = calculate_categorical_metrics(obs, nwp, threshold=thr)
        cat_cor[thr_key] = calculate_categorical_metrics(obs, cor, threshold=thr)
        fss_scores[thr_key] = {
            "raw_nwp": calculate_fractions_skill_score(obs, nwp, threshold=thr),
            "corrected": calculate_fractions_skill_score(obs, cor, threshold=thr)
        }

    return {
        "continuous": {
            "raw_nwp": cont_nwp,
            "corrected": cont_cor,
            "rmse_reduction_pct": rmse_reduction_pct
        },
        "thresholds": {
            thr_key: {
                "raw_nwp": cat_nwp[thr_key],
                "corrected": cat_cor[thr_key],
                "fss": fss_scores[thr_key]
            }
            for thr_key in cat_nwp
        }
    }
