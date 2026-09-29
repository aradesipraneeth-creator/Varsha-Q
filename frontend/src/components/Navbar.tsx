import React from 'react';
import { CloudRain, Play, ShieldAlert, Cpu, Activity } from 'lucide-react';
import { SystemStatus } from '../types';

interface NavbarProps {
  status: SystemStatus | null;
  onOpenJudgeDemo: () => void;
  activeSection: string;
  onNavigate: (sectionId: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ status, onOpenJudgeDemo, activeSection, onNavigate }) => {
  const navItems = [
    { id: 'overview', label: 'Overview' },
    { id: 'forecast', label: 'Forecast' },
    { id: 'regimes', label: 'Regimes' },
    { id: 'districts', label: 'Districts' },
    { id: 'optimization', label: 'Optimization' },
    { id: 'verification', label: 'Verification' },
    { id: 'methodology', label: 'Methodology' },
  ];

  return (
    <header className="sticky top-0 z-40 bg-[#FAF8F5]/90 backdrop-blur-md border-b border-[#E7E2DA] transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Brand Logo & Editorial Title */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => onNavigate('overview')}>
            <div className="w-9 h-9 rounded bg-[#B85D3B] flex items-center justify-center text-white shadow-sm">
              <CloudRain className="w-5 h-5 stroke-[2]" />
            </div>
            <div>
              <span className="font-editorial text-2xl font-bold tracking-tight text-[#1C1917]">
                VARSHA-Q
              </span>
              <span className="hidden sm:inline-block ml-2 text-[11px] font-sans tracking-widest uppercase text-[#78716C] border-l border-[#DCD6CC] pl-2">
                PS 26080
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1 lg:space-x-2">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`px-3 py-1.5 text-xs font-medium tracking-wide uppercase transition-colors rounded-sm ${
                  activeSection === item.id
                    ? 'text-[#B85D3B] font-semibold bg-[#F5F2EB]'
                    : 'text-[#57534E] hover:text-[#1C1917] hover:bg-[#F5F2EB]/60'
                }`}
              >
                {item.label}
              </button>
            ))}
          </nav>

          {/* System Status Indicators & CTA */}
          <div className="flex items-center space-x-3">
            {/* Mode Indicator */}
            <div className="hidden lg:flex items-center space-x-2 px-2.5 py-1 bg-[#F5F2EB] border border-[#E7E2DA] rounded text-[11px]">
              <span className="flex h-2 w-2 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-600"></span>
              </span>
              <span className="font-mono text-[#44403C] uppercase tracking-wider font-medium">
                {status?.mode || 'DEMO'}
              </span>
              <span className="text-[#A8A29E]">|</span>
              <span className="font-mono text-[#57534E] text-[10px]">
                {status?.device?.toUpperCase() || 'CPU'}
              </span>
            </div>

            {/* Run Judge Demo Action */}
            <button
              onClick={onOpenJudgeDemo}
              className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded bg-[#B85D3B] hover:bg-[#9C4729] text-white text-xs font-medium tracking-wider uppercase shadow-sm transition-all transform active:scale-95"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Judge Demo</span>
            </button>
          </div>

        </div>
      </div>
    </header>
  );
};
