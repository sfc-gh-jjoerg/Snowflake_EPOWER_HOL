'use client';

import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface TimeseriesRow {
  time: string;
  region: string;
  active_vpp_devices: number;
  avg_battery_soc_pct: number;
  avg_solar_yield_kw: number;
  net_grid_kw: number;
  price_eur_mwh: number;
}

interface PriceCapacityChartProps {
  data: TimeseriesRow[];
  loading?: boolean;
}

export default function PriceCapacityChart({ data, loading }: PriceCapacityChartProps) {
  if (loading) {
    return (
      <div className="card h-[340px] flex items-center justify-center">
        <div className="animate-pulse text-slate-500">Loading time-series...</div>
      </div>
    );
  }

  if (!Array.isArray(data) || data.length === 0) {
    return (
      <div className="card h-[340px] flex items-center justify-center">
        <div className="text-slate-500">No time-series data available</div>
      </div>
    );
  }

  // Aggregate across regions if multiple are selected
  const aggregated = Object.values(
    data.reduce<Record<string, {
      time: string;
      avgSoc: number;
      totalSolar: number;
      avgPrice: number;
      count: number;
    }>>((acc, row) => {
      const key = row.time;
      if (!acc[key]) {
        acc[key] = { time: key, avgSoc: 0, totalSolar: 0, avgPrice: 0, count: 0 };
      }
      acc[key].avgSoc += row.avg_battery_soc_pct;
      acc[key].totalSolar += row.avg_solar_yield_kw;
      acc[key].avgPrice += row.price_eur_mwh || 0;
      acc[key].count += 1;
      return acc;
    }, {})
  ).map((d) => ({
    time: d.time.slice(0, 10), // format as YYYY-MM-DD
    'Battery SOC (%)': Number((d.avgSoc / d.count).toFixed(1)),
    'Solar Yield (kW)': Number((d.totalSolar / d.count).toFixed(1)),
    'Price (EUR/MWh)': Number((d.avgPrice / d.count).toFixed(1)),
  }));

  return (
    <div className="card">
      <h3 className="text-sm font-medium text-slate-400 mb-3">
        Price vs. VPP Capacity
      </h3>
      <ResponsiveContainer width="100%" height={280}>
        <ComposedChart data={aggregated} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            dataKey="time"
            tick={{ fill: '#64748b', fontSize: 11 }}
            tickFormatter={(v) => v.slice(5)} // MM-DD
          />
          <YAxis
            yAxisId="left"
            tick={{ fill: '#64748b', fontSize: 11 }}
            label={{ value: '%  /  kW', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 11 }}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            tick={{ fill: '#64748b', fontSize: 11 }}
            label={{ value: 'EUR/MWh', angle: 90, position: 'insideRight', fill: '#64748b', fontSize: 11 }}
          />
          <Tooltip
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
            labelStyle={{ color: '#94a3b8' }}
          />
          <Legend wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }} />
          <Area
            yAxisId="left"
            type="monotone"
            dataKey="Battery SOC (%)"
            fill="#22d3ee"
            fillOpacity={0.1}
            stroke="#22d3ee"
            strokeWidth={1.5}
          />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="Solar Yield (kW)"
            stroke="#34d399"
            strokeWidth={2}
            dot={false}
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="Price (EUR/MWh)"
            stroke="#fbbf24"
            strokeWidth={2}
            dot={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
