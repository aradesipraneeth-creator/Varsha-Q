import React, { useEffect, useRef, useState } from 'react';
import { ForecastResponse, DistrictForecast } from '../types';
import L from 'leaflet';
import { Layers, MapPin, X, ArrowRight, ShieldAlert, CloudRain, Mountain, Compass } from 'lucide-react';

interface DistrictMapSectionProps {
  forecast: ForecastResponse | null;
  geoJsonData: any;
  selectedDistrict: DistrictForecast | null;
  onSelectDistrict: (district: DistrictForecast | null) => void;
}

export const DistrictMapSection: React.FC<DistrictMapSectionProps> = ({
  forecast,
  geoJsonData,
  selectedDistrict,
  onSelectDistrict,
}) => {
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const geoJsonLayerRef = useRef<L.GeoJSON | null>(null);

  const [activeLayer, setActiveLayer] = useState<'corrected' | 'raw' | 'delta' | 'prob' | 'risk'>('corrected');

  // Color functions for each layer
  const getColor = (dForecast?: DistrictForecast): string => {
    if (!dForecast) return '#E7E2DA';

    if (activeLayer === 'corrected') {
      const val = dForecast.corrected_rainfall_mm;
      if (val >= 100) return '#7E361E';
      if (val >= 60) return '#B85D3B';
      if (val >= 35) return '#CE7856';
      if (val >= 15) return '#4B7B94';
      if (val >= 5) return '#82A7BA';
      return '#DFD7C5';
    }

    if (activeLayer === 'raw') {
      const val = dForecast.raw_nwp_rainfall_mm;
      if (val >= 100) return '#7E361E';
      if (val >= 60) return '#B85D3B';
      if (val >= 35) return '#CE7856';
      if (val >= 15) return '#4B7B94';
      return '#DFD7C5';
    }

    if (activeLayer === 'delta') {
      const delta = dForecast.delta_mm;
      if (delta >= 25) return '#10B981'; // Large positive correction
      if (delta >= 10) return '#34D399';
      if (delta <= -20) return '#F59E0B'; // Large negative correction
      if (delta <= -5) return '#FCD34D';
      return '#E5E7EB';
    }

    if (activeLayer === 'prob') {
      const p = dForecast.heavy_rain_probabilities.p_gt_50mm || 0;
      if (p >= 0.7) return '#B85D3B';
      if (p >= 0.4) return '#CE7856';
      if (p >= 0.2) return '#4B7B94';
      return '#E7E2DA';
    }

    if (activeLayer === 'risk') {
      if (dForecast.risk_category === 'VERY HIGH') return '#E11D48';
      if (dForecast.risk_category === 'HIGH') return '#EA580C';
      if (dForecast.risk_category === 'MODERATE') return '#D97706';
      return '#10B981';
    }

    return '#DFD7C5';
  };

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    // Centered on Central / Southern India
    const map = L.map(mapContainerRef.current, {
      center: [20.5937, 79.9629],
      zoom: 5,
      zoomControl: false,
      attributionControl: false,
    });

    // Add minimal, warm ivory CartoDB Positron tiles
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 10,
      subdomains: 'abcd',
    }).addTo(map);

    L.control.zoom({ position: 'bottomright' }).addTo(map);

    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update GeoJSON layer when data or activeLayer changes
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !geoJsonData || !forecast) return;

    if (geoJsonLayerRef.current) {
      map.removeLayer(geoJsonLayerRef.current);
    }

    const forecastMap = new Map<string, DistrictForecast>();
    forecast.district_forecasts.forEach((d) => forecastMap.set(d.district_id, d));

    const geoLayer = L.geoJSON(geoJsonData, {
      style: (feature) => {
        const dId = feature?.properties?.id;
        const dForecast = forecastMap.get(dId);
        const isSelected = selectedDistrict?.district_id === dId;

        return {
          fillColor: getColor(dForecast),
          weight: isSelected ? 2.5 : 1,
          opacity: 1,
          color: isSelected ? '#1C1917' : '#FFFFFF',
          fillOpacity: 0.85,
        };
      },
      onEachFeature: (feature, layer) => {
        const dId = feature?.properties?.id;
        const dForecast = forecastMap.get(dId);
        const name = feature?.properties?.name || 'District';

        layer.on({
          click: () => {
            if (dForecast) onSelectDistrict(dForecast);
          },
          mouseover: (e) => {
            const l = e.target;
            l.setStyle({ weight: 2, color: '#1C1917', fillOpacity: 0.95 });
          },
          mouseout: (e) => {
            const isSelected = selectedDistrict?.district_id === dId;
            geoLayer.resetStyle(e.target);
            if (isSelected) {
              e.target.setStyle({ weight: 2.5, color: '#1C1917' });
            }
          },
        });

        // Hover tooltip
        if (dForecast) {
          layer.bindTooltip(
            `<strong>${name}</strong><br/>` +
            `Raw NWP: ${dForecast.raw_nwp_rainfall_mm} mm<br/>` +
            `VARSHA-Q: <strong>${dForecast.corrected_rainfall_mm} mm</strong>`,
            { direction: 'top', sticky: true }
          );
        }
      },
    }).addTo(map);

    geoJsonLayerRef.current = geoLayer;
  }, [geoJsonData, forecast, activeLayer, selectedDistrict]);

  return (
    <section id="districts" className="py-16 border-b border-[#E7E2DA] bg-[#FAF8F5]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 pb-4 border-b border-[#E7E2DA]">
          <div>
            <span className="text-xs uppercase tracking-widest text-[#B85D3B] font-mono block mb-1">
              Geospatial Visualizer
            </span>
            <h2 className="font-editorial text-3xl sm:text-4xl text-[#1C1917] font-normal">
              District Meteorological Intelligence Map
            </h2>
          </div>

          {/* Layer Switcher Controls */}
          <div className="mt-4 md:mt-0 flex flex-wrap items-center gap-2">
            <span className="text-xs font-mono uppercase text-[#78716C] mr-1 hidden sm:inline">
              Layer:
            </span>
            {[
              { id: 'corrected', label: 'VARSHA-Q Rainfall' },
              { id: 'raw', label: 'Raw NWP Rainfall' },
              { id: 'delta', label: 'Correction Offset' },
              { id: 'prob', label: 'Heavy Rain Prob' },
              { id: 'risk', label: 'Model Risk' },
            ].map((layer) => (
              <button
                key={layer.id}
                onClick={() => setActiveLayer(layer.id as any)}
                className={`px-3 py-1 text-xs font-medium tracking-wide rounded border transition-all ${
                  activeLayer === layer.id
                    ? 'bg-[#1C1917] text-white border-[#1C1917]'
                    : 'bg-white text-[#57534E] border-[#E7E2DA] hover:border-[#B85D3B]'
                }`}
              >
                {layer.label}
              </button>
            ))}
          </div>
        </div>

        {/* Map Container + District Drilldown Inspector */}
        <div className="relative grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          {/* Leaflet Map Frame (8 cols or 12 cols if no inspector) */}
          <div className={`border border-[#E7E2DA] rounded overflow-hidden shadow-sm h-[560px] bg-[#FAF8F5] relative ${selectedDistrict ? 'lg:col-span-8' : 'lg:col-span-12'}`}>
            <div ref={mapContainerRef} className="w-full h-full" />

            {/* Map Legend Floating Tag */}
            <div className="absolute bottom-4 left-4 z-[500] bg-white/90 backdrop-blur-sm border border-[#E7E2DA] p-3 rounded text-[11px] shadow-sm">
              <span className="font-mono uppercase font-semibold text-[#1C1917] block mb-1.5">
                {activeLayer === 'corrected' && 'Rainfall Scale (mm)'}
                {activeLayer === 'raw' && 'Raw NWP Scale (mm)'}
                {activeLayer === 'delta' && 'Bias Offset (Observed - NWP)'}
                {activeLayer === 'prob' && 'P(Rain > 50mm)'}
                {activeLayer === 'risk' && 'Model Risk Level'}
              </span>
              {activeLayer === 'corrected' || activeLayer === 'raw' ? (
                <div className="flex items-center space-x-1 font-mono text-[10px] text-[#57534E]">
                  <span className="w-3.5 h-3.5 rounded bg-[#DFD7C5]" /> <span>&lt;15</span>
                  <span className="w-3.5 h-3.5 rounded bg-[#4B7B94]" /> <span>15-35</span>
                  <span className="w-3.5 h-3.5 rounded bg-[#CE7856]" /> <span>35-60</span>
                  <span className="w-3.5 h-3.5 rounded bg-[#B85D3B]" /> <span>60-100</span>
                  <span className="w-3.5 h-3.5 rounded bg-[#7E361E]" /> <span>&gt;100</span>
                </div>
              ) : activeLayer === 'delta' ? (
                <div className="flex items-center space-x-1 font-mono text-[10px] text-[#57534E]">
                  <span className="w-3.5 h-3.5 rounded bg-[#F59E0B]" /> <span>-20 (Overpred)</span>
                  <span className="w-3.5 h-3.5 rounded bg-[#E5E7EB]" /> <span>0</span>
                  <span className="w-3.5 h-3.5 rounded bg-[#34D399]" /> <span>+10</span>
                  <span className="w-3.5 h-3.5 rounded bg-[#10B981]" /> <span>+25 (Underpred)</span>
                </div>
              ) : (
                <div className="flex items-center space-x-1 font-mono text-[10px] text-[#57534E]">
                  <span className="w-3.5 h-3.5 rounded bg-[#10B981]" /> <span>Low</span>
                  <span className="w-3.5 h-3.5 rounded bg-[#D97706]" /> <span>Mod</span>
                  <span className="w-3.5 h-3.5 rounded bg-[#EA580C]" /> <span>High</span>
                  <span className="w-3.5 h-3.5 rounded bg-[#E11D48]" /> <span>Very High</span>
                </div>
              )}
            </div>
          </div>

          {/* District Inspector Drilldown Panel (4 cols) */}
          {selectedDistrict && (
            <div className="lg:col-span-4 bg-white border border-[#E7E2DA] p-6 rounded shadow-sm relative">
              <button
                onClick={() => onSelectDistrict(null)}
                className="absolute top-4 right-4 text-[#78716C] hover:text-[#1C1917] p-1 rounded hover:bg-[#FAF8F5]"
              >
                <X className="w-4 h-4" />
              </button>

              <div className="flex items-center space-x-2 text-xs font-mono uppercase tracking-wider text-[#78716C] mb-2">
                <MapPin className="w-3.5 h-3.5 text-[#B85D3B]" />
                <span>District Inspector</span>
              </div>

              <h3 className="font-editorial text-2xl text-[#1C1917] font-normal mb-1">
                {selectedDistrict.name}
              </h3>
              <span className="text-xs text-[#57534E] block mb-4">
                {selectedDistrict.state} &bull; Lat: {selectedDistrict.lat.toFixed(2)}&deg;, Lon: {selectedDistrict.lon.toFixed(2)}&deg;
              </span>

              {/* Rainfall Comparison Card */}
              <div className="grid grid-cols-2 gap-3 p-4 bg-[#FAF8F5] border border-[#E7E2DA] rounded mb-5">
                <div>
                  <span className="text-[10px] font-mono uppercase text-[#78716C] block">Raw NWP</span>
                  <span className="text-xl font-editorial font-light text-[#1C1917]">
                    {selectedDistrict.raw_nwp_rainfall_mm} <span className="text-xs font-sans text-[#78716C]">mm</span>
                  </span>
                </div>
                <div>
                  <span className="text-[10px] font-mono uppercase text-[#B85D3B] font-semibold block">VARSHA-Q</span>
                  <span className="text-xl font-editorial font-bold text-[#B85D3B]">
                    {selectedDistrict.corrected_rainfall_mm} <span className="text-xs font-sans text-[#B85D3B]">mm</span>
                  </span>
                </div>
              </div>

              {/* Uncertainty Quantiles */}
              <div className="mb-5 text-xs">
                <span className="text-[11px] font-mono uppercase tracking-wider text-[#78716C] block mb-2">
                  Quantile Prediction Bounds:
                </span>
                <div className="flex items-center justify-between p-2.5 bg-[#FAF8F5] rounded border border-[#E7E2DA] text-[11px] font-mono">
                  <div>
                    <span className="text-[#78716C] block text-[10px]">P10 (Lower)</span>
                    <strong className="text-[#1C1917]">{selectedDistrict.uncertainty.lower_bound_p10_mm} mm</strong>
                  </div>
                  <div>
                    <span className="text-[#78716C] block text-[10px]">P50 (Median)</span>
                    <strong className="text-[#B85D3B]">{selectedDistrict.uncertainty.median_p50_mm} mm</strong>
                  </div>
                  <div>
                    <span className="text-[#78716C] block text-[10px]">P90 (Upper)</span>
                    <strong className="text-[#1C1917]">{selectedDistrict.uncertainty.upper_bound_p90_mm} mm</strong>
                  </div>
                </div>
              </div>

              {/* Exceedance Probabilities Breakdown */}
              <div className="mb-5 text-xs">
                <span className="text-[11px] font-mono uppercase tracking-wider text-[#78716C] block mb-2">
                  Heavy-Rain Probabilities:
                </span>
                <div className="grid grid-cols-3 gap-2 text-center font-mono">
                  <div className="p-2 bg-[#FAF8F5] border border-[#E7E2DA] rounded">
                    <span className="text-[10px] text-[#78716C] block">&gt; 25mm</span>
                    <span className="font-bold text-[#1C1917]">
                      {((selectedDistrict.heavy_rain_probabilities.p_gt_25mm || 0) * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="p-2 bg-[#FAF8F5] border border-[#E7E2DA] rounded">
                    <span className="text-[10px] text-[#78716C] block">&gt; 50mm</span>
                    <span className="font-bold text-[#B85D3B]">
                      {((selectedDistrict.heavy_rain_probabilities.p_gt_50mm || 0) * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="p-2 bg-[#FAF8F5] border border-[#E7E2DA] rounded">
                    <span className="text-[10px] text-[#78716C] block">&gt; 100mm</span>
                    <span className="font-bold text-[#7E361E]">
                      {((selectedDistrict.heavy_rain_probabilities.p_gt_100mm || 0) * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Physical Attribution Priors */}
              <div className="pt-4 border-t border-[#E7E2DA] text-xs text-[#57534E] space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1.5"><Mountain className="w-3.5 h-3.5 text-[#78716C]" /> Elevation:</span>
                  <span className="font-mono text-[#1C1917]">{selectedDistrict.elevation_m} m</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1.5"><Compass className="w-3.5 h-3.5 text-[#78716C]" /> Distance to Coast:</span>
                  <span className="font-mono text-[#1C1917]">{selectedDistrict.coastal_dist_km} km</span>
                </div>
                <div className="flex items-center justify-between pt-1">
                  <span className="flex items-center gap-1.5"><ShieldAlert className="w-3.5 h-3.5 text-[#B85D3B]" /> Model Risk:</span>
                  <span className="font-semibold text-[#B85D3B]">{selectedDistrict.risk_category}</span>
                </div>
              </div>

            </div>
          )}

        </div>

      </div>
    </section>
  );
};
