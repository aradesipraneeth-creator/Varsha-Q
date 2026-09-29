export interface UncertaintyInterval {
  lower_bound_p10_mm: number;
  median_p50_mm: number;
  upper_bound_p90_mm: number;
  uncertainty_spread_mm: number;
  uncertainty_level: 'LOW' | 'MODERATE' | 'HIGH';
}

export interface HeavyRainProbabilities {
  p_gt_15mm?: number;
  p_gt_25mm: number;
  p_gt_50mm: number;
  p_gt_100mm: number;
  p_gt_150mm?: number;
}

export interface DistrictForecast {
  district_id: string;
  name: string;
  state: string;
  lat: number;
  lon: number;
  elevation_m: number;
  coastal_dist_km: number;
  raw_nwp_rainfall_mm: number;
  corrected_rainfall_mm: number;
  delta_mm: number;
  observed_rainfall_mm?: number;
  regime: string;
  heavy_rain_probabilities: HeavyRainProbabilities;
  uncertainty: UncertaintyInterval;
  risk_category: 'LOW' | 'MODERATE' | 'HIGH' | 'VERY HIGH';
  risk_label: string;
}

export interface FeatureImpact {
  feature: string;
  importance: number;
  value: number;
}

export interface RegimeIntelligence {
  regime: string;
  title: string;
  confidence: number;
  probabilities: Record<string, number>;
  description: string;
  key_indicators: string[];
  feature_contributions: FeatureImpact[];
}

export interface ForecastResponse {
  run_id?: number;
  timestamp: string;
  mode: string;
  provenance: {
    source: string;
    mode: string;
    disclaimer: string;
    valid_time: string;
    cycle?: string;
    scenario?: string;
  };
  regime_intelligence: RegimeIntelligence;
  correction_summary: {
    strategy: string;
    is_fallback: boolean;
    fallback_reason: string;
    mean_nwp_mm: number;
    mean_corrected_mm: number;
    mean_delta_mm: number;
  };
  spatiotemporal_representation: {
    device: string;
    num_districts: number;
    temporal_embedding_dim: number;
    spatial_embedding_dim: number;
    fused_embedding_dim: number;
  };
  district_forecasts: DistrictForecast[];
  verification?: {
    continuous: {
      raw_nwp: { rmse: number; mae: number; bias: number; corr: number; count: number };
      corrected: { rmse: number; mae: number; bias: number; corr: number; count: number };
      rmse_reduction_pct: number;
    };
    thresholds: Record<string, {
      raw_nwp: { pod: number; far: number; csi: number; ets: number };
      corrected: { pod: number; far: number; csi: number; ets: number };
      fss: { raw_nwp: number; corrected: number };
    }>;
  };
}

export interface SystemStatus {
  project_name: string;
  full_title: string;
  version: string;
  team: string;
  problem_statement: string;
  mode: string;
  device: string;
  active_scenario?: string;
  is_healthy: boolean;
  data_sources: Record<string, any>;
  models_status: Record<string, string>;
  last_update: string;
}

export interface OptimizationBenchmark {
  status: string;
  scientific_disclaimer: string;
  classical_baseline: {
    name: string;
    objective_energy: number;
    selected_features: string[];
    num_selected: number;
    runtime_ms: number;
    convergence: Array<{ step: number; temp: number; energy: number }>;
  };
  quantum_inspired: {
    name: string;
    objective_energy: number;
    selected_features: string[];
    num_selected: number;
    runtime_ms: number;
    convergence: Array<{ sweep: number; gamma: number; energy: number }>;
  };
  energy_delta: number;
  qubo_dimension: number;
}

export interface RegimeEvaluation {
  regime: string;
  title: string;
  sample_count: number;
  raw_rmse: number;
  corrected_rmse: number;
  rmse_reduction_pct: number;
  csi_25: number;
  pod_25: number;
  far_25: number;
  ets_25: number;
  fss_25: number;
}

export interface FullVerification {
  status: string;
  scientific_note: string;
  overall: {
    total_samples: number;
    raw_nwp_rmse: number;
    corrected_rmse: number;
    rmse_reduction_pct: number;
    csi_25: number;
    pod_25: number;
    far_25: number;
    ets_25: number;
    fss_25: number;
  };
  regime_wise: RegimeEvaluation[];
}
