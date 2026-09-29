import React from 'react';
import { BookOpen, Code2, Users, Database, Sparkles, CheckCircle2 } from 'lucide-react';

export const MethodologySection: React.FC = () => {
  return (
    <section id="methodology" className="py-16 bg-[#FAF8F5]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="max-w-3xl mb-12">
          <span className="text-xs uppercase tracking-widest text-[#B85D3B] font-mono block mb-1">
            System Design &amp; References
          </span>
          <h2 className="font-editorial text-3xl sm:text-4xl text-[#1C1917] font-normal mb-2">
            Scientific Methodology &amp; Architecture
          </h2>
          <p className="text-sm text-[#57534E] leading-relaxed">
            VARSHA-Q is grounded in rigorous meteorological post-processing and modern spatiotemporal deep learning. Below is the full end-to-end dataflow pipeline and scientific citations.
          </p>
        </div>

        {/* Pipeline Architecture Diagram Card */}
        <div className="bg-white border border-[#E7E2DA] p-6 sm:p-8 rounded shadow-sm mb-12">
          <h3 className="font-editorial text-xl text-[#1C1917] mb-6 font-normal">
            End-to-End Pipeline Dataflow
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-7 gap-3 text-center text-xs font-mono">
            
            <div className="p-3 bg-[#FAF8F5] border border-[#E7E2DA] rounded">
              <span className="text-[#B85D3B] font-bold block mb-1">Stage 1</span>
              <strong className="text-[#1C1917] block">Data Ingest</strong>
              <span className="text-[10px] text-[#78716C]">NWP + Obs + Terrain</span>
            </div>

            <div className="p-3 bg-[#FAF8F5] border border-[#E7E2DA] rounded">
              <span className="text-[#B85D3B] font-bold block mb-1">Stage 2</span>
              <strong className="text-[#1C1917] block">Spatiotemporal</strong>
              <span className="text-[10px] text-[#78716C]">LNN (Time) + GNN (Space)</span>
            </div>

            <div className="p-3 bg-[#FBF2EE] border-2 border-[#B85D3B]/40 rounded shadow-sm">
              <span className="text-[#B85D3B] font-bold block mb-1">Stage 3</span>
              <strong className="text-[#B85D3B] block">Regime Classifier</strong>
              <span className="text-[10px] text-[#9C4729]">Pre-Correction Labeling</span>
            </div>

            <div className="p-3 bg-[#FAF8F5] border border-[#E7E2DA] rounded">
              <span className="text-[#B85D3B] font-bold block mb-1">Stage 4</span>
              <strong className="text-[#1C1917] block">Bias Correction</strong>
              <span className="text-[10px] text-[#78716C]">Regime-Specific Models</span>
            </div>

            <div className="p-3 bg-[#FAF8F5] border border-[#E7E2DA] rounded">
              <span className="text-[#B85D3B] font-bold block mb-1">Stage 5</span>
              <strong className="text-[#1C1917] block">Quantum-Inspired</strong>
              <span className="text-[10px] text-[#78716C]">QUBO Feature Search</span>
            </div>

            <div className="p-3 bg-[#FAF8F5] border border-[#E7E2DA] rounded">
              <span className="text-[#B85D3B] font-bold block mb-1">Stage 6</span>
              <strong className="text-[#1C1917] block">Probability</strong>
              <span className="text-[10px] text-[#78716C]">P10/P50/P90 Bounds</span>
            </div>

            <div className="p-3 bg-[#FAF8F5] border border-[#E7E2DA] rounded">
              <span className="text-[#B85D3B] font-bold block mb-1">Stage 7</span>
              <strong className="text-[#1C1917] block">Verification</strong>
              <span className="text-[10px] text-[#78716C]">RMSE, CSI, ETS, FSS</span>
            </div>

          </div>
        </div>

        {/* Mathematical Formulations Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
          
          <div className="bg-white border border-[#E7E2DA] p-6 rounded text-xs space-y-4">
            <h4 className="font-editorial text-lg text-[#1C1917] font-normal">
              1. Continuous-Time Liquid Neural Dynamics
            </h4>
            <p className="text-[#57534E] leading-relaxed">
              Unlike classical RNNs with static discrete clocking, Liquid Neural Networks represent state trajectories through non-linear differential equations where internal decay rates vary with inputs:
            </p>
            <div className="p-3 bg-[#FAF8F5] border border-[#E7E2DA] rounded font-mono text-[11px] text-[#1C1917]">
              dx(t)/dt = - [ 1/&tau; + f(x(t), u(t)) ] &middot; x(t) + A &middot; f(x(t), u(t))
            </div>
            <p className="text-[#78716C] text-[11px]">
              Solved using semi-implicit Euler stepping for numerical stability across rapid monsoon convective transitions.
            </p>
          </div>

          <div className="bg-white border border-[#E7E2DA] p-6 rounded text-xs space-y-4">
            <h4 className="font-editorial text-lg text-[#1C1917] font-normal">
              2. QUBO Combinatorial Feature Optimization
            </h4>
            <p className="text-[#57534E] leading-relaxed">
              Binary feature selection mapped onto an effective Ising Hamiltonian:
            </p>
            <div className="p-3 bg-[#FAF8F5] border border-[#E7E2DA] rounded font-mono text-[11px] text-[#1C1917]">
              min E(x) = x<sup>T</sup> Q x + &lambda; &sum; x<sub>i</sub>, &nbsp; x &isin; &#123;0, 1&#125;<sup>N</sup>
            </div>
            <p className="text-[#78716C] text-[11px]">
              Solved via Path-Integral Monte Carlo with P Trotter replicas. Transverse field &Gamma;(t) allows quantum tunneling through narrow barriers that trap classical thermal annealing.
            </p>
          </div>

        </div>

        {/* References & Team Footer */}
        <div className="border-t border-[#E7E2DA] pt-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-xs text-[#78716C]">
          <div>
            <strong className="text-[#1C1917] block">VARSHA-Q &bull; Team QUANTUM LEAPERS</strong>
            <span>Smart India Hackathon 2026 &bull; Problem Statement: SIH PS 26080</span>
          </div>

          <div className="flex flex-wrap gap-4 text-[11px]">
            <span>IMD MoES Meteorological Standards</span>
            <span>Roberts &amp; Lean (2008) FSS</span>
            <span>Hasani et al. (2021) Liquid Nets</span>
          </div>
        </div>

      </div>
    </section>
  );
};
