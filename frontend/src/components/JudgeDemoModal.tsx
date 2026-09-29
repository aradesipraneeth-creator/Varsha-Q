import React, { useState, useEffect } from 'react';
import { X, Play, CheckCircle2, Loader2, ArrowRight, Sparkles, AlertCircle } from 'lucide-react';
import { ForecastResponse } from '../types';

interface JudgeDemoModalProps {
  isOpen: boolean;
  onClose: () => void;
  onRunDemo: (scenario: string) => Promise<ForecastResponse>;
  currentScenario: string;
}

export const JudgeDemoModal: React.FC<JudgeDemoModalProps> = ({
  isOpen,
  onClose,
  onRunDemo,
  currentScenario,
}) => {
  const [selectedScenario, setSelectedScenario] = useState<string>(currentScenario || 'OROGRAPHIC');
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [currentStageIndex, setCurrentStageIndex] = useState<number>(-1);
  const [demoResult, setDemoResult] = useState<ForecastResponse | null>(null);

  useEffect(() => {
    if (isOpen) {
      setSelectedScenario(currentScenario || 'OROGRAPHIC');
      setDemoResult(null);
      setCurrentStageIndex(-1);
      setIsRunning(false);
    }
  }, [isOpen, currentScenario]);

  if (!isOpen) return null;

  const stages = [
    { id: 'INGESTING', label: '1. Meteorological Data Ingestion', desc: 'Ingesting GFS NWP grids, SRTM elevation, & rain gauges' },
    { id: 'ANALYZING', label: '2. Spatiotemporal AI (LNN + GNN)', desc: 'Continuous-time ODE dynamics & district graph message passing' },
    { id: 'CLASSIFYING', label: '3. Weather Regime Classification', desc: 'Predicting synoptic regime & calibrated confidence BEFORE correction' },
    { id: 'CORRECTING', label: '4. Regime-Specific Bias Correction', desc: 'Applying regime-specialized gradient boosted estimator' },
    { id: 'OPTIMIZING', label: '5. Quantum-Inspired Optimization', desc: 'Simulated Quantum Annealing over QUBO feature Hamiltonian' },
    { id: 'QUANTIFYING', label: '6. Heavy Rain Probability & Bounds', desc: 'Quantile uncertainty (P10/P50/P90) & operational exceedance' },
    { id: 'VERIFYING', label: '7. Scientific Verification Suite', desc: 'Evaluating RMSE, CSI, POD, FAR, ETS, & spatial FSS' },
  ];

  const scenarios = [
    { id: 'OROGRAPHIC', name: 'Orographic Rainfall', note: 'Extreme Western Ghats lifting; NWP underestimates steep terrain' },
    { id: 'DEPRESSION_LOW', name: 'Depression / Low', note: 'Bay of Bengal cyclonic storm; severe core rainfall bias' },
    { id: 'ACTIVE_MONSOON', name: 'Active Monsoon', note: 'Widespread convective trough across Central & Peninsular India' },
    { id: 'BREAK_MONSOON', name: 'Break Monsoon', note: 'Trough shifts to foothills; NWP false-alarm rain over dry south' },
    { id: 'COASTAL', name: 'Coastal Rainfall', note: 'Sea-breeze diurnal convergence along marine boundary' },
  ];

  const handleStartDemo = async () => {
    setIsRunning(true);
    setDemoResult(null);

    // Visibly cycle through pipeline animation stages
    for (let i = 0; i < stages.length; i++) {
      setCurrentStageIndex(i);
      await new Promise((resolve) => setTimeout(resolve, 380));
    }

    try {
      const result = await onRunDemo(selectedScenario);
      setDemoResult(result);
    } catch (err) {
      console.error('Demo run failed:', err);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn">
      <div className="bg-[#FAF8F5] border border-[#E7E2DA] rounded-lg shadow-2xl w-full max-w-3xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Modal Header */}
        <div className="p-6 bg-white border-b border-[#E7E2DA] flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-2 text-[11px] font-mono uppercase tracking-widest text-[#B85D3B] mb-1">
              <Sparkles className="w-3.5 h-3.5" />
              <span>SIH PS 26080 Evaluation Flow</span>
            </div>
            <h3 className="font-editorial text-2xl text-[#1C1917] font-normal">
              Judge Demonstration Mode
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-[#78716C] hover:text-[#1C1917] hover:bg-[#FAF8F5]"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          
          {/* Scenario Selection Cards */}
          <div>
            <span className="text-xs font-mono uppercase tracking-wider text-[#78716C] block mb-2.5">
              Select Controlled Demonstration Scenario:
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {scenarios.map((sc) => {
                const isSelected = selectedScenario === sc.id;
                return (
                  <div
                    key={sc.id}
                    onClick={() => !isRunning && setSelectedScenario(sc.id)}
                    className={`p-3 rounded border text-left cursor-pointer transition-all ${
                      isSelected
                        ? 'border-[#B85D3B] bg-[#FBF2EE] shadow-sm'
                        : 'border-[#E7E2DA] bg-white hover:border-[#DCD6CC]'
                    } ${isRunning ? 'pointer-events-none opacity-60' : ''}`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <strong className={`text-xs ${isSelected ? 'text-[#B85D3B]' : 'text-[#1C1917]'}`}>
                        {sc.name}
                      </strong>
                      {isSelected && <span className="w-2 h-2 rounded-full bg-[#B85D3B]" />}
                    </div>
                    <p className="text-[11px] text-[#57534E] leading-tight">
                      {sc.note}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Action Trigger Button */}
          {!isRunning && !demoResult && (
            <div className="text-center pt-2">
              <button
                onClick={handleStartDemo}
                className="inline-flex items-center space-x-2 px-8 py-3.5 rounded bg-[#B85D3B] hover:bg-[#9C4729] text-white text-sm font-medium tracking-wide shadow-md transition-all transform active:scale-95"
              >
                <Play className="w-4 h-4 fill-current" />
                <span>Execute End-to-End Pipeline</span>
              </button>
              <span className="text-[11px] text-[#78716C] block mt-2">
                Simulates real-time data ingestion, neural inference, and verification.
              </span>
            </div>
          )}

          {/* Pipeline Execution Animation Stages */}
          {isRunning && (
            <div className="bg-white border border-[#E7E2DA] p-5 rounded space-y-3">
              <span className="text-xs font-mono uppercase tracking-wider text-[#78716C] block mb-2">
                Live Pipeline Execution in Progress:
              </span>
              {stages.map((st, idx) => {
                const isDone = currentStageIndex > idx;
                const isCurrent = currentStageIndex === idx;

                return (
                  <div
                    key={st.id}
                    className={`flex items-center space-x-3 p-2 rounded transition-all text-xs ${
                      isCurrent
                        ? 'bg-[#FBF2EE] border border-[#EEC7B7]'
                        : isDone
                        ? 'text-[#1C1917]'
                        : 'text-[#A8A29E]'
                    }`}
                  >
                    {isDone ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                    ) : isCurrent ? (
                      <Loader2 className="w-4 h-4 text-[#B85D3B] animate-spin shrink-0" />
                    ) : (
                      <span className="w-4 h-4 rounded-full border border-[#DCD6CC] shrink-0" />
                    )}
                    <div className="flex-1">
                      <strong className={`block ${isCurrent ? 'text-[#B85D3B]' : ''}`}>{st.label}</strong>
                      <span className="text-[11px] text-[#78716C]">{st.desc}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Demonstration Results Output */}
          {demoResult && (
            <div className="bg-white border-2 border-emerald-500/40 p-6 rounded shadow-sm space-y-5">
              <div className="flex items-center justify-between pb-3 border-b border-[#E7E2DA]">
                <div className="flex items-center space-x-2 text-xs font-mono text-emerald-800">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Pipeline Completed Successfully</span>
                </div>
                <span className="text-xs font-mono text-[#78716C]">
                  Mode: {demoResult.mode}
                </span>
              </div>

              {/* Highlight Metrics Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                <div className="p-3 bg-[#FAF8F5] border border-[#E7E2DA] rounded">
                  <span className="text-[10px] font-mono uppercase text-[#78716C] block">Detected Regime</span>
                  <strong className="text-xs text-[#B85D3B] block mt-1">
                    {demoResult.regime_intelligence.title}
                  </strong>
                  <span className="text-[10px] text-[#78716C]">
                    {(demoResult.regime_intelligence.confidence * 100).toFixed(0)}% Conf
                  </span>
                </div>

                <div className="p-3 bg-[#FAF8F5] border border-[#E7E2DA] rounded">
                  <span className="text-[10px] font-mono uppercase text-[#78716C] block">Raw NWP Mean</span>
                  <strong className="text-base font-editorial text-[#1C1917] block mt-0.5">
                    {demoResult.correction_summary.mean_nwp_mm} mm
                  </strong>
                  <span className="text-[10px] text-[#78716C]">Baseline</span>
                </div>

                <div className="p-3 bg-[#FAF8F5] border border-[#E7E2DA] rounded">
                  <span className="text-[10px] font-mono uppercase text-[#78716C] block">VARSHA-Q Mean</span>
                  <strong className="text-base font-editorial text-[#B85D3B] block mt-0.5">
                    {demoResult.correction_summary.mean_corrected_mm} mm
                  </strong>
                  <span className="text-[10px] text-emerald-700">Bias Corrected</span>
                </div>

                <div className="p-3 bg-emerald-50 border border-emerald-200 rounded">
                  <span className="text-[10px] font-mono uppercase text-emerald-800 block">RMSE Reduction</span>
                  <strong className="text-base font-editorial text-emerald-900 block mt-0.5">
                    {demoResult.verification?.continuous?.rmse_reduction_pct}%
                  </strong>
                  <span className="text-[10px] text-emerald-700 font-mono">Real Metric</span>
                </div>
              </div>

              <div className="text-center pt-2">
                <button
                  onClick={onClose}
                  className="px-6 py-2.5 rounded bg-[#1C1917] hover:bg-[#292524] text-white text-xs font-medium tracking-wide shadow-sm"
                >
                  View Updated Dashboard &amp; Map
                </button>
              </div>
            </div>
          )}

        </div>

        {/* Modal Footer */}
        <div className="p-4 bg-[#F5F2EB] border-t border-[#E7E2DA] text-[11px] text-[#78716C] flex items-center justify-between">
          <span>VARSHA-Q SIH PS 26080 Prototype</span>
          <span className="font-mono">100% Deterministic &amp; Offline Defensible</span>
        </div>

      </div>
    </div>
  );
};
