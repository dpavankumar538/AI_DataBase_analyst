export function LoadingSpinner({ size = 'md', className = '' }) {
  const sizes = {
    sm: 'h-4 w-4 border-2',
    md: 'h-6 w-6 border-2',
    lg: 'h-8 w-8 border-3',
  };

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <div
        className={`${sizes[size] || sizes.md} animate-spin rounded-full border-blue-600 border-t-transparent`}
      />
    </div>
  );
}

export function SkeletonRow({ cols = 4, rows = 3 }) {
  return (
    <div className="w-full space-y-3">
      {Array.from({ length: rows }).map((_, rIdx) => (
        <div key={rIdx} className="flex gap-4 items-center">
          {Array.from({ length: cols }).map((_, cIdx) => (
            <div
              key={cIdx}
              className="h-4 bg-slate-100 rounded animate-pulse"
              style={{ width: `${100 / cols}%` }}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

export function SkeletonCard() {
  return (
    <div className="p-5 border border-slate-200 rounded-lg bg-white space-y-3 animate-pulse">
      <div className="h-4 w-1/3 bg-slate-100 rounded" />
      <div className="h-6 w-1/2 bg-slate-200 rounded" />
      <div className="h-3 w-2/3 bg-slate-100 rounded" />
    </div>
  );
}
