interface KpiCardProps {
  label: string;
  value: string;
  unit?: string;
  color: 'solar' | 'battery' | 'price' | 'grid' | 'margin';
  subvalue?: string;
}

const colorMap = {
  solar: 'text-solar-400',
  battery: 'text-battery-400',
  price: 'text-price-400',
  grid: 'text-grid-400',
  margin: 'text-margin-400',
};

const bgMap = {
  solar: 'bg-solar-400/5',
  battery: 'bg-battery-400/5',
  price: 'bg-price-400/5',
  grid: 'bg-grid-400/5',
  margin: 'bg-margin-400/5',
};

export default function KpiCard({ label, value, unit, color, subvalue }: KpiCardProps) {
  return (
    <div className={`card ${bgMap[color]} flex flex-col justify-between min-w-[160px]`}>
      <p className="text-xs uppercase tracking-wider text-slate-500 mb-2">{label}</p>
      <div className="flex items-baseline gap-1">
        <span className={`text-2xl font-semibold tabular-nums ${colorMap[color]}`}>
          {value}
        </span>
        {unit && <span className="text-sm text-slate-500">{unit}</span>}
      </div>
      {subvalue && (
        <p className="text-xs text-slate-500 mt-1">{subvalue}</p>
      )}
    </div>
  );
}
