import React, { useState } from 'react';
import { ForecastResponse, DistrictForecast } from '../types';
import { CloudRain, TrendingUp, TrendingDown, ArrowRight, ShieldCheck, Filter, Search } from 'lucide-react';

interface ForecastViewProps {
  forecast: ForecastResponse | null;
  selectedState: string;
  onSelectState: (state: string) => void;
  onSelectDistrict: (district: DistrictForecast) => void;
}

export const ForecastView: React.FC<ForecastViewProps> = ({
  forecast,
  selectedState,
  onSelectState,
  onSelectDistrict,
}) => {
  const [activeTab, setActiveTab] = useState<'comparison' | 'table'>('comparison');
  const [searchQuery, setSearchQuery] = useState('');
  const [horizon, setHorizon] = useState<'24h' | '48h' | '72h'>('24h');

  if (!forecast) {
    return (
      <div className="py-20 text-center text-[#78716C]">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-[#B85D3B] mb-4" />
        <p className="font-editorial text-xl">Loading meteorological forecast tensors...</p>
      </div>
    );
  }

  const allDistricts = forecast.district_forecasts;
  const states = ['All India', 'Andhra Pradesh', 'Odisha', 'Telangana', 'Kerala', 'Maharashtra', 'West Bengal', 'Assam', 'Meghalaya', 'Rajasthan', 'Gujarat', 'Madhya Pradesh'];

  const filteredDistricts = allDistricts.filter((d) => {
    const matchesState = selectedState === 'All India' || d.state.toLowerCase() === selectedState.toLowerCase();
    const matchesSearch = d.name.toLowerCase().includes(searchQuery.toLowerCase()) || d.state.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesState && matchesSearch;
  });

  const summary = forecast.correction_summary;
  const verification = forecast.verification?.continuous;

  return (
    <section id="forecast" className="py-16 border-b border-[#E7E2DA] bg-[#FAF8F5]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-10 pb-6 border-b border-[#E7E2DA]">
          <div>
            <span className="text-xs uppercase tracking-widest text-[#B85D3B] font-mono block mb-1">
              Forecast Workspace
            </span>
            <h2 className="font-editorial text-3xl sm:text-4xl text-[#1C1917] font-normal">
              Raw NWP vs. VARSHA-Q Corrected
            </h2>
          </div>

          {/* Horizon & State Selectors */}
          <div className="mt-4 md:mt-0 flex flex-wrap items-center gap-3">
            {/* Horizon */}
            <div className="inline-flex rounded border border-[#E7E2DA] bg-white p-0.5 text-xs font-mono">
              {(['24h', '48h', '72h'] as const).map((h) => (
                <button
                  key={h}
                  onClick={() => setHorizon(h)}
                  className={`px-3 py-1 rounded-sm transition-all ${
                    horizon === h ? 'bg-[#1C1917] text-white' : 'text-[#78716C] hover:text-[#1C1917]'
                  }`}
                >
                  +{h}
                </button>
              ))}
            </div>

            {/* State filter */}
            <div className="relative">
              <select
                value={selectedState}
                onChange={(e) => onSelectState(e.target.value)}
                className="appearance-none bg-white border border-[#E7E2DA] rounded px-3 py-1.5 pr-8 text-xs font-medium text-[#1C1917] focus:outline-none focus:border-[#B85D3B]"
              >
                {states.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
              <Filter className="w-3 h-3 text-[#78716C] absolute right-2.5 top-2.5 pointer-events-none" />
            </div>
          </div>
        </div>

        {/* Highlight Metric Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
          <div className="bg-white border border-[#E7E2DA] p-5 rounded">
            <span className="text-xs uppercase tracking-wider text-[#78716C] font-mono block mb-1">
              Raw NWP Mean
            </span>
            <div className="flex items-baseline space-x-2">
              <span className="text-3xl font-light text-[#1C1917] font-editorial">
                {summary.mean_nwp_mm}
              </span>
              <span className="text-xs text-[#78716C]">mm</span>
            </div>
            <span className="text-[11px] text-[#A8A29E] mt-2 block">
              Coarse numerical baseline
            </span>
          </div>

          <div className="bg-white border border-[#E7E2DA] p-5 rounded">
            <span className="text-xs uppercase tracking-wider text-[#B85D3B] font-mono block mb-1">
              VARSHA-Q Mean
            </span>
            <div className="flex items-baseline space-x-2">
              <span className="text-3xl font-light text-[#B85D3B] font-editorial font-semibold">
                {summary.mean_corrected_mm}
              </span>
              <span className="text-xs text-[#B85D3B]">mm</span>
            </div>
            <span className="text-[11px] text-[#57534E] mt-2 block">
              Regime-adjusted prediction
            </span>
          </div>

          <div className="bg-white border border-[#E7E2DA] p-5 rounded">
            <span className="text-xs uppercase tracking-wider text-[#78716C] font-mono block mb-1">
              Mean Bias Correction
            </span>
            <div className="flex items-baseline space-x-2">
              <span className="text-3xl font-light text-[#1C1917] font-editorial">
                {summary.mean_delta_mm > 0 ? `+${summary.mean_delta_mm}` : summary.mean_delta_mm}
              </span>
              <span className="text-xs text-[#78716C]">mm</span>
            </div>
            <div className="flex items-center space-x-1 mt-2 text-[11px] text-[#57534E]">
              {summary.mean_delta_mm > 0 ? (
                <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />
              ) : (
                <TrendingDown className="w-3.5 h-3.5 text-amber-600" />
              )}
              <span>Systematic error offset</span>
            </div>
          </div>

          <div className="bg-white border border-[#E7E2DA] p-5 rounded">
            <span className="text-xs uppercase tracking-wider text-[#78716C] font-mono block mb-1">
              Active Strategy
            </span>
            <div className="text-sm font-medium text-[#1C1917] truncate mt-1">
              {summary.strategy}
            </div>
            <span className="text-[11px] text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200 mt-2 inline-block">
              {verification ? `${verification.rmse_reduction_pct}% RMSE Reduction` : 'Calibrated'}
            </span>
          </div>
        </div>

        {/* District Forecast Table with Search */}
        <div className="bg-white border border-[#E7E2DA] rounded overflow-hidden shadow-sm">
          <div className="p-4 border-b border-[#E7E2DA] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center space-x-2">
              <CloudRain className="w-4 h-4 text-[#B85D3B]" />
              <span className="text-sm font-medium text-[#1C1917]">
                District Rainfall Intelligence ({filteredDistricts.length} districts)
              </span>
            </div>

            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search district or state..."
                className="pl-8 pr-3 py-1 text-xs border border-[#E7E2DA] rounded w-56 focus:outline-none focus:border-[#B85D3B]"
              />
              <Search className="w-3.5 h-3.5 text-[#78716C] absolute left-2.5 top-2 pointer-events-none" />
            </div>
          </div>

          <div className="overflow-x-auto max-h-[460px] overflow-y-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#F5F2EB]/80 sticky top-0 border-b border-[#E7E2DA] text-[#57534E] uppercase tracking-wider font-mono text-[10px]">
                <tr>
                  <th className="py-2.5 px-4">District</th>
                  <th className="py-2.5 px-3">State</th>
                  <th className="py-2.5 px-3">Raw NWP</th>
                  <th className="py-2.5 px-3 text-[#B85D3B] font-semibold">VARSHA-Q</th>
                  <th className="py-2.5 px-3">Delta</th>
                  <th className="py-2.5 px-3">P(&gt;50mm)</th>
                  <th className="py-2.5 px-3">Uncertainty</th>
                  <th className="py-2.5 px-3">Model Risk</th>
                  <th className="py-2.5 px-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E7E2DA]">
                {filteredDistricts.map((d) => {
                  const p50 = d.heavy_rain_probabilities.p_gt_50mm || 0;
                  const riskBg =
                    d.risk_category === 'VERY HIGH'
                      ? 'bg-rose-100 text-rose-800'
                      : d.risk_category === 'HIGH'
                      ? 'bg-orange-100 text-orange-800'
                      : d.risk_category === 'MODERATE'
                      ? 'bg-amber-100 text-amber-800'
                      : 'bg-emerald-50 text-emerald-800';

                  return (
                    <tr
                      key={d.district_id}
                      className="hover:bg-[#FAF8F5] transition-colors cursor-pointer"
                      onClick={() => onSelectDistrict(d)}
                    >
                      <td className="py-2.5 px-4 font-medium text-[#1C1917]">{d.name}</td>
                      <td className="py-2.5 px-3 text-[#57534E]">{d.state}</td>
                      <td className="py-2.5 px-3 font-mono text-[#78716C]">{d.raw_nwp_rainfall_mm} mm</td>
                      <td className="py-2.5 px-3 font-mono text-[#B85D3B] font-bold">{d.corrected_rainfall_mm} mm</td>
                      <td className="py-2.5 px-3 font-mono">
                        <span className={d.delta_mm >= 0 ? 'text-emerald-700' : 'text-amber-700'}>
                          {d.delta_mm >= 0 ? `+${d.delta_mm}` : d.delta_mm} mm
                        </span>
                      </td>
                      <td className="py-2.5 px-3 font-mono font-medium">
                        {(p50 * 100).toFixed(0)}%
                      </td>
                      <td className="py-2.5 px-3 text-[11px] text-[#78716C]">
                        {d.uncertainty.uncertainty_level} (±{d.uncertainty.uncertainty_spread_mm} mm)
                      </td>
                      <td className="py-2.5 px-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-semibold tracking-wide ${riskBg}`}>
                          {d.risk_category}
                        </span>
                      </td>
                      <td className="py-2.5 px-3">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectDistrict(d);
                          }}
                          className="text-[#B85D3B] hover:text-[#9C4729] font-medium text-xs inline-flex items-center gap-1"
                        >
                          <span>Inspect</span>
                          <ArrowRight className="w-3 h-3" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <div className="p-3 bg-[#FAF8F5] border-t border-[#E7E2DA] text-[11px] text-[#78716C] flex justify-between items-center">
            <span>Showing {filteredDistricts.length} of {allDistricts.length} districts</span>
            <span className="italic font-sans">Click on any district row to view exceedance curves and physical attribution.</span>
          </div>
        </div>

      </div>
    </section>
  );
};
