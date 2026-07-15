'use client';

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface ActionRow {
  day: string;
  region: string;
  customer_type: string;
  battery_action: string;
  customer_margin_eur: number;
  epower_margin_eur: number;
  net_margin_eur: number;
}

interface RevenueChartProps {
  data: ActionRow[];
  loading?: boolean;
}

export default function RevenueChart({ data, loading }: RevenueChartProps) {
  if (loading) {
    return (
      <div className="card h-[300px] flex items-center justify-center">
        <div className="animate-pulse text-slate-500">Loading margins...</div>
      </div>
    );
  }

  if (!Array.isArray(data) || data.length === 0) {
    return (
      <div className="card h-[300px] flex items-center justify-center">
        <div className="text-slate-500">No margin data available</div>
      </div>
    );
  }

  // Aggregate by region: sum customer and epower margins
  const byRegion = Object.values(
    data.reduce<Record<string, { region: string; customer: number; epower: number }>>((acc, row) => {
      const key = row.region;
      if (!acc[key]) {
        acc[key] = { region: key, customer: 0, epower: 0 };
      }
      acc[key].customer += row.customer_margin_eur || 0;
      acc[key].epower += row.epower_margin_eur || 0;
      return acc;
    }, {})
  ).map((d) => ({
    region: d.region,
    'Customer Margin (EUR)': Number(d.customer.toFixed(0)),
    'EPOWER Margin (EUR)': Number(d.epower.toFixed(0)),
  }));

  return (
    <div className="card">
      <h3 className="text-sm font-medium text-slate-400 mb-3">
        Revenue Breakdown by Region
      </h3>
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={byRegion} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="region" tick={{ fill: '#64748b', fontSize: 12 }} />
          <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
            labelStyle={{ color: '#94a3b8' }}
            formatter={(value: number) => `${value.toLocaleString()} EUR`}
          />
          <Legend wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }} />
          <Bar dataKey="Customer Margin (EUR)" fill="#22d3ee" radius={[4, 4, 0, 0]} />
          <Bar dataKey="EPOWER Margin (EUR)" fill="#a78bfa" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
