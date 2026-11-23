/**
 * Distribution summary component for displaying statistics (min, 25%, 50%, 75%, max)
 */
export default function DistributionChart({ title, stats }) {
  if (!stats || typeof stats !== 'object') return null;

  const min = stats['min'] ?? 0;
  const p25 = stats['25%'] ?? 0;
  const p50 = stats['50%'] ?? 0;
  const p75 = stats['75%'] ?? 0;
  const max = stats['max'] ?? 100;
  const mean = stats['mean'] ?? 0;
  const std = stats['std'] ?? 0;

  const range = max - min || 1;
  const getPercent = (val) => Math.max(0, Math.min(100, ((val - min) / range) * 100));

  return (
    <div className="p-3 bg-slate-50 rounded-md border border-slate-200 text-xs">
      <div className="flex items-center justify-between mb-2">
        <span className="font-medium text-slate-800 truncate">{title}</span>
        <span className="text-[11px] text-slate-500 font-mono">μ: {mean} | σ: {std}</span>
      </div>

      {/* Visual range track */}
      <div className="relative h-2.5 bg-slate-200 rounded-full my-3">
        {/* IQR Box (25% to 75%) */}
        <div
          className="absolute top-0 bottom-0 bg-blue-400 rounded-xs opacity-75"
          style={{
            left: `${getPercent(p25)}%`,
            width: `${Math.max(4, getPercent(p75) - getPercent(p25))}%`,
          }}
        />
        {/* Median marker */}
        <div
          className="absolute top-[-3px] bottom-[-3px] w-1 bg-blue-700 rounded-full"
          style={{ left: `${getPercent(p50)}%` }}
          title={`Median: ${p50}`}
        />
      </div>

      <div className="grid grid-cols-5 text-[10px] text-slate-500 font-mono text-center pt-1 border-t border-slate-200/60">
        <div>
          <span className="text-slate-400 block">Min</span>
          {min}
        </div>
        <div>
          <span className="text-slate-400 block">Q1</span>
          {p25}
        </div>
        <div>
          <span className="text-blue-700 font-semibold block">Med</span>
          {p50}
        </div>
        <div>
          <span className="text-slate-400 block">Q3</span>
          {p75}
        </div>
        <div>
          <span className="text-slate-400 block">Max</span>
          {max}
        </div>
      </div>
    </div>
  );
}
