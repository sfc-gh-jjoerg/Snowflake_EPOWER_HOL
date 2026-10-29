'use client';

interface TimeSliderProps {
  minDate: string;  // YYYY-MM-DD
  maxDate: string;  // YYYY-MM-DD
  selectedDate: string;
  selectedHour: number | null;  // null = "All Day"
  onDateChange: (date: string) => void;
  onHourChange: (hour: number | null) => void;
}

function dateToIndex(date: string, minDate: string): number {
  const d = new Date(date).getTime();
  const m = new Date(minDate).getTime();
  return Math.round((d - m) / (1000 * 60 * 60 * 24));
}

function indexToDate(index: number, minDate: string): string {
  const d = new Date(minDate);
  d.setDate(d.getDate() + index);
  return d.toISOString().slice(0, 10);
}

function totalDays(minDate: string, maxDate: string): number {
  return dateToIndex(maxDate, minDate);
}

export default function TimeSlider({
  minDate,
  maxDate,
  selectedDate,
  selectedHour,
  onDateChange,
  onHourChange,
}: TimeSliderProps) {
  const days = totalDays(minDate, maxDate);
  const currentIndex = dateToIndex(selectedDate, minDate);

  const formatDate = (d: string) => {
    const dt = new Date(d);
    return dt.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit' });
  };

  return (
    <div className="mt-4 space-y-2">
      {/* Day slider */}
      <div className="flex items-center gap-3">
        <span className="text-[11px] text-slate-500 w-12">{formatDate(minDate)}</span>
        <input
          type="range"
          min={0}
          max={days}
          value={currentIndex}
          onChange={(e) => {
            const newDate = indexToDate(parseInt(e.target.value, 10), minDate);
            onDateChange(newDate);
          }}
          className="flex-1 h-1.5 appearance-none rounded-full bg-slate-700 cursor-pointer
            [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-3.5
            [&::-webkit-slider-thumb]:w-3.5 [&::-webkit-slider-thumb]:rounded-full
            [&::-webkit-slider-thumb]:bg-cyan-400 [&::-webkit-slider-thumb]:shadow-md"
        />
        <span className="text-[11px] text-slate-500 w-12 text-right">{formatDate(maxDate)}</span>
      </div>

      {/* Date label + hour picker */}
      <div className="flex items-center gap-3 flex-wrap">
        <span className="text-xs text-slate-300 font-medium min-w-[90px]">
          {selectedDate} {selectedHour != null ? `${String(selectedHour).padStart(2, '0')}:00` : '(all day)'}
        </span>
        <div className="flex items-center gap-1 flex-wrap">
          <button
            onClick={() => onHourChange(null)}
            className={`px-2 py-0.5 rounded text-[10px] font-medium transition-colors ${
              selectedHour == null
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                : 'bg-slate-800 text-slate-400 border border-slate-700 hover:border-slate-500'
            }`}
          >
            All Day
          </button>
          {Array.from({ length: 24 }, (_, i) => (
            <button
              key={i}
              onClick={() => onHourChange(i)}
              className={`w-6 py-0.5 rounded text-[10px] font-medium transition-colors ${
                selectedHour === i
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                  : 'bg-slate-800 text-slate-500 border border-slate-700 hover:border-slate-500'
              }`}
            >
              {String(i).padStart(2, '0')}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
