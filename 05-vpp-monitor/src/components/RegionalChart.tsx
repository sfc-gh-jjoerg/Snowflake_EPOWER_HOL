'use client';

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

interface ClusterRow {
  cluster_id: string;
  cluster_name: string;
  compass_region: string;
  active_devices: number;
  avg_soc_pct: number;
  avg_solar_kw: number;
  total_import_kwh: number;
  total_export_kwh: number;
  net_flow_kwh: number;
  avg_price_eur_mwh: number;
}

interface RegionalChartProps {
  data: ClusterRow[];
  loading?: boolean;
}

export default function RegionalChart({ data, loading }: RegionalChartProps) {
  if (loading) {
    return (
      <div className="card h-[300px] flex items-center justify-center">
        <div className="animate-pulse text-slate-500">Loading regional data...</div>
      </div>
    );
  }

  const sorted = [...data].sort((a, b) => a.net_flow_kwh - b.net_flow_kwh);

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-slate-400">
          Regional Comparison — Net Energy Flow (kWh)
        </h3>
        <div className="flex items-center gap-3 text-[11px]">
          <span className="text-emerald-400">Exporting</span>
          <span className="text-red-400">Importing</span>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart
          data={sorted}
          layout="vertical"
          margin={{ top: 5, right: 20, bottom: 5, left: 100 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
          <XAxis
            type="number"
            tick={{ fill: '#64748b', fontSize: 11 }}
            tickFormatter={(v: number) => `${v >= 0 ? '+' : ''}${v.toFixed(0)}`}
          />
          <YAxis
            type="category"
            dataKey="cluster_name"
            tick={{ fill: '#94a3b8', fontSize: 11 }}
            width={95}
          />
          <Tooltip
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
            labelStyle={{ color: '#e2e8f0', fontWeight: 600 }}
            formatter={(value: number, _name: string, props: { payload: ClusterRow }) => {
              const row = props.payload;
              return [
                `${value > 0 ? '+' : ''}${value.toFixed(1)} kWh`,
                `Net Flow | Devices: ${row.active_devices} | SOC: ${row.avg_soc_pct.toFixed(1)}%`,
              ];
            }}
          />
          <Bar dataKey="net_flow_kwh" radius={[0, 4, 4, 0]}>
            {sorted.map((entry, idx) => (
              <Cell
                key={idx}
                fill={entry.net_flow_kwh <= 0 ? '#34d399' : '#f87171'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
