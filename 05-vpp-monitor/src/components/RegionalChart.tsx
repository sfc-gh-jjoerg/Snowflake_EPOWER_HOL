'use client';

import { useEffect, useState } from 'react';
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
import TimeSlider from './TimeSlider';

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

interface DateRange {
  min_date: string;
  max_date: string;
}

interface RegionalChartProps {
  selectedClusters?: string[];
}

export default function RegionalChart({ selectedClusters = [] }: RegionalChartProps) {
  const [data, setData] = useState<ClusterRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState<DateRange | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [selectedHour, setSelectedHour] = useState<number | null>(null);

  // Fetch available date range on mount
  useEffect(() => {
    const fetchRange = async () => {
      try {
        const res = await fetch('/api/map-range');
        const range: DateRange = await res.json();
        setDateRange(range);
        setSelectedDate(range.max_date);
      } catch (error) {
        console.error('Failed to fetch date range:', error);
      }
    };
    fetchRange();
  }, []);

  // Fetch cluster data when date/hour/clusters change
  useEffect(() => {
    if (!selectedDate) return;

    const fetchData = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams({ date: selectedDate });
        if (selectedHour != null) params.set('hour', String(selectedHour));
        if (selectedClusters.length > 0) params.set('cluster', selectedClusters.join(','));
        const res = await fetch(`/api/map?${params}`);
        const rows: ClusterRow[] = await res.json();
        setData(rows);
      } catch (error) {
        console.error('Failed to fetch regional data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [selectedDate, selectedHour, selectedClusters]);

  if (!dateRange) {
    return (
      <div className="card h-[360px] flex items-center justify-center">
        <div className="animate-pulse text-slate-500">Loading regional data...</div>
      </div>
    );
  }

  const sorted = [...data].sort((a, b) => a.net_flow_kwh - b.net_flow_kwh);
  const timeLabel = selectedHour != null
    ? `${selectedDate} ${String(selectedHour).padStart(2, '0')}:00`
    : `${selectedDate} (all day)`;

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-slate-400">
          Regional Comparison — Net Energy Flow per Cluster ({timeLabel})
        </h3>
        <div className="flex items-center gap-3 text-[11px]">
          <span className="text-emerald-400">&#9664; Exporting to grid</span>
          <span className="text-red-400">Importing from grid &#9654;</span>
        </div>
      </div>

      {loading ? (
        <div className="h-[280px] flex items-center justify-center">
          <div className="animate-pulse text-slate-500">Loading...</div>
        </div>
      ) : (
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
              itemStyle={{ color: '#cbd5e1' }}
              formatter={(value: number) => [`${value > 0 ? '+' : ''}${value.toFixed(1)} kWh`, 'Net Flow']}
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
      )}

      <TimeSlider
        minDate={dateRange.min_date}
        maxDate={dateRange.max_date}
        selectedDate={selectedDate}
        selectedHour={selectedHour}
        onDateChange={setSelectedDate}
        onHourChange={setSelectedHour}
      />
    </div>
  );
}
