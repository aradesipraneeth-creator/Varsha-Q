import { SystemStatus, ForecastResponse, FullVerification, OptimizationBenchmark } from '../types';

const API_BASE = '/api';

export const api = {
  async getSystemStatus(): Promise<SystemStatus> {
    const res = await fetch(`${API_BASE}/system/status`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return res.json();
  },

  async getLatestForecast(): Promise<ForecastResponse> {
    const res = await fetch(`${API_BASE}/forecast/latest`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return res.json();
  },

  async getDistrictsGeoJson(): Promise<any> {
    const res = await fetch(`${API_BASE}/districts/geojson`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return res.json();
  },

  async getVerification(): Promise<FullVerification> {
    const res = await fetch(`${API_BASE}/verification`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return res.json();
  },

  async getOptimizationLatest(): Promise<OptimizationBenchmark> {
    const res = await fetch(`${API_BASE}/optimization/latest`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return res.json();
  },

  async runInference(scenario: string, mode?: string): Promise<ForecastResponse> {
    const params = new URLSearchParams({ scenario });
    if (mode) params.append('mode', mode);
    const res = await fetch(`${API_BASE}/inference/run?${params.toString()}`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return res.json();
  },

  async runOptimization(): Promise<OptimizationBenchmark> {
    const res = await fetch(`${API_BASE}/optimization/run`, { method: 'POST' });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return res.json();
  }
};
