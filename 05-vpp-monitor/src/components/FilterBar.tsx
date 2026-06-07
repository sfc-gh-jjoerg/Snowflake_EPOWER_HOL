'use client';

interface FilterBarProps {
  regions: string[];
  selectedRegions: string[];
  onRegionsChange: (regions: string[]) => void;
  customerTypes: string[];
  selectedTypes: string[];
  onTypesChange: (types: string[]) => void;
  dateFrom: string;
  dateTo: string;
  onDateFromChange: (date: string) => void;
  onDateToChange: (date: string) => void;
}

export default function FilterBar({
  regions,
  selectedRegions,
  onRegionsChange,
  customerTypes,
  selectedTypes,
  onTypesChange,
  dateFrom,
  dateTo,
  onDateFromChange,
  onDateToChange,
}: FilterBarProps) {
  const toggleRegion = (region: string) => {
    if (selectedRegions.includes(region)) {
      onRegionsChange(selectedRegions.filter((r) => r !== region));
    } else {
      onRegionsChange([...selectedRegions, region]);
    }
  };

  const toggleType = (type: string) => {
    if (selectedTypes.includes(type)) {
      onTypesChange(selectedTypes.filter((t) => t !== type));
    } else {
      onTypesChange([...selectedTypes, type]);
    }
  };

  return (
    <div className="flex flex-wrap items-center gap-4 p-4 rounded-xl border border-slate-800 bg-slate-900/50">
      {/* Region chips */}
      <div className="flex items-center gap-2">
        <span className="text-xs uppercase tracking-wider text-slate-500 mr-1">Region</span>
        {regions.map((region) => (
          <button
            key={region}
            onClick={() => toggleRegion(region)}
            className={`filter-chip ${
              selectedRegions.includes(region) ? 'filter-chip-active' : ''
            }`}
          >
            {region}
          </button>
        ))}
      </div>

      {/* Separator */}
      <div className="w-px h-6 bg-slate-700" />

      {/* Customer type chips */}
      <div className="flex items-center gap-2">
        <span className="text-xs uppercase tracking-wider text-slate-500 mr-1">Type</span>
        {customerTypes.map((type) => (
          <button
            key={type}
            onClick={() => toggleType(type)}
            className={`filter-chip ${
              selectedTypes.includes(type) ? 'filter-chip-active' : ''
            }`}
          >
            {type}
          </button>
        ))}
      </div>

      {/* Separator */}
      <div className="w-px h-6 bg-slate-700" />

      {/* Date range */}
      <div className="flex items-center gap-2">
        <span className="text-xs uppercase tracking-wider text-slate-500 mr-1">Period</span>
        <input
          type="date"
          value={dateFrom}
          onChange={(e) => onDateFromChange(e.target.value)}
          className="bg-slate-800 border border-slate-700 rounded-lg px-2 py-1 text-sm text-slate-300
                     focus:border-cyan-500 focus:outline-none"
        />
        <span className="text-slate-500">—</span>
        <input
          type="date"
          value={dateTo}
          onChange={(e) => onDateToChange(e.target.value)}
          className="bg-slate-800 border border-slate-700 rounded-lg px-2 py-1 text-sm text-slate-300
                     focus:border-cyan-500 focus:outline-none"
        />
      </div>
    </div>
  );
}
