'use client';

interface FilterBarProps {
  regions: string[];
  selectedRegions: string[];
  onRegionsChange: (regions: string[]) => void;
  clusters: Record<string, { name: string; compassRegion: string }>;
  selectedClusters: string[];
  onClustersChange: (clusters: string[]) => void;
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
  clusters,
  selectedClusters,
  onClustersChange,
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

  const toggleCluster = (clusterId: string) => {
    if (selectedClusters.includes(clusterId)) {
      onClustersChange(selectedClusters.filter((c) => c !== clusterId));
    } else {
      onClustersChange([...selectedClusters, clusterId]);
    }
  };

  const toggleType = (type: string) => {
    if (selectedTypes.includes(type)) {
      onTypesChange(selectedTypes.filter((t) => t !== type));
    } else {
      onTypesChange([...selectedTypes, type]);
    }
  };

  // Get clusters grouped by compass region (only for selected regions)
  const visibleClusters = selectedRegions.length > 0
    ? Object.entries(clusters).filter(([, c]) => selectedRegions.includes(c.compassRegion))
    : [];

  const clustersByRegion = visibleClusters.reduce<Record<string, { id: string; name: string }[]>>(
    (acc, [id, c]) => {
      if (!acc[c.compassRegion]) acc[c.compassRegion] = [];
      acc[c.compassRegion].push({ id, name: c.name });
      return acc;
    },
    {}
  );

  const allVisible = visibleClusters.map(([id]) => id);
  const allSelected = allVisible.length > 0 && allVisible.every((id) => selectedClusters.includes(id));
  const noneSelected = allVisible.length > 0 && !allVisible.some((id) => selectedClusters.includes(id));

  const selectAll = () => {
    const others = selectedClusters.filter((c) => !allVisible.includes(c));
    onClustersChange([...others, ...allVisible]);
  };

  const clearAll = () => {
    onClustersChange(selectedClusters.filter((c) => !allVisible.includes(c)));
  };

  return (
    <div className="space-y-0">
      {/* Main filter row */}
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

      {/* Cluster chip row (appears when regions are selected) */}
      <div
        className={`overflow-hidden transition-all duration-300 ease-in-out ${
          selectedRegions.length > 0 ? 'max-h-40 opacity-100 mt-2' : 'max-h-0 opacity-0'
        }`}
      >
        <div className="flex flex-wrap items-center gap-3 px-4 py-3 rounded-xl border border-slate-800/60 bg-slate-900/30">
          <span className="text-xs uppercase tracking-wider text-slate-500 mr-1">Cluster</span>

          {/* Quick actions */}
          <div className="flex items-center gap-1 mr-2">
            <button
              onClick={selectAll}
              disabled={allSelected}
              className="text-[10px] px-1.5 py-0.5 rounded text-slate-400 hover:text-cyan-400
                         disabled:opacity-30 disabled:cursor-default transition-colors"
            >
              All
            </button>
            <span className="text-slate-700">|</span>
            <button
              onClick={clearAll}
              disabled={noneSelected}
              className="text-[10px] px-1.5 py-0.5 rounded text-slate-400 hover:text-cyan-400
                         disabled:opacity-30 disabled:cursor-default transition-colors"
            >
              None
            </button>
          </div>

          {/* Cluster chips grouped by region */}
          {Object.entries(clustersByRegion).map(([region, regionClusters]) => (
            <div key={region} className="flex items-center gap-1.5">
              <span className="text-[10px] text-slate-600 font-medium">{region}:</span>
              {regionClusters.map(({ id, name }) => (
                <button
                  key={id}
                  onClick={() => toggleCluster(id)}
                  className={`filter-chip-sm ${
                    selectedClusters.includes(id) ? 'filter-chip-sm-active' : ''
                  }`}
                >
                  {name}
                </button>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
