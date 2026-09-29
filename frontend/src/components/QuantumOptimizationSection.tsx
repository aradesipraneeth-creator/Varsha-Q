import React, { useState } from 'react';
import { OptimizationBenchmark } from '../types';
import { Cpu, Zap, RotateCcw, AlertCircle, CheckCircle2, Sliders, ArrowRight } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

interface QuantumOptimizationSectionProps {
  benchmarkData: OptimizationBenchmark | null;
  onRunBenchmark: () => Promise<void>;
  isLoading: boolean;
}

export const QuantumOptimizationSection: React.FC<QuantumOptimizationSectionProps> = ({
  benchmarkData,
  onRunBenchmark,
  isLoading,
}) => {
  if (!benchmarkData) return null;

  const csa = benchmarkData.classical_baseline;
  const sqa = benchmarkData.quantum_inspired;

  // Merge convergence data for comparison chart
  const chartData = sqa.convergence.map((sItem, idx) => {
    const cItem = csa.convergence[idx] || csa.convergence[csa.convergence.length - 1];
    return {
      iteration: idx + 1,
      sqaEnergy: sItem.energy,
      csaEnergy: cItem ? cItem.energy : sItem.energy,
    };
  });

  return (
    <section id="optimization" className="py-16 border-b border-[#E7E2DA] bg-[#FAF8F5]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="max-w-3xl mb-12">
          <span className="text-xs uppercase tracking-widest text-[#B85D3B] font-mono block mb-1">
            Combinatorial Search
          </span>
          <h2 className="font-editorial text-3xl sm:text-4xl text-[#1C1917] font-normal mb-2">
            Quantum-Inspired Optimization
          </h2>
          <h3 className="text-lg text-[#B85D3B] font-serif italic mb-4">
            Search the configuration space &mdash; not the atmosphere.
          </h3>
          <p className="text-sm text-[#57534E] leading-relaxed">
            Quantum-inspired search is used to efficiently explore candidate model configurations for forecast post-processing. 
            By mapping feature subset selection onto a Quadratic Unconstrained Binary Optimization (QUBO) Hamiltonian, 
            Simulated Quantum Annealing leverages quantum tunneling dynamics to escape local energy minima.
          </p>
        </div>

        {/* Scientific Framing Banner */}
        <div className="bg-[#F5F2EB] border border-[#E7E2DA] p-4 rounded mb-10 text-xs text-[#57534E] flex items-start gap-3">
          <AlertCircle className="w-4 h-4 text-[#B85D3B] shrink-0 mt-0.5" />
          <div className="leading-relaxed">
            <strong className="text-[#1C1917]">Rigorous Scientific Positioning:</strong> Quantum computing does <em>not</em> predict rainfall. 
            Quantum-inspired optimization is strictly an optimization component exploring the combinatorial configuration space (feature selection and loss weights). 
            Runs on classical hardware via Path-Integral Monte Carlo with Trotter replicas.
          </div>
        </div>

        {/* Benchmark Control Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 pb-4 border-b border-[#E7E2DA]">
          <div>
            <span className="font-mono text-xs uppercase tracking-wider text-[#78716C]">
              Active Problem: QUBO Binary Feature Selection (Dim: {benchmarkData.qubo_dimension}&times;{benchmarkData.qubo_dimension})
            </span>
            <div className="text-xs text-[#1C1917]">
              Energy Delta: <strong className="font-mono">{benchmarkData.energy_delta > 0 ? `+${benchmarkData.energy_delta}` : benchmarkData.energy_delta}</strong>
            </div>
          </div>

          <button
            onClick={onRunBenchmark}
            disabled={isLoading}
            className="inline-flex items-center space-x-2 px-4 py-2 rounded bg-[#1C1917] hover:bg-[#292524] text-white text-xs font-medium tracking-wide transition-all disabled:opacity-50"
          >
            <RotateCcw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>{isLoading ? 'Annealing Replicas...' : 'Re-Run Optimization Benchmark'}</span>
          </button>
        </div>

        {/* Side-by-Side Comparison: Classical vs Quantum-Inspired */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          
          {/* Classical Baseline (CSA) */}
          <div className="bg-white border border-[#E7E2DA] p-6 rounded relative">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono uppercase tracking-wider text-[#78716C]">
                Classical Baseline
              </span>
              <span className="text-xs font-mono text-[#78716C] bg-[#FAF8F5] px-2 py-0.5 rounded border border-[#E7E2DA]">
                {csa.runtime_ms} ms
              </span>
            </div>

            <h4 className="font-editorial text-xl text-[#1C1917] font-normal mb-1">
              {csa.name}
            </h4>
            <p className="text-xs text-[#78716C] mb-4">
              Standard thermal Metropolis-Hastings dynamics subject to thermal barrier trapping.
            </p>

            <div className="flex items-baseline space-x-2 mb-6">
              <span className="text-xs font-mono text-[#78716C]">Best Energy:</span>
              <span className="text-2xl font-mono font-light text-[#1C1917]">
                {csa.objective_energy}
              </span>
            </div>

            <div>
              <span className="text-[11px] font-mono uppercase tracking-wider text-[#78716C] block mb-2">
                Selected Features ({csa.num_selected}):
              </span>
              <div className="flex flex-wrap gap-1.5">
                {csa.selected_features.map((feat) => (
                  <span
                    key={feat}
                    className="px-2 py-0.5 rounded bg-[#FAF8F5] border border-[#E7E2DA] text-[11px] font-mono text-[#44403C]"
                  >
                    {feat}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Quantum-Inspired (SQA) */}
          <div className="bg-white border-2 border-[#B85D3B]/40 p-6 rounded relative shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono uppercase tracking-wider text-[#B85D3B] font-semibold">
                Quantum-Inspired Algorithm
              </span>
              <span className="text-xs font-mono text-[#B85D3B] bg-[#FBF2EE] px-2 py-0.5 rounded border border-[#EEC7B7]">
                {sqa.runtime_ms} ms
              </span>
            </div>

            <h4 className="font-editorial text-xl text-[#1C1917] font-normal mb-1">
              {sqa.name}
            </h4>
            <p className="text-xs text-[#78716C] mb-4">
              Transverse-field quantum tunneling across 8 Trotter replicas escaping local minima.
            </p>

            <div className="flex items-baseline space-x-2 mb-6">
              <span className="text-xs font-mono text-[#78716C]">Best Energy:</span>
              <span className="text-2xl font-mono font-bold text-[#B85D3B]">
                {sqa.objective_energy}
              </span>
            </div>

            <div>
              <span className="text-[11px] font-mono uppercase tracking-wider text-[#B85D3B] font-semibold block mb-2">
                Selected Features ({sqa.num_selected}):
              </span>
              <div className="flex flex-wrap gap-1.5">
                {sqa.selected_features.map((feat) => (
                  <span
                    key={feat}
                    className="px-2 py-0.5 rounded bg-[#FBF2EE] border border-[#EEC7B7] text-[11px] font-mono text-[#9C4729] font-medium"
                  >
                    {feat}
                  </span>
                ))}
              </div>
            </div>
          </div>

        </div>

        {/* Convergence Trajectory Chart */}
        <div className="bg-white border border-[#E7E2DA] p-6 rounded">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h4 className="font-editorial text-lg text-[#1C1917] font-normal">
                Annealing Energy Trajectory Comparison
              </h4>
              <span className="text-xs text-[#78716C]">
                Objective energy minimization over normalized annealing sweeps
              </span>
            </div>
            <div className="flex items-center space-x-4 text-xs font-mono">
              <div className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#B85D3B]" />
                <span>Simulated Quantum Annealing</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#78716C]" />
                <span>Classical Annealing</span>
              </div>
            </div>
          </div>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <XAxis dataKey="iteration" stroke="#A8A29E" fontSize={11} tickLine={false} />
                <YAxis stroke="#A8A29E" fontSize={11} tickLine={false} domain={['auto', 'auto']} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#FAF8F5',
                    borderColor: '#E7E2DA',
                    fontSize: '12px',
                    fontFamily: 'Inter',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="sqaEnergy"
                  stroke="#B85D3B"
                  strokeWidth={2}
                  dot={false}
                  name="Quantum-Inspired (SQA)"
                />
                <Line
                  type="monotone"
                  dataKey="csaEnergy"
                  stroke="#78716C"
                  strokeWidth={1.5}
                  strokeDasharray="4 4"
                  dot={false}
                  name="Classical Baseline (CSA)"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="mt-4 pt-3 border-t border-[#E7E2DA] text-[11px] text-[#78716C] italic font-sans text-center">
            {benchmarkData.scientific_disclaimer}
          </div>
        </div>

      </div>
    </section>
  );
};
