export default function Card({
  title,
  subtitle,
  actions,
  children,
  footer,
  className = '',
  bodyClassName = '',
}) {
  return (
    <div className={`bg-white rounded-lg border border-slate-200 shadow-xs overflow-hidden ${className}`}>
      {(title || actions) && (
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
          <div>
            {title && <h3 className="text-sm font-semibold text-slate-800">{title}</h3>}
            {subtitle && <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>}
          </div>
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </div>
      )}
      <div className={`p-5 ${bodyClassName}`}>{children}</div>
      {footer && <div className="border-t border-slate-100 bg-slate-50/50 px-5 py-3">{footer}</div>}
    </div>
  );
}
