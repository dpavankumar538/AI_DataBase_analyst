import { useId } from 'react';

export function Input({
  label,
  error,
  helperText,
  id,
  className = '',
  icon: Icon = null,
  ...props
}) {
  const generatedId = useId();
  const inputId = id || props.name || generatedId;

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={inputId} className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1.5">
          {label}
        </label>
      )}
      <div className="relative">
        {Icon && (
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
            <Icon className="h-4 w-4" />
          </div>
        )}
        <input
          id={inputId}
          className={`block w-full rounded-md border ${
            error ? 'border-rose-400 focus:border-rose-500 focus:ring-rose-200' : 'border-slate-300 focus:border-blue-500 focus:ring-blue-100'
          } bg-white text-slate-900 placeholder:text-slate-400 text-sm px-3 py-2 transition-colors focus:outline-none focus:ring-2 ${
            Icon ? 'pl-9' : ''
          } ${className}`}
          {...props}
        />
      </div>
      {error && <p className="mt-1 text-xs text-rose-600">{error}</p>}
      {helperText && !error && <p className="mt-1 text-xs text-slate-500">{helperText}</p>}
    </div>
  );
}

export function Select({
  label,
  error,
  options = [],
  id,
  className = '',
  ...props
}) {
  const generatedId = useId();
  const selectId = id || props.name || generatedId;

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={selectId} className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1.5">
          {label}
        </label>
      )}
      <select
        id={selectId}
        className={`block w-full rounded-md border ${
          error ? 'border-rose-400 focus:border-rose-500' : 'border-slate-300 focus:border-blue-500'
        } bg-white text-slate-900 text-sm px-3 py-2 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-100 ${className}`}
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && <p className="mt-1 text-xs text-rose-600">{error}</p>}
    </div>
  );
}

export function Textarea({
  label,
  error,
  id,
  rows = 3,
  className = '',
  ...props
}) {
  const generatedId = useId();
  const textareaId = id || props.name || generatedId;

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={textareaId} className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1.5">
          {label}
        </label>
      )}
      <textarea
        id={textareaId}
        rows={rows}
        className={`block w-full rounded-md border ${
          error ? 'border-rose-400 focus:border-rose-500 focus:ring-rose-200' : 'border-slate-300 focus:border-blue-500 focus:ring-blue-100'
        } bg-white text-slate-900 placeholder:text-slate-400 text-sm p-3 transition-colors focus:outline-none focus:ring-2 resize-y ${className}`}
        {...props}
      />
      {error && <p className="mt-1 text-xs text-rose-600">{error}</p>}
    </div>
  );
}
