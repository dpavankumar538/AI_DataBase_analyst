export default function MetricTrend({
  label,
  value,
  subtitle,
  icon: Icon,
  badge,
  className = '',
}) {
  return (
    <div className={`p-5 bg-white rounded-lg border border-slate-200 shadow-2xs ${className}`}>
      <div className="flex items-center justify-between text-slate-500 mb-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-600">{label}</span>
        {Icon && (
          <div className="p-2 rounded-md bg-slate-50 text-slate-600 border border-slate-100">
            <Icon className="h-4 w-4" />
          </div>
        )}
      </div>
      <div className="flex items-baseline gap-2">
        <span className="text-2xl font-bold tracking-tight text-slate-900">{value}</span>
        {badge && <span>{badge}</span>}
      </div>
      {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
    </div>
  );
}
