import React, { useState } from 'react';
import { ForecastResponse, DistrictForecast } from '../types';
import { ShieldAlert, BarChart3, Info, ChevronRight } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface HeavyRainProbabilitySectionProps {
  forecast: ForecastResponse | null;
  onSelectDistrict: (district: DistrictForecast) => void;
}

export const HeavyRainProbabilitySection: React.FC<HeavyRainProbabilitySectionProps> = ({
  forecast,
  onSelectDistrict,
}) => {
  if (!forecast) return null;

  const districts = forecast.district_forecasts;
  const [selectedThreshold, setSelectedThreshold] = useState<'p_gt_25mm' | 'p_gt_50mm' | 'p_gt_100mm'>('p_gt_50mm');

  // Top 8 highest risk districts for selected threshold
  const sortedDistricts = [...districts].sort(
    (a, b) => (b.heavy_rain_probabilities[selectedThreshold] || 0) - (a.heavy_rain_probabilities[selectedThreshold] || 0)
  ).slice(0, 8);

  const barData = sortedDistricts.map((d) => ({
    name: d.name,
    prob: Math.round((d.heavy_rain_probabilities[selectedThreshold] || 0) * 100),
    rainfall: d.corrected_rainfall_mm,
    risk: d.risk_category,
    rawDistrict: d,
  }));

  const thresholdLabels = {
    p_gt_25mm: '> 25 mm (Rather Heavy)',
    p_gt_50mm: '> 50 mm (Heavy Rainfall)',
    p_gt_100mm: '> 100 mm (Very Heavy)',
  };

  return (
    <section className="py-16 border-b border-[#E7E2DA] bg-[#F5F2EB]/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-10 pb-6 border-b border-[#E7E2DA]">
          <div className="max-w-2xl">
            <span className="text-xs uppercase tracking-widest text-[#B85D3B] font-mono block mb-1">
              Probabilistic Assessment
            </span>
            <h2 className="font-editorial text-3xl sm:text-4xl text-[#1C1917] font-normal mb-2">
              Heavy Rain Exceedance Probabilities
            </h2>
            <p className="text-xs sm:text-sm text-[#57534E]">
              Deterministic point rainfall predictions miss tail risks. VARSHA-Q evaluates calibrated heteroscedastic probability curves conditioned on synoptic regime variance and uncertainty intervals.
            </p>
          </div>

          {/* Threshold Switcher */}
          <div className="mt-4 md:mt-0 flex rounded border border-[#E7E2DA] bg-white p-0.5 text-xs font-mono">
            {(['p_gt_25mm', 'p_gt_50mm', 'p_gt_100mm'] as const).map((key) => (
              <button
                key={key}
                onClick={() => setSelectedThreshold(key)}
                className={`px-3 py-1.5 rounded-sm transition-all ${
                  selectedThreshold === key ? 'bg-[#1C1917] text-white' : 'text-[#78716C] hover:text-[#1C1917]'
                }`}
              >
                {thresholdLabels[key]}
              </button>
            ))}
          </div>
        </div>

        {/* Chart + Risk Breakdown Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Bar Chart: Top Districts Probabilities (8 cols) */}
          <div className="lg:col-span-8 bg-white border border-[#E7E2DA] p-6 rounded shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono uppercase tracking-wider text-[#78716C]">
                Exceedance Probability (%) for {thresholdLabels[selectedThreshold]}
              </span>
              <span className="text-xs text-[#78716C]">
                Top 8 Vulnerable Districts
              </span>
            </div>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <XAxis
                    dataKey="name"
                    stroke="#78716C"
                    fontSize={11}
                    tickLine={false}
                    interval={0}
                    angle={-20}
                    textAnchor="end"
                  />
                  <YAxis stroke="#78716C" fontSize={11} tickLine={false} domain={[0, 100]} />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const item = payload[0].payload;
                        return (
                          <div className="bg-[#FAF8F5] border border-[#E7E2DA] p-2.5 rounded text-xs shadow-md">
                            <strong className="block text-[#1C1917]">{item.name}</strong>
                            <div className="text-[#B85D3B]">Exceedance: {item.prob}%</div>
                            <div className="text-[#78716C]">Forecast: {item.rainfall} mm</div>
                            <div className="text-[#57534E] text-[10px] mt-1 font-mono">
                              Risk: {item.risk}
                            </div>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Bar dataKey="prob" radius={[3, 3, 0, 0]}>
                    {barData.map((entry, index) => {
                      const color =
                        entry.prob >= 60 ? '#B85D3B' : entry.prob >= 35 ? '#CE7856' : '#4B7B94';
                      return <Cell key={`cell-${index}`} fill={color} />;
                    })}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="mt-4 pt-3 border-t border-[#E7E2DA] text-[11px] text-[#78716C] flex items-center justify-between">
              <span>Color coding: Terracotta (&ge;60%), Clay (&ge;35%), Atmospheric Blue (&lt;35%)</span>
              <span className="font-mono text-[10px]">Model-Derived Tail Exceedance</span>
            </div>
          </div>

          {/* Uncertainty & Risk Category Card (4 cols) */}
          <div className="lg:col-span-4 bg-white border border-[#E7E2DA] p-6 rounded shadow-sm">
            <div className="flex items-center space-x-2 text-xs font-mono uppercase tracking-wider text-[#78716C] mb-3">
              <ShieldAlert className="w-4 h-4 text-[#B85D3B]" />
              <span>Model Risk Categories</span>
            </div>

            <p className="text-xs text-[#57534E] leading-relaxed mb-4">
              Thresholds categorize hydrometeorological threat levels derived purely from calibrated exceedance probability and expected accumulation:
            </p>

            <div className="space-y-2 mb-6">
              <div className="p-2 rounded bg-rose-50 border border-rose-200 text-xs">
                <span className="font-bold text-rose-900 block font-mono">VERY HIGH RISK</span>
                <span className="text-[11px] text-rose-700">Rain &ge; 100mm or P(&gt;100mm) &ge; 40%</span>
              </div>
              <div className="p-2 rounded bg-orange-50 border border-orange-200 text-xs">
                <span className="font-bold text-orange-900 block font-mono">HIGH RISK</span>
                <span className="text-[11px] text-orange-700">Rain &ge; 50mm or P(&gt;50mm) &ge; 45%</span>
              </div>
              <div className="p-2 rounded bg-amber-50 border border-amber-200 text-xs">
                <span className="font-bold text-amber-900 block font-mono">MODERATE RISK</span>
                <span className="text-[11px] text-amber-700">Rain &ge; 25mm or P(&gt;50mm) &ge; 20%</span>
              </div>
              <div className="p-2 rounded bg-emerald-50 border border-emerald-200 text-xs">
                <span className="font-bold text-emerald-900 block font-mono">LOW RISK</span>
                <span className="text-[11px] text-emerald-700">Routine or light precipitation</span>
              </div>
            </div>

            <div className="p-3 bg-[#FAF8F5] border border-[#E7E2DA] rounded text-[11px] text-[#78716C]">
              <strong className="text-[#1C1917]">Note on Uncertainty:</strong> Each district forecast outputs [P10, P50, P90] quantile intervals representing model + atmospheric spread.
            </div>
          </div>

        </div>

      </div>
    </section>
  );
};
