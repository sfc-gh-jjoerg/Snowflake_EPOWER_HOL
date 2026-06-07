'use client';

import { useCallback, useEffect, useState } from 'react';
import FilterBar from '@/components/FilterBar';
import KpiCard from '@/components/KpiCard';
import PriceCapacityChart from '@/components/PriceCapacityChart';
import BatteryActionsChart from '@/components/BatteryActionsChart';
import RevenueChart from '@/components/RevenueChart';

const REGIONS = ['North', 'South', 'East', 'West'];
const CUSTOMER_TYPES = ['Privatkunde', 'Kleingewerbe', 'Gewerbekunde'];

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
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [dateFrom, setDateFrom] = useState(defaultFrom);
  const [dateTo, setDateTo] = useState(defaultTo);

  const [kpis, setKpis] = useState<KpiData>({});
  const [timeseries, setTimeseries] = useState<unknown[]>([]);
  const [actions, setActions] = useState<unknown[]>([]);
  const [loading, setLoading] = useState(true);

  const buildParams = useCallback(() => {
    const params = new URLSearchParams();
    if (selectedRegions.length > 0) params.set('region', selectedRegions.join(','));
    if (selectedTypes.length > 0) params.set('type', selectedTypes.join(','));
    if (dateFrom) params.set('from', dateFrom);
    if (dateTo) params.set('to', dateTo);
    return params.toString();
  }, [selectedRegions, selectedTypes, dateFrom, dateTo]);

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
        onRegionsChange={setSelectedRegions}
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
        />
        <KpiCard
          label="Avg Battery SOC"
          value={formatNum(kpis.avg_battery_soc_pct, 1)}
          unit="%"
          color="battery"
        />
        <KpiCard
          label="Avg Solar Yield"
          value={formatNum(kpis.avg_solar_kw, 1)}
          unit="kW"
          color="solar"
        />
        <KpiCard
          label="Avg Price"
          value={formatNum(kpis.avg_price_eur_mwh, 1)}
          unit="EUR/MWh"
          color="price"
        />
        <KpiCard
          label="Customer Margin"
          value={formatEur(kpis.total_customer_margin)}
          unit="EUR"
          color="margin"
          subvalue="total period"
        />
        <KpiCard
          label="EPOWER Margin"
          value={formatEur(kpis.total_epower_margin)}
          unit="EUR"
          color="margin"
          subvalue="total period"
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

      {/* Footer */}
      <footer className="text-center text-xs text-slate-600 pt-4 border-t border-slate-800/50">
        EPOWER Energie Deutschland GmbH — VPP Monitor v1.0 — Powered by Snowflake App Runtime
      </footer>
    </main>
  );
}
