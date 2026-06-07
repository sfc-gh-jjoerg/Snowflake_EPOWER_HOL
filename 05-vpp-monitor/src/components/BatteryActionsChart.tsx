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
  action_count: number;
}

interface BatteryActionsChartProps {
  data: ActionRow[];
  loading?: boolean;
}

const ACTION_COLORS: Record<string, string> = {
  CHARGE: '#22d3ee',
  DISCHARGE: '#fbbf24',
  SELF_CONSUME: '#34d399',
  MAX_CHARGE: '#a78bfa',
};

export default function BatteryActionsChart({ data, loading }: BatteryActionsChartProps) {
  if (loading) {
    return (
      <div className="card h-[300px] flex items-center justify-center">
        <div className="animate-pulse text-slate-500">Loading actions...</div>
      </div>
    );
  }

  // Pivot: group by day, sum action counts across all regions/types
  const pivoted = Object.values(
    data.reduce<Record<string, Record<string, number | string>>>((acc, row) => {
      const key = row.day;
      if (!acc[key]) {
        acc[key] = { day: key, CHARGE: 0, DISCHARGE: 0, SELF_CONSUME: 0, MAX_CHARGE: 0 };
      }
      const action = row.battery_action;
      if (action in acc[key]) {
        (acc[key][action] as number) += row.action_count;
      }
      return acc;
    }, {})
  ).sort((a, b) => String(a.day).localeCompare(String(b.day)));

  return (
    <div className="card">
      <h3 className="text-sm font-medium text-slate-400 mb-3">
        Battery Actions by Day
      </h3>
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={pivoted} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            dataKey="day"
            tick={{ fill: '#64748b', fontSize: 11 }}
            tickFormatter={(v) => String(v).slice(5)}
          />
          <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
            labelStyle={{ color: '#94a3b8' }}
          />
          <Legend wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }} />
          <Bar dataKey="CHARGE" stackId="a" fill={ACTION_COLORS.CHARGE} />
          <Bar dataKey="DISCHARGE" stackId="a" fill={ACTION_COLORS.DISCHARGE} />
          <Bar dataKey="SELF_CONSUME" stackId="a" fill={ACTION_COLORS.SELF_CONSUME} />
          <Bar dataKey="MAX_CHARGE" stackId="a" fill={ACTION_COLORS.MAX_CHARGE} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
