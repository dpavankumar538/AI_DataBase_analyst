import Button from './Button';

export default function EmptyState({
  icon: Icon,
  title,
  description,
  actionText,
  onAction,
  actionIcon: ActionIcon,
  className = '',
}) {
  return (
    <div className={`flex flex-col items-center justify-center p-8 text-center rounded-lg border border-dashed border-slate-200 bg-slate-50/50 ${className}`}>
      {Icon && (
        <div className="p-3 bg-white rounded-full border border-slate-200 text-slate-400 shadow-2xs mb-3">
          <Icon className="h-6 w-6 stroke-[1.75]" />
        </div>
      )}
      <h3 className="text-sm font-semibold text-slate-800">{title}</h3>
      {description && <p className="text-xs text-slate-500 max-w-sm mt-1 mb-4 leading-relaxed">{description}</p>}
      {actionText && onAction && (
        <Button size="sm" variant="outline" onClick={onAction} icon={ActionIcon}>
          {actionText}
        </Button>
      )}
    </div>
  );
}
