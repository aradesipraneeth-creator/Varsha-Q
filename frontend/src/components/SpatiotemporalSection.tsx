import React from 'react';
import { Clock, Network, Cpu, GitMerge, ArrowRight, Waves } from 'lucide-react';

export const SpatiotemporalSection: React.FC = () => {
  return (
    <section className="py-16 border-b border-[#E7E2DA] bg-[#FAF8F5]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="max-w-3xl mb-12">
          <span className="text-xs uppercase tracking-widest text-[#B85D3B] font-mono block mb-1">
            Deep Architecture
          </span>
          <h2 className="font-editorial text-3xl sm:text-4xl text-[#1C1917] font-normal mb-3">
            Spatiotemporal Representation Learning
          </h2>
          <p className="text-sm sm:text-base text-[#57534E] leading-relaxed">
            Atmospheric processes evolve continuously in time while propagating across complex spatial terrain. 
            VARSHA-Q couples continuous-time Liquid Neural Networks with Spatial Graph Neural Networks via an adaptive gated fusion layer.
          </p>
        </div>

        {/* 3 Pillars Grid: LNN + GNN + Fusion */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          
          {/* Pillar 1: LNN */}
          <div className="bg-white border border-[#E7E2DA] p-6 rounded relative overflow-hidden flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded bg-[#FAF8F5] border border-[#E7E2DA] flex items-center justify-center text-[#B85D3B] mb-4">
                <Clock className="w-5 h-5" />
              </div>
              <span className="text-[11px] font-mono uppercase tracking-wider text-[#78716C] block mb-1">
                Temporal Component
              </span>
              <h3 className="font-editorial text-2xl text-[#1C1917] font-normal mb-2">
                Liquid Neural Network
              </h3>
              <p className="text-xs text-[#57534E] leading-relaxed mb-4">
                Models non-linear continuous-time rainfall sequence dynamics using Liquid Time-Constant (LTC) differential equations. 
                Adapts its internal time-constants dynamically to input flux.
              </p>

              <div className="bg-[#FAF8F5] border border-[#E7E2DA] p-3 rounded font-mono text-[11px] text-[#44403C] space-y-1">
                <div className="text-[#B85D3B] font-semibold">Continuous-Time ODE:</div>
                <div className="italic text-[10px] leading-tight">
                  dx/dt = - [1/&tau; + f(x,u)] &middot; x + A &middot; f(x,u)
                </div>
                <div className="text-[10px] text-[#78716C] pt-1">
                  Semi-implicit Euler integration &bull; 32D Latent Trajectory
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-[#E7E2DA] text-[11px] text-[#78716C] flex items-center justify-between">
              <span>Input: Historical Sequence (T=6)</span>
              <span className="font-mono text-[#1C1917]">H_temp &isin; &Ropf;<sup>32</sup></span>
            </div>
          </div>

          {/* Pillar 2: GNN */}
          <div className="bg-white border border-[#E7E2DA] p-6 rounded relative overflow-hidden flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded bg-[#FAF8F5] border border-[#E7E2DA] flex items-center justify-center text-[#2C5282] mb-4">
                <Network className="w-5 h-5" />
              </div>
              <span className="text-[11px] font-mono uppercase tracking-wider text-[#78716C] block mb-1">
                Spatial Component
              </span>
              <h3 className="font-editorial text-2xl text-[#1C1917] font-normal mb-2">
                Graph Neural Network
              </h3>
              <p className="text-xs text-[#57534E] leading-relaxed mb-4">
                District vertices connected by spatial adjacency edges. Propagates elevation gradients, terrain roughness, and marine-coastal boundaries across topological neighbors.
              </p>

              <div className="bg-[#FAF8F5] border border-[#E7E2DA] p-3 rounded font-mono text-[11px] text-[#44403C] space-y-1">
                <div className="text-[#2C5282] font-semibold">Graph Convolution:</div>
                <div className="italic text-[10px] leading-tight">
                  H<sup>(l+1)</sup> = &sigma;( D&#770;<sup>-1/2</sup> A&#770; D&#770;<sup>-1/2</sup> H<sup>(l)</sup> W + W<sub>res</sub> )
                </div>
                <div className="text-[10px] text-[#78716C] pt-1">
                  Topological Adjacency &bull; Terrain &amp; Coastal Priors
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-[#E7E2DA] text-[11px] text-[#78716C] flex items-center justify-between">
              <span>Input: District Adjacency</span>
              <span className="font-mono text-[#1C1917]">H_spat &isin; &Ropf;<sup>32</sup></span>
            </div>
          </div>

          {/* Pillar 3: Gated Fusion */}
          <div className="bg-white border border-[#E7E2DA] p-6 rounded relative overflow-hidden flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded bg-[#FAF8F5] border border-[#E7E2DA] flex items-center justify-center text-[#4D7C5F] mb-4">
                <GitMerge className="w-5 h-5" />
              </div>
              <span className="text-[11px] font-mono uppercase tracking-wider text-[#78716C] block mb-1">
                Joint Representation
              </span>
              <h3 className="font-editorial text-2xl text-[#1C1917] font-normal mb-2">
                Gated Fusion Layer
              </h3>
              <p className="text-xs text-[#57534E] leading-relaxed mb-4">
                Adaptively weights temporal persistence against spatial neighborhood influence using a learnable non-linear gating mechanism before passing to regime-specific bias estimators.
              </p>

              <div className="bg-[#FAF8F5] border border-[#E7E2DA] p-3 rounded font-mono text-[11px] text-[#44403C] space-y-1">
                <div className="text-[#4D7C5F] font-semibold">Gated Projection:</div>
                <div className="italic text-[10px] leading-tight">
                  Z<sub>ST</sub> = LN( G &odot; W<sub>t</sub>H<sub>t</sub> + (1 - G) &odot; W<sub>s</sub>H<sub>s</sub> )
                </div>
                <div className="text-[10px] text-[#78716C] pt-1">
                  Cross-attention gating &bull; LayerNorm stabilized
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-[#E7E2DA] text-[11px] text-[#78716C] flex items-center justify-between">
              <span>Output: Joint Embedding</span>
              <span className="font-mono text-[#1C1917]">Z_ST &isin; &Ropf;<sup>32</sup></span>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
};
