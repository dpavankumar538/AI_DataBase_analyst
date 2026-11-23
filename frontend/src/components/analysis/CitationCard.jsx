import { FileText } from 'lucide-react';
import Badge from '../common/Badge';

export default function CitationCard({ citation, documentName = '' }) {
  if (!citation) return null;

  const page = citation.page_number ?? citation.page;
  const distance = citation.distance !== undefined ? Number(citation.distance).toFixed(3) : null;
  const textSnippet = citation.text || citation.snippet || '';

  return (
    <div className="p-3 bg-amber-50/40 rounded-md border border-amber-200/80 text-xs text-slate-800">
      <div className="flex items-center justify-between gap-2 mb-1.5">
        <div className="flex items-center gap-1.5 font-medium text-amber-900">
          <FileText className="h-3.5 w-3.5 text-amber-600 shrink-0" />
          <span className="truncate">{documentName || `Document #${citation.document_id || ''}`}</span>
        </div>
        <div className="flex items-center gap-1 shrink-0">
          {page !== undefined && (
            <Badge variant="warning" size="sm">
              Page {page}
            </Badge>
          )}
          {distance !== null && (
            <span className="text-[10px] text-slate-500 font-mono" title="Vector Cosine Distance">
              dist: {distance}
            </span>
          )}
        </div>
      </div>
      {textSnippet && (
        <blockquote className="italic text-slate-600 text-[11px] border-l-2 border-amber-300 pl-2.5 my-1 leading-relaxed">
          &ldquo;{textSnippet}&rdquo;
        </blockquote>
      )}
    </div>
  );
}
