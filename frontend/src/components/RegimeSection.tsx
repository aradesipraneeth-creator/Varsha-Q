import React from 'react';
import { RegimeIntelligence } from '../types';
import { Compass, Wind, Droplets, Gauge, AlertTriangle, ArrowRight, Check } from 'lucide-react';

interface RegimeSectionProps {
  regimeData: RegimeIntelligence | null;
  onScenarioChange: (scenario: string) => void;
}

export const RegimeSection: React.FC<RegimeSectionProps> = ({ regimeData, onScenarioChange }) => {
  if (!regimeData) return null;

  const regimeOrder = [
    'ACTIVE_MONSOON',
    'BREAK_MONSOON',
    'DEPRESSION_LOW',
    'COASTAL',
    'OROGRAPHIC',
  ];

  const regimeDisplayNames: Record<string, string> = {
    ACTIVE_MONSOON: 'Active Monsoon',
    BREAK_MONSOON: 'Break Monsoon',
    DEPRESSION_LOW: 'Depression / Low',
    COASTAL: 'Coastal Rainfall',
    OROGRAPHIC: 'Orographic Lifting',
    UNKNOWN_TRANSITION: 'Transition',
  };

  return (
    <section id="regimes" className="py-16 border-b border-[#E7E2DA] bg-[#F5F2EB]/40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="max-w-3xl mb-12">
          <span className="text-xs uppercase tracking-widest text-[#B85D3B] font-mono block mb-1">
            Synoptic Intelligence
          </span>
          <h2 className="font-editorial text-3xl sm:text-4xl text-[#1C1917] font-normal mb-3">
            Atmospheric Regime Classifier
          </h2>
          <p className="text-sm sm:text-base text-[#57534E] leading-relaxed">
            Different atmospheric regimes exhibit fundamentally distinct physical error mechanisms in NWP models. 
            VARSHA-Q classifies the prevailing synoptic regime <em>prior</em> to bias correction, ensuring the post-processing strategy aligns dynamically with large-scale atmospheric forcing.
          </p>
        </div>

        {/* Main Grid: Active Regime Card + Probability Distribution */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Active Classified Regime Card (5 cols) */}
          <div className="lg:col-span-5 bg-white border border-[#E7E2DA] p-6 sm:p-8 rounded shadow-sm relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-[#B85D3B]/5 rounded-bl-full pointer-events-none" />

            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono uppercase tracking-widest text-[#78716C]">
                Classified State
              </span>
              <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-200">
                Confidence: {(regimeData.confidence * 100).toFixed(1)}%
              </span>
            </div>

            <h3 className="font-editorial text-3xl text-[#1C1917] font-normal mb-3">
              {regimeData.title}
            </h3>

            <p className="text-xs sm:text-sm text-[#57534E] leading-relaxed mb-6">
              {regimeData.description}
            </p>

            {/* Key Atmospheric Indicators */}
            <div className="border-t border-[#E7E2DA] pt-4 mb-6">
              <span className="text-[11px] font-mono uppercase tracking-wider text-[#78716C] block mb-2.5">
                Key Observed Atmospheric Indicators:
              </span>
              <div className="space-y-1.5">
                {regimeData.key_indicators.map((indicator, idx) => (
                  <div key={idx} className="flex items-center space-x-2 text-xs text-[#1C1917]">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#B85D3B]" />
                    <span>{indicator}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Feature Contributions ("Why?") */}
            {regimeData.feature_contributions && regimeData.feature_contributions.length > 0 && (
              <div className="border-t border-[#E7E2DA] pt-4 text-xs">
                <span className="text-[11px] font-mono uppercase tracking-wider text-[#78716C] block mb-2">
                  Top Attributed Meteorological Features:
                </span>
                <div className="space-y-1">
                  {regimeData.feature_contributions.slice(0, 3).map((f, i) => (
                    <div key={i} className="flex items-center justify-between text-[#57534E] text-[11px]">
                      <span className="font-mono text-[#44403C]">{f.feature.replace(/_/g, ' ')}</span>
                      <span className="font-mono text-[#78716C]">{(f.importance * 100).toFixed(1)}% weight</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Regime Probabilities Breakdown & Switcher (7 cols) */}
          <div className="lg:col-span-7 bg-white border border-[#E7E2DA] p-6 sm:p-8 rounded shadow-sm">
            <h4 className="font-editorial text-xl text-[#1C1917] mb-2 font-normal">
              Regime Probability Distribution
            </h4>
            <p className="text-xs text-[#78716C] mb-6">
              Full calibrated probability distribution produced by the Random Forest classifier. Select any regime to inspect its specialized bias correction behavior.
            </p>

            <div className="space-y-4">
              {regimeOrder.map((regKey) => {
                const prob = regimeData.probabilities[regKey] || 0;
                const isCurrent = regimeData.regime === regKey;
                const displayName = regimeDisplayNames[regKey] || regKey;

                return (
                  <div
                    key={regKey}
                    onClick={() => onScenarioChange(regKey)}
                    className={`p-3.5 rounded border transition-all cursor-pointer ${
                      isCurrent
                        ? 'border-[#B85D3B] bg-[#FAF8F5]'
                        : 'border-[#E7E2DA] hover:border-[#DCD6CC] hover:bg-[#FAF8F5]/50'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="flex items-center space-x-2">
                        <span className={`text-xs font-medium ${isCurrent ? 'text-[#B85D3B] font-bold' : 'text-[#1C1917]'}`}>
                          {displayName}
                        </span>
                        {isCurrent && (
                          <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-[#B85D3B] text-white">
                            ACTIVE
                          </span>
                        )}
                      </div>
                      <span className="font-mono text-xs font-semibold text-[#1C1917]">
                        {(prob * 100).toFixed(1)}%
                      </span>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-[#E7E2DA] h-1.5 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all duration-500 rounded-full ${
                          isCurrent ? 'bg-[#B85D3B]' : 'bg-[#78716C]'
                        }`}
                        style={{ width: `${Math.max(2, prob * 100)}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Scientific Architectural Decision Note */}
            <div className="mt-6 p-3.5 bg-[#F5F2EB]/60 border border-[#E7E2DA] rounded text-xs text-[#57534E] flex items-start gap-2.5">
              <Compass className="w-4 h-4 text-[#B85D3B] shrink-0 mt-0.5" />
              <div>
                <strong className="text-[#1C1917]">Architectural Principle:</strong> Classification happens <em>strictly before</em> bias correction. This breaks the single-model assumption that often causes over-correction in dry break spells or severe under-correction in orographic barriers.
              </div>
            </div>

          </div>

        </div>

      </div>
    </section>
  );
};
