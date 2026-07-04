'use client';

import { useCallback, useEffect, useState } from 'react';
import FilterBar from '@/components/FilterBar';
import KpiCard from '@/components/KpiCard';
import RegionalChart from '@/components/RegionalChart';
import PriceCapacityChart from '@/components/PriceCapacityChart';
import BatteryActionsChart from '@/components/BatteryActionsChart';
import RevenueChart from '@/components/RevenueChart';

const REGIONS = ['North', 'South', 'East', 'West'];
const CUSTOMER_TYPES = ['Privatkunde', 'Kleingewerbe', 'Gewerbekunde'];

// Cluster definitions: id → { name, compassRegion }
const CLUSTERS: Record<string, { name: string; compassRegion: string }> = {
  freiburg_oberrhein: { name: 'Freiburg/Oberrhein', compassRegion: 'South' },
  bavaria_south:      { name: 'Bayern Sued', compassRegion: 'South' },
  munich_metro:       { name: 'Muenchen Metro', compassRegion: 'South' },
  stuttgart_metro:    { name: 'Stuttgart Metro', compassRegion: 'South' },
  nuernberg_franken:  { name: 'Nuernberg/Franken', compassRegion: 'South' },
  frankfurt_main:     { name: 'Frankfurt/Rhein-Main', compassRegion: 'West' },
  koeln_bonn:         { name: 'Koeln/Bonn', compassRegion: 'West' },
  rhine_ruhr:         { name: 'Rhein-Ruhr', compassRegion: 'West' },
  berlin_metro:       { name: 'Berlin Metro', compassRegion: 'East' },
  leipzig_halle:      { name: 'Leipzig/Halle', compassRegion: 'East' },
  saxony_east:        { name: 'Sachsen/Ost', compassRegion: 'East' },
  hamburg_metro:      { name: 'Hamburg Metro', compassRegion: 'North' },
  bremen_weser:       { name: 'Bremen/Weser', compassRegion: 'North' },
  lower_saxony:       { name: 'Niedersachsen/Nord', compassRegion: 'North' },
};

function getClustersForRegions(regions: string[]): string[] {
  if (regions.length === 0) return [];
  return Object.entries(CLUSTERS)
    .filter(([, c]) => regions.includes(c.compassRegion))
    .map(([id]) => id);
}

// Default date range: last 30 days
function defaultFrom() {
  const d = new Date();
  d.setDate(d.getDate() - 30);
  return d.toISOString().slice(0, 10);
}
function defaultTo() {
  return new Date().toISOString().slice(0, 10);
}

interface KpiData {
  avg_active_devices?: number;
  avg_battery_soc_pct?: number;
  avg_solar_kw?: number;
  total_net_grid_kwh?: number;
  avg_price_eur_mwh?: number;
  total_customer_margin?: number;
  total_epower_margin?: number;
  total_net_margin?: number;
}

export default function Dashboard() {
  const [selectedRegions, setSelectedRegions] = useState<string[]>([]);
  const [selectedClusters, setSelectedClusters] = useState<string[]>([]);
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [dateFrom, setDateFrom] = useState(defaultFrom);
  const [dateTo, setDateTo] = useState(defaultTo);

  const [kpis, setKpis] = useState<KpiData>({});
  const [timeseries, setTimeseries] = useState<unknown[]>([]);
  const [actions, setActions] = useState<unknown[]>([]);
  const [loading, setLoading] = useState(true);

  // When regions change, auto-select all clusters in those regions
  const handleRegionsChange = useCallback((regions: string[]) => {
    setSelectedRegions(regions);
    if (regions.length > 0) {
      setSelectedClusters(getClustersForRegions(regions));
    } else {
      setSelectedClusters([]);
    }
  }, []);

  const buildParams = useCallback(() => {
    const params = new URLSearchParams();
    if (selectedRegions.length > 0) params.set('region', selectedRegions.join(','));
    if (selectedClusters.length > 0) params.set('cluster', selectedClusters.join(','));
    if (selectedTypes.length > 0) params.set('type', selectedTypes.join(','));
    if (dateFrom) params.set('from', dateFrom);
    if (dateTo) params.set('to', dateTo);
    return params.toString();
  }, [selectedRegions, selectedClusters, selectedTypes, dateFrom, dateTo]);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const params = buildParams();

      try {
        const [kpiRes, tsRes, actRes] = await Promise.all([
          fetch(`/api/kpis?${params}`),
          fetch(`/api/timeseries?${params}&granularity=daily`),
          fetch(`/api/actions?${params}`),
        ]);

        const [kpiData, tsData, actData] = await Promise.all([
          kpiRes.json(),
          tsRes.json(),
          actRes.json(),
        ]);

        setKpis(kpiData);
        setTimeseries(tsData);
        setActions(actData);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [buildParams]);

  const formatNum = (n?: number, decimals = 0) =>
    n != null ? n.toLocaleString('de-DE', { maximumFractionDigits: decimals }) : '—';

  const formatEur = (n?: number) =>
    n != null
      ? `${n >= 0 ? '+' : ''}${n.toLocaleString('de-DE', { maximumFractionDigits: 0 })}`
      : '—';

  return (
    <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">EPOWER VPP Monitor</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Virtual Power Plant Performance Dashboard
          </p>
        </div>
        <div className="text-xs text-slate-600">
          Data: {dateFrom} — {dateTo}
        </div>
      </div>

      {/* Filters */}
      <FilterBar
        regions={REGIONS}
        selectedRegions={selectedRegions}
        onRegionsChange={handleRegionsChange}
        clusters={CLUSTERS}
        selectedClusters={selectedClusters}
        onClustersChange={setSelectedClusters}
        customerTypes={CUSTOMER_TYPES}
        selectedTypes={selectedTypes}
        onTypesChange={setSelectedTypes}
        dateFrom={dateFrom}
        dateTo={dateTo}
        onDateFromChange={setDateFrom}
        onDateToChange={setDateTo}
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        <KpiCard
          label="Active Devices"
          value={formatNum(kpis.avg_active_devices)}
          color="battery"
          subvalue="avg batteries in VPP"
        />
        <KpiCard
          label="Avg Battery SOC"
          value={formatNum(kpis.avg_battery_soc_pct, 1)}
          unit="%"
          color="battery"
          subvalue="state of charge"
        />
        <KpiCard
          label="Avg Solar Yield"
          value={formatNum(kpis.avg_solar_kw, 1)}
          unit="kW"
          color="solar"
          subvalue="generation per device"
        />
        <KpiCard
          label="Spot Price"
          value={formatNum(kpis.avg_price_eur_mwh, 1)}
          unit="EUR/MWh"
          color="price"
          subvalue="avg day-ahead market"
        />
        <KpiCard
          label="Customer Savings"
          value={formatEur(kpis.total_customer_margin)}
          unit="EUR"
          color="margin"
          subvalue="VPP participation revenue"
        />
        <KpiCard
          label="EPOWER Revenue"
          value={formatEur(kpis.total_epower_margin)}
          unit="EUR"
          color="margin"
          subvalue="platform trading margin"
        />
      </div>

      {/* Main Chart: Price vs Capacity */}
      <PriceCapacityChart
        data={timeseries as never[]}
        loading={loading}
      />

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <BatteryActionsChart
          data={actions as never[]}
          loading={loading}
        />
        <RevenueChart
          data={actions as never[]}
          loading={loading}
        />
      </div>

      {/* Regional Comparison with time slider */}
      <RegionalChart selectedClusters={selectedClusters} />

      {/* Footer */}
      <footer className="text-center text-xs text-slate-600 pt-4 border-t border-slate-800/50">
        EPOWER Energie Deutschland GmbH — VPP Monitor v1.0 — Powered by Snowflake App Runtime
      </footer>
    </main>
  );
}
