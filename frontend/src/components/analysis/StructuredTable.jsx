import { useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export default function StructuredTable({
  columns = [],
  rows = [],
  pageSize = 5,
  title = '',
}) {
  const [page, setPage] = useState(0);

  if (!rows || rows.length === 0) {
    return (
      <div className="my-2 p-3 rounded border border-slate-200 bg-slate-50 text-xs text-slate-500 text-center">
        No tabular rows returned.
      </div>
    );
  }

  // Derive columns if not explicitly supplied
  const effectiveColumns =
    columns.length > 0
      ? columns
      : Object.keys(rows[0] || {}).map((key) => ({ key, label: key }));

  const totalPages = Math.ceil(rows.length / pageSize);
  const currentRows = rows.slice(page * pageSize, (page + 1) * pageSize);

  return (
    <div className="my-3 rounded-md border border-slate-200 overflow-hidden bg-white text-xs">
      {title && (
        <div className="px-3 py-2 bg-slate-50 border-b border-slate-200 font-semibold text-slate-700">
          {title}
        </div>
      )}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold">
              {effectiveColumns.map((col, idx) => (
                <th key={idx} className="px-3 py-2 whitespace-nowrap">
                  {col.label || col.name || col.key}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {currentRows.map((row, rIdx) => (
              <tr key={rIdx} className="hover:bg-slate-50/70 transition-colors">
                {effectiveColumns.map((col, cIdx) => {
                  const val = row[col.key || col.name];
                  return (
                    <td key={cIdx} className="px-3 py-2 whitespace-nowrap text-slate-700 font-mono text-[11px]">
                      {val === null || val === undefined ? '—' : String(val)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between px-3 py-2 border-t border-slate-200 bg-slate-50 text-[11px] text-slate-600">
          <span>
            Page {page + 1} of {totalPages} ({rows.length} rows)
          </span>
          <div className="flex gap-1">
            <button
              type="button"
              disabled={page === 0}
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              className="p-1 rounded hover:bg-slate-200 disabled:opacity-30 disabled:hover:bg-transparent"
            >
              <ChevronLeft className="h-3.5 w-3.5" />
            </button>
            <button
              type="button"
              disabled={page >= totalPages - 1}
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              className="p-1 rounded hover:bg-slate-200 disabled:opacity-30 disabled:hover:bg-transparent"
            >
              <ChevronRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
