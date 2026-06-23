'use client';

import { useCallback, useMemo, useState } from 'react';
import Map, { Marker, Popup } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';

interface ClusterData {
  CLUSTER_ID: string;
  CLUSTER_NAME: string;
  CENTROID_LAT: number;
  CENTROID_LNG: number;
  REGION_CHARACTER: string;
  COMPASS_REGION: string;
  ACTIVE_DEVICES: number;
  AVG_SOC_PCT: number;
  AVG_SOLAR_KW: number;
  TOTAL_IMPORT_KWH: number;
  TOTAL_EXPORT_KWH: number;
  NET_FLOW_KWH: number;
  AVG_PRICE_EUR_MWH: number;
  FLOW_DIRECTION: string;
}

interface ClusterMapProps {
  data: ClusterData[];
  loading: boolean;
  selectedHour: string;
  availableHours: string[];
  onHourChange: (hour: string) => void;
}

function getCircleColor(netFlow: number): string {
  if (netFlow < -50) return '#10b981'; // strong export — green
  if (netFlow < -10) return '#6ee7b7'; // moderate export — light green
  if (netFlow < 10) return '#fbbf24';  // neutral — yellow
  if (netFlow < 50) return '#fb923c';  // moderate import — orange
  return '#ef4444';                     // strong import — red
}

function getCircleRadius(activeDevices: number): number {
  const minR = 20;
  const maxR = 50;
  const minDevices = 100;
  const maxDevices = 3000;
  const clamped = Math.max(minDevices, Math.min(maxDevices, activeDevices));
  return minR + ((clamped - minDevices) / (maxDevices - minDevices)) * (maxR - minR);
}

export default function ClusterMap({
  data,
  loading,
  selectedHour,
  availableHours,
  onHourChange,
}: ClusterMapProps) {
  const [popupInfo, setPopupInfo] = useState<ClusterData | null>(null);

  const formatNum = (n: number, decimals = 0) =>
    n != null ? n.toLocaleString('de-DE', { maximumFractionDigits: decimals }) : '—';

  const hourLabel = useMemo(() => {
    if (!selectedHour) return '';
    const d = new Date(selectedHour);
    return `${d.toLocaleDateString('de-DE')} ${d.getHours().toString().padStart(2, '0')}:00`;
  }, [selectedHour]);

  const handleHourSlider = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const idx = parseInt(e.target.value, 10);
      if (availableHours[idx]) onHourChange(availableHours[idx]);
    },
    [availableHours, onHourChange]
  );

  const currentIdx = availableHours.indexOf(selectedHour);

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/50 overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold text-slate-200">VPP Cluster Map</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            {loading ? 'Loading...' : `${data.length} clusters — ${hourLabel}`}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-emerald-400">● Export</span>
          <span className="text-[10px] text-yellow-400">● Neutral</span>
          <span className="text-[10px] text-red-400">● Import</span>
        </div>
      </div>

      <div className="relative h-[420px]">
        <Map
          initialViewState={{
            latitude: 51.2,
            longitude: 10.4,
            zoom: 5.3,
          }}
          style={{ width: '100%', height: '100%' }}
          mapStyle="https://tiles.openfreemap.org/styles/liberty"
        >
          {data.map((cluster) => (
            <Marker
              key={cluster.CLUSTER_ID}
              latitude={cluster.CENTROID_LAT}
              longitude={cluster.CENTROID_LNG}
              anchor="center"
            >
              <div
                className="rounded-full opacity-80 hover:opacity-100 cursor-pointer transition-opacity border border-white/20"
                style={{
                  width: getCircleRadius(cluster.ACTIVE_DEVICES),
                  height: getCircleRadius(cluster.ACTIVE_DEVICES),
                  backgroundColor: getCircleColor(cluster.NET_FLOW_KWH),
                }}
                onClick={() => setPopupInfo(cluster)}
              />
            </Marker>
          ))}

          {popupInfo && (
            <Popup
              latitude={popupInfo.CENTROID_LAT}
              longitude={popupInfo.CENTROID_LNG}
              anchor="bottom"
              onClose={() => setPopupInfo(null)}
              closeOnClick={false}
              className="[&_.maplibregl-popup-content]:!bg-slate-800 [&_.maplibregl-popup-content]:!text-slate-200 [&_.maplibregl-popup-content]:!rounded-lg [&_.maplibregl-popup-content]:!border [&_.maplibregl-popup-content]:!border-slate-700 [&_.maplibregl-popup-content]:!shadow-xl [&_.maplibregl-popup-content]:!p-3"
            >
              <div className="text-xs space-y-1 min-w-[180px]">
                <div className="font-semibold text-sm">{popupInfo.CLUSTER_NAME}</div>
                <div className="text-slate-400 text-[10px]">{popupInfo.REGION_CHARACTER}</div>
                <hr className="border-slate-700 my-1" />
                <div className="flex justify-between">
                  <span className="text-slate-400">Active Devices</span>
                  <span>{formatNum(popupInfo.ACTIVE_DEVICES)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Net Flow</span>
                  <span className={popupInfo.NET_FLOW_KWH > 0 ? 'text-red-400' : 'text-emerald-400'}>
                    {formatNum(popupInfo.NET_FLOW_KWH, 1)} kWh
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Avg SOC</span>
                  <span>{formatNum(popupInfo.AVG_SOC_PCT, 1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Avg Solar</span>
                  <span>{formatNum(popupInfo.AVG_SOLAR_KW, 1)} kW</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Avg Price</span>
                  <span>{formatNum(popupInfo.AVG_PRICE_EUR_MWH, 1)} €/MWh</span>
                </div>
              </div>
            </Popup>
          )}
        </Map>
      </div>

      {/* Hour slider */}
      {availableHours.length > 1 && (
        <div className="px-4 py-3 border-t border-slate-800 flex items-center gap-3">
          <span className="text-xs text-slate-500 w-10 shrink-0">
            {availableHours.length > 0
              ? `${new Date(availableHours[0]).getHours().toString().padStart(2, '0')}:00`
              : ''}
          </span>
          <input
            type="range"
            min={0}
            max={availableHours.length - 1}
            value={currentIdx >= 0 ? currentIdx : 0}
            onChange={handleHourSlider}
            className="flex-1 h-1.5 accent-sky-500 cursor-pointer"
          />
          <span className="text-xs text-slate-500 w-10 shrink-0 text-right">
            {availableHours.length > 0
              ? `${new Date(availableHours[availableHours.length - 1]).getHours().toString().padStart(2, '0')}:00`
              : ''}
          </span>
          <span className="text-xs text-slate-300 font-mono w-12 text-right">{hourLabel.split(' ')[1] || ''}</span>
        </div>
      )}
    </div>
  );
}
