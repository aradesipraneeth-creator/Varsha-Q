import React, { useEffect, useRef } from 'react';
import { ArrowDown, Compass, Play, Sparkles, Layers, Sliders } from 'lucide-react';

interface HeroSectionProps {
  onExploreForecast: () => void;
  onOpenJudgeDemo: () => void;
  onViewMethodology: () => void;
  activeScenario: string;
  onSelectScenario: (sc: string) => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({
  onExploreForecast,
  onOpenJudgeDemo,
  onViewMethodology,
  activeScenario,
  onSelectScenario,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // Atmospheric streamline animation
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let width = (canvas.width = canvas.offsetWidth);
    let height = (canvas.height = canvas.offsetHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = canvas.offsetWidth;
      height = canvas.height = canvas.offsetHeight;
    };
    window.addEventListener('resize', handleResize);

    // Precipitation & wind particle flow
    const particleCount = 55;
    const particles = Array.from({ length: particleCount }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      length: Math.random() * 20 + 10,
      speed: Math.random() * 2.5 + 1.2,
      opacity: Math.random() * 0.35 + 0.15,
      angle: 0.25 + Math.random() * 0.1, // Southwesterly monsoon tilt
    }));

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // Subtle atmospheric isobar contour lines
      ctx.strokeStyle = 'rgba(75, 123, 148, 0.08)';
      ctx.lineWidth = 1;
      for (let i = 0; i < 4; i++) {
        ctx.beginPath();
        const yOffset = height * (0.25 + i * 0.2);
        ctx.moveTo(0, yOffset);
        ctx.bezierCurveTo(
          width * 0.3, yOffset - 35,
          width * 0.7, yOffset + 35,
          width, yOffset - 10
        );
        ctx.stroke();
      }

      // Draw precipitation streamlines
      particles.forEach((p) => {
        ctx.strokeStyle = `rgba(184, 93, 59, ${p.opacity})`;
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.moveTo(p.x, p.y);
        ctx.lineTo(
          p.x + Math.sin(p.angle) * p.length,
          p.y + Math.cos(p.angle) * p.length
        );
        ctx.stroke();

        p.y += p.speed;
        p.x += Math.sin(p.angle) * p.speed;

        if (p.y > height) {
          p.y = -p.length;
          p.x = Math.random() * width;
        }
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  const scenarios = [
    { id: 'ACTIVE_MONSOON', label: 'Active Monsoon' },
    { id: 'BREAK_MONSOON', label: 'Break Monsoon' },
    { id: 'DEPRESSION_LOW', label: 'Depression / Low' },
    { id: 'COASTAL', label: 'Coastal Rainfall' },
    { id: 'OROGRAPHIC', label: 'Orographic Lifting' },
  ];

  return (
    <section className="relative overflow-hidden border-b border-[#E7E2DA] bg-[#FAF8F5] pt-12 pb-16 lg:pt-20 lg:pb-24">
      {/* Background canvas for atmospheric streamlines */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full pointer-events-none"
      />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Top Eyebrow Tag */}
        <div className="inline-flex items-center gap-2 px-3 py-1 mb-8 rounded-full border border-[#DCD6CC] bg-[#F5F2EB]/80 text-[11px] font-mono tracking-widest uppercase text-[#57534E]">
          <span className="w-1.5 h-1.5 rounded-full bg-[#B85D3B]" />
          <span>SIH 2026 PS 26080 &bull; TEAM QUANTUM LEAPERS</span>
        </div>

        {/* Editorial Headline */}
        <div className="max-w-4xl">
          <h1 className="font-editorial text-4xl sm:text-5xl lg:text-7xl font-normal leading-[1.08] text-[#1C1917] tracking-tight mb-6">
            Rainfall intelligence that <em className="italic font-serif font-normal text-[#B85D3B]">adapts</em> to the atmosphere.
          </h1>
          
          <p className="text-lg sm:text-xl text-[#57534E] leading-relaxed max-w-3xl mb-10 font-normal">
            Raw Numerical Weather Prediction (NWP) rainfall forecasts suffer from systematic errors that shift drastically across weather regimes. VARSHA-Q integrates <strong className="font-medium text-[#1C1917]">Continuous-Time Liquid Neural Networks (LNN)</strong>, <strong className="font-medium text-[#1C1917]">Spatial Graph Neural Networks (GNN)</strong>, and <strong className="font-medium text-[#1C1917]">Quantum-Inspired Optimization</strong> to deliver calibrated, regime-aware district intelligence.
          </p>
        </div>

        {/* Main CTA Actions */}
        <div className="flex flex-wrap items-center gap-4 mb-14">
          <button
            onClick={onExploreForecast}
            className="inline-flex items-center space-x-2 px-6 py-3 rounded bg-[#B85D3B] hover:bg-[#9C4729] text-white text-sm font-medium tracking-wide shadow-sm transition-all"
          >
            <span>Explore Forecast</span>
            <ArrowDown className="w-4 h-4" />
          </button>

          <button
            onClick={onOpenJudgeDemo}
            className="inline-flex items-center space-x-2 px-6 py-3 rounded bg-white hover:bg-[#F5F2EB] text-[#1C1917] border border-[#DCD6CC] text-sm font-medium tracking-wide shadow-sm transition-all"
          >
            <Play className="w-4 h-4 text-[#B85D3B] fill-current" />
            <span>Run Judge Demo</span>
          </button>

          <button
            onClick={onViewMethodology}
            className="inline-flex items-center space-x-1.5 px-4 py-3 text-sm text-[#57534E] hover:text-[#1C1917] transition-colors"
          >
            <span>View Methodology &rarr;</span>
          </button>
        </div>

        {/* Regime Scenario Switcher Bar */}
        <div className="pt-8 border-t border-[#E7E2DA]">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <span className="text-xs uppercase tracking-widest text-[#78716C] font-mono block">
                Simulate Weather Regime Scenario:
              </span>
              <span className="text-xs text-[#57534E]">
                See how VARSHA-Q reconfigures bias correction specifically for each atmospheric pattern.
              </span>
            </div>

            <div className="flex flex-wrap gap-2">
              {scenarios.map((sc) => {
                const isSelected = activeScenario === sc.id;
                return (
                  <button
                    key={sc.id}
                    onClick={() => onSelectScenario(sc.id)}
                    className={`px-3 py-1.5 rounded text-xs font-medium tracking-wide transition-all border ${
                      isSelected
                        ? 'bg-[#1C1917] text-white border-[#1C1917] shadow-sm'
                        : 'bg-white/80 text-[#57534E] border-[#E7E2DA] hover:border-[#B85D3B] hover:text-[#1C1917]'
                    }`}
                  >
                    {sc.label}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

      </div>
    </section>
  );
};
