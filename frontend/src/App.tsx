import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { StatusBanner } from './components/StatusBanner';
import { HeroSection } from './components/HeroSection';
import { ForecastView } from './components/ForecastView';
import { RegimeSection } from './components/RegimeSection';
import { SpatiotemporalSection } from './components/SpatiotemporalSection';
import { QuantumOptimizationSection } from './components/QuantumOptimizationSection';
import { HeavyRainProbabilitySection } from './components/HeavyRainProbabilitySection';
import { DistrictMapSection } from './components/DistrictMapSection';
import { VerificationDashboard } from './components/VerificationDashboard';
import { MethodologySection } from './components/MethodologySection';
import { JudgeDemoModal } from './components/JudgeDemoModal';

import { api } from './services/api';
import { SystemStatus, ForecastResponse, FullVerification, OptimizationBenchmark, DistrictForecast } from './types';

export const App: React.FC = () => {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [geoJsonData, setGeoJsonData] = useState<any>(null);
  const [verification, setVerification] = useState<FullVerification | null>(null);
  const [optimization, setOptimization] = useState<OptimizationBenchmark | null>(null);

  const [activeScenario, setActiveScenario] = useState<string>('OROGRAPHIC');
  const [selectedState, setSelectedState] = useState<string>('All India');
  const [selectedDistrict, setSelectedDistrict] = useState<DistrictForecast | null>(null);
  const [isJudgeDemoOpen, setIsJudgeDemoOpen] = useState<boolean>(false);
  const [activeSection, setActiveSection] = useState<string>('overview');
  const [isOptLoading, setIsOptLoading] = useState<boolean>(false);

  // Initial load
  useEffect(() => {
    const initData = async () => {
      try {
        const [sysStatus, fcast, geo, ver, opt] = await Promise.all([
          api.getSystemStatus().catch(() => null),
          api.getLatestForecast().catch(() => null),
          api.getDistrictsGeoJson().catch(() => null),
          api.getVerification().catch(() => null),
          api.getOptimizationLatest().catch(() => null),
        ]);

        if (sysStatus) setStatus(sysStatus);
        if (fcast) {
          setForecast(fcast);
          setActiveScenario(fcast.regime_intelligence?.regime || 'ACTIVE_MONSOON');
        }
        if (geo) setGeoJsonData(geo);
        if (ver) setVerification(ver);
        if (opt) setOptimization(opt);
      } catch (err) {
        console.error('Initialization error:', err);
      }
    };

    initData();
  }, []);

  const handleScenarioChange = async (scenario: string) => {
    setActiveScenario(scenario);
    try {
      const updated = await api.runInference(scenario);
      setForecast(updated);
      setSelectedDistrict(null);
    } catch (err) {
      console.error(`Failed to change scenario to ${scenario}:`, err);
    }
  };

  const handleRunJudgeDemo = async (scenario: string): Promise<ForecastResponse> => {
    const updated = await api.runInference(scenario);
    setForecast(updated);
    setActiveScenario(scenario);
    return updated;
  };

  const handleRunOptimizationBenchmark = async () => {
    setIsOptLoading(true);
    try {
      const res = await api.runOptimization();
      setOptimization(res);
    } catch (err) {
      console.error('Optimization run failed:', err);
    } finally {
      setIsOptLoading(false);
    }
  };

  const scrollToSection = (sectionId: string) => {
    setActiveSection(sectionId);
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#FAF8F5] text-[#1C1917]">
      
      {/* 1. Header Navigation */}
      <Navbar
        status={status}
        onOpenJudgeDemo={() => setIsJudgeDemoOpen(true)}
        activeSection={activeSection}
        onNavigate={scrollToSection}
      />

      {/* 2. Real-Time Operational Status Banner */}
      <StatusBanner
        status={status}
        mode={forecast?.mode || status?.mode || 'DEMO'}
      />

      <main className="flex-1">
        
        {/* 3. Hero Section */}
        <div id="overview">
          <HeroSection
            onExploreForecast={() => scrollToSection('forecast')}
            onOpenJudgeDemo={() => setIsJudgeDemoOpen(true)}
            onViewMethodology={() => scrollToSection('methodology')}
            activeScenario={activeScenario}
            onSelectScenario={handleScenarioChange}
          />
        </div>

        {/* 4. Live / Replay Forecast View */}
        <ForecastView
          forecast={forecast}
          selectedState={selectedState}
          onSelectState={setSelectedState}
          onSelectDistrict={(d) => {
            setSelectedDistrict(d);
            scrollToSection('districts');
          }}
        />

        {/* 5. Weather Regime Classifier */}
        <RegimeSection
          regimeData={forecast?.regime_intelligence || null}
          onScenarioChange={handleScenarioChange}
        />

        {/* 6. Spatiotemporal AI (LNN + GNN + Fusion) */}
        <SpatiotemporalSection />

        {/* 7. Quantum-Inspired Optimization Engine */}
        <QuantumOptimizationSection
          benchmarkData={optimization}
          onRunBenchmark={handleRunOptimizationBenchmark}
          isLoading={isOptLoading}
        />

        {/* 8. Heavy Rain Probability & Quantile Uncertainty */}
        <HeavyRainProbabilitySection
          forecast={forecast}
          onSelectDistrict={(d) => {
            setSelectedDistrict(d);
            scrollToSection('districts');
          }}
        />

        {/* 9. District Intelligence Map & Inspector */}
        <DistrictMapSection
          forecast={forecast}
          geoJsonData={geoJsonData}
          selectedDistrict={selectedDistrict}
          onSelectDistrict={setSelectedDistrict}
        />

        {/* 10. Scientific Verification Dashboard */}
        <VerificationDashboard
          verificationData={verification}
        />

        {/* 11. Methodology & Reference Documentation */}
        <MethodologySection />

      </main>

      {/* Judge Demo Interactive Modal */}
      <JudgeDemoModal
        isOpen={isJudgeDemoOpen}
        onClose={() => setIsJudgeDemoOpen(false)}
        onRunDemo={handleRunJudgeDemo}
        currentScenario={activeScenario}
      />

      {/* Editorial Footer */}
      <footer className="border-t border-[#E7E2DA] bg-[#FAF8F5] py-12 text-xs text-[#78716C]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center space-x-3">
            <span className="font-editorial text-xl font-bold tracking-tight text-[#1C1917]">
              VARSHA-Q
            </span>
            <span className="text-[#DCD6CC]">|</span>
            <span>Quantum-Inspired Spatiotemporal AI for Regime-Aware Rainfall</span>
          </div>

          <div className="text-center md:text-right font-mono text-[11px]">
            <div>Smart India Hackathon 2026 &bull; Problem Statement ID: 26080</div>
            <div className="text-[#B85D3B] font-semibold mt-0.5">TEAM: QUANTUM LEAPERS</div>
          </div>
        </div>
      </footer>

    </div>
  );
};

export default App;
