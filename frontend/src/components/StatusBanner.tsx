import React from 'react';
import { AlertCircle, CheckCircle2, Clock, Database, Server } from 'lucide-react';
import { SystemStatus } from '../types';

interface StatusBannerProps {
  status: SystemStatus | null;
  mode: string;
}

export const StatusBanner: React.FC<StatusBannerProps> = ({ status, mode }) => {
  const isDemo = mode === 'DEMO' || mode.includes('FALLBACK');

  return (
    <div className="border-b border-[#E7E2DA] bg-[#F5F2EB]/50 text-xs text-[#57534E]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2.5">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2">
          
          {/* Data Class Health Badges */}
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5">
            <span className="font-semibold tracking-wider text-[11px] uppercase text-[#44403C] flex items-center gap-1.5">
              <Database className="w-3.5 h-3.5 text-[#B85D3B]" /> Data Pipeline:
            </span>
            
            <div className="flex items-center space-x-1.5">
              <span className={`w-1.5 h-1.5 rounded-full ${isDemo ? 'bg-amber-500' : 'bg-emerald-500'}`} />
              <span className="text-[#44403C]">NWP (GFS/ECMWF):</span>
              <span className="font-mono text-[11px] text-[#78716C]">{isDemo ? 'Replay Baseline' : 'Live Stream'}</span>
            </div>

            <div className="flex items-center space-x-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              <span className="text-[#44403C]">Terrain (SRTM):</span>
              <span className="font-mono text-[11px] text-[#78716C]">Loaded (30m)</span>
            </div>

            <div className="flex items-center space-x-1.5">
              <span className={`w-1.5 h-1.5 rounded-full ${isDemo ? 'bg-amber-500' : 'bg-emerald-500'}`} />
              <span className="text-[#44403C]">AWS / Rain Gauge:</span>
              <span className="font-mono text-[11px] text-[#78716C]">{isDemo ? 'Synchronized Replay' : 'IMD Ingest'}</span>
            </div>

            <div className="hidden sm:flex items-center space-x-1.5 text-[#78716C]">
              <Clock className="w-3 h-3 text-[#A8A29E]" />
              <span className="font-mono text-[10px]">
                Cycle: 00Z Synoptic Run | Mode: <strong className="text-[#B85D3B]">{mode}</strong>
              </span>
            </div>
          </div>

          {/* Mandatory Disclaimer */}
          <div className="flex items-center gap-1.5 text-[11px] text-[#78716C] bg-white/70 px-2 py-0.5 rounded border border-[#E7E2DA]">
            <AlertCircle className="w-3.5 h-3.5 text-[#B85D3B] shrink-0" />
            <span className="truncate">
              Research Prototype. Not an official IMD meteorological warning.
            </span>
          </div>

        </div>
      </div>
    </div>
  );
};
