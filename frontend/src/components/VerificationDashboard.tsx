import React from 'react';
import { FullVerification } from '../types';
import { Award, CheckCircle2, TrendingUp, BarChart2, ShieldCheck, FileCheck } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface VerificationDashboardProps {
  verificationData: FullVerification | null;
}

export const VerificationDashboard: React.FC<VerificationDashboardProps> = ({ verificationData }) => {
  if (!verificationData) {
    return (
      <section id="verification" className="py-16 border-b border-[#E7E2DA] bg-[#FAF8F5] text-center">
        <p className="text-[#78716C]">Awaiting verification dataset evaluation...</p>
      </section>
    );
  }

  const { overall, regime_wise, scientific_note } = verificationData;

  const comparisonBarData = regime_wise.map((r) => ({
    name: r.title,
    RawNWP: r.raw_rmse,
    VARSHA_Q: r.corrected_rmse,
  }));

  return (
    <section id="verification" className="py-16 border-b border-[#E7E2DA] bg-[#F5F2EB]/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="max-w-3xl mb-12">
          <span className="text-xs uppercase tracking-widest text-[#B85D3B] font-mono block mb-1">
            Empirical Validation
          </span>
          <h2 className="font-editorial text-3xl sm:text-4xl text-[#1C1917] font-normal mb-2">
            Scientific Verification Dashboard
          </h2>
          <p className="text-sm text-[#57534E] leading-relaxed">
            Standard continuous and categorical meteorological forecast verification metrics comparing raw numerical baseline against VARSHA-Q across all regimes.
          </p>
        </div>

        {/* Overall Benchmark Metric Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-10">
          <div className="bg-white border border-[#E7E2DA] p-4 rounded text-center">
            <span className="text-[10px] uppercase font-mono tracking-wider text-[#78716C] block mb-1">
              RMSE Reduction
            </span>
            <span className="text-2xl font-editorial font-bold text-[#B85D3B]">
              {overall.rmse_reduction_pct}%
            </span>
            <span className="text-[10px] text-[#57534E] block mt-1">Multi-regime pooled</span>
          </div>

          <div className="bg-white border border-[#E7E2DA] p-4 rounded text-center">
            <span className="text-[10px] uppercase font-mono tracking-wider text-[#78716C] block mb-1">
              CSI (&gt;25mm)
            </span>
            <span className="text-2xl font-editorial font-light text-[#1C1917]">
              {overall.csi_25.toFixed(3)}
            </span>
            <span className="text-[10px] text-[#78716C] block mt-1">Critical Success Index</span>
          </div>

          <div className="bg-white border border-[#E7E2DA] p-4 rounded text-center">
            <span className="text-[10px] uppercase font-mono tracking-wider text-[#78716C] block mb-1">
              POD (&gt;25mm)
            </span>
            <span className="text-2xl font-editorial font-light text-[#1C1917]">
              {overall.pod_25.toFixed(3)}
            </span>
            <span className="text-[10px] text-[#78716C] block mt-1">Probability of Detection</span>
          </div>

          <div className="bg-white border border-[#E7E2DA] p-4 rounded text-center">
            <span className="text-[10px] uppercase font-mono tracking-wider text-[#78716C] block mb-1">
              FAR (&gt;25mm)
            </span>
            <span className="text-2xl font-editorial font-light text-[#1C1917]">
              {overall.far_25.toFixed(3)}
            </span>
            <span className="text-[10px] text-[#78716C] block mt-1">False Alarm Ratio</span>
          </div>

          <div className="bg-white border border-[#E7E2DA] p-4 rounded text-center">
            <span className="text-[10px] uppercase font-mono tracking-wider text-[#78716C] block mb-1">
              ETS (&gt;25mm)
            </span>
            <span className="text-2xl font-editorial font-light text-[#1C1917]">
              {overall.ets_25.toFixed(3)}
            </span>
            <span className="text-[10px] text-[#78716C] block mt-1">Equitable Threat Score</span>
          </div>

          <div className="bg-white border border-[#E7E2DA] p-4 rounded text-center">
            <span className="text-[10px] uppercase font-mono tracking-wider text-[#78716C] block mb-1">
              FSS (&gt;25mm)
            </span>
            <span className="text-2xl font-editorial font-light text-[#1C1917]">
              {overall.fss_25.toFixed(3)}
            </span>
            <span className="text-[10px] text-[#78716C] block mt-1">Fractions Skill Score</span>
          </div>
        </div>

        {/* Regime-Wise Comparison Table */}
        <div className="bg-white border border-[#E7E2DA] rounded overflow-hidden shadow-sm mb-10">
          <div className="p-4 border-b border-[#E7E2DA] bg-[#FAF8F5] flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <FileCheck className="w-4 h-4 text-[#B85D3B]" />
              <span className="text-sm font-medium text-[#1C1917]">
                Regime-Specific Verification Breakdown
              </span>
            </div>
            <span className="text-xs font-mono text-[#78716C]">
              Evaluation Samples: {overall.total_samples}
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#F5F2EB]/80 border-b border-[#E7E2DA] text-[#57534E] uppercase tracking-wider font-mono text-[10px]">
                <tr>
                  <th className="py-2.5 px-4">Weather Regime</th>
                  <th className="py-2.5 px-3">Samples</th>
                  <th className="py-2.5 px-3">Raw NWP RMSE</th>
                  <th className="py-2.5 px-3 text-[#B85D3B] font-semibold">VARSHA-Q RMSE</th>
                  <th className="py-2.5 px-3 text-emerald-800 font-semibold">RMSE Red %</th>
                  <th className="py-2.5 px-3">CSI (&gt;25mm)</th>
                  <th className="py-2.5 px-3">POD</th>
                  <th className="py-2.5 px-3">FAR</th>
                  <th className="py-2.5 px-3">ETS</th>
                  <th className="py-2.5 px-3">FSS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E7E2DA]">
                {regime_wise.map((row) => (
                  <tr key={row.regime} className="hover:bg-[#FAF8F5] transition-colors">
                    <td className="py-3 px-4 font-medium text-[#1C1917]">{row.title}</td>
                    <td className="py-3 px-3 font-mono text-[#78716C]">{row.sample_count}</td>
                    <td className="py-3 px-3 font-mono text-[#78716C]">{row.raw_rmse.toFixed(2)} mm</td>
                    <td className="py-3 px-3 font-mono font-bold text-[#B85D3B]">{row.corrected_rmse.toFixed(2)} mm</td>
                    <td className="py-3 px-3 font-mono font-semibold text-emerald-700 bg-emerald-50/50">
                      +{row.rmse_reduction_pct.toFixed(1)}%
                    </td>
                    <td className="py-3 px-3 font-mono">{row.csi_25.toFixed(3)}</td>
                    <td className="py-3 px-3 font-mono">{row.pod_25.toFixed(3)}</td>
                    <td className="py-3 px-3 font-mono">{row.far_25.toFixed(3)}</td>
                    <td className="py-3 px-3 font-mono">{row.ets_25.toFixed(3)}</td>
                    <td className="py-3 px-3 font-mono">{row.fss_25.toFixed(3)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* RMSE Comparison Bar Chart */}
        <div className="bg-white border border-[#E7E2DA] p-6 rounded">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h4 className="font-editorial text-lg text-[#1C1917] font-normal">
                Continuous Error (RMSE in mm) Across Regimes
              </h4>
              <span className="text-xs text-[#78716C]">
                Lower RMSE indicates superior forecast accuracy against observed precipitation
              </span>
            </div>
          </div>

          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparisonBarData} margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
                <XAxis dataKey="name" stroke="#78716C" fontSize={11} tickLine={false} />
                <YAxis stroke="#78716C" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#FAF8F5',
                    borderColor: '#E7E2DA',
                    fontSize: '12px',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', fontFamily: 'Inter' }} />
                <Bar dataKey="RawNWP" fill="#A8A29E" name="Raw NWP Forecast" radius={[2, 2, 0, 0]} />
                <Bar dataKey="VARSHA_Q" fill="#B85D3B" name="VARSHA-Q Bias Corrected" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="mt-4 pt-3 border-t border-[#E7E2DA] text-[11px] text-[#78716C] italic font-sans text-center">
            {scientific_note}
          </div>
        </div>

      </div>
    </section>
  );
};
