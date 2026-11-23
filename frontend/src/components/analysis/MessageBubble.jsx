import { Sparkles, User, AlertCircle, CheckCircle2 } from 'lucide-react';
import Badge from '../common/Badge';
import SqlViewer from './SqlViewer';
import StructuredTable from './StructuredTable';
import CitationCard from './CitationCard';
import SimpleBarChart from '../charts/SimpleBarChart';
import { getRouteLabel } from '../../utils/helpers';
import { formatDate } from '../../utils/formatters';

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';

  if (isUser) {
    return (
      <div className="flex gap-3 justify-end items-start my-4">
        <div className="max-w-[85%] rounded-lg bg-blue-600 text-white p-4 shadow-2xs">
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
          <span className="text-[10px] text-blue-200 mt-2 block text-right font-mono">
            {formatDate(message.timestamp || message.created_at)}
          </span>
        </div>
        <div className="h-8 w-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-700 shrink-0 font-semibold text-xs border border-slate-300">
          <User className="h-4 w-4" />
        </div>
      </div>
    );
  }

  // AI Response
  const { label: routeLabel, color: routeColor } = getRouteLabel(message.route);
  const evaluationPassed =
    message.evaluation === 'passed' ||
    message.evaluation_result === 'passed' ||
    message.evaluation === 'acceptable';

  // Extract tabular rows if available
  let tableRows = [];
  let tableCols = [];
  let chartData = [];
  let sqlQuery = message.generated_query;

  if (message.structured_result && typeof message.structured_result === 'object') {
    const datasets = message.structured_result.datasets || [];
    for (const ds of datasets) {
      if (ds.sql_query && !sqlQuery) sqlQuery = ds.sql_query;
      if (ds.generated_sql && !sqlQuery) sqlQuery = ds.generated_sql;

      if (ds.result && Array.isArray(ds.result)) {
        tableRows = ds.result;
      } else if (ds.overview?.columns) {
        // Dataset overview columns
        tableRows = ds.overview.columns;
        tableCols = [
          { key: 'name', label: 'Column' },
          { key: 'data_type', label: 'Type' },
          { key: 'missing_values', label: 'Missing' },
          { key: 'unique_values', label: 'Unique' },
        ];
      }
    }
  }

  // Check if we can extract chart data from tableRows if numerical
  if (tableRows.length > 0 && tableRows.length <= 15) {
    const firstRow = tableRows[0];
    const keys = Object.keys(firstRow);
    const labelKey = keys.find((k) => typeof firstRow[k] === 'string') || keys[0];
    const numKey = keys.find((k) => typeof firstRow[k] === 'number');
    if (labelKey && numKey) {
      chartData = tableRows.map((r) => ({
        label: String(r[labelKey]),
        value: Number(r[numKey]),
      }));
    }
  }

  // Extract citations
  const citations = message.document_citations || message.document_context || [];

  return (
    <div className="flex gap-3 justify-start items-start my-4">
      <div className="h-8 w-8 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center shrink-0 border border-blue-200">
        <Sparkles className="h-4 w-4" />
      </div>

      <div className="flex-1 max-w-[92%] rounded-lg bg-white border border-slate-200 p-5 shadow-2xs">
        {/* Header with Route & Status */}
        <div className="flex items-center justify-between gap-2 border-b border-slate-100 pb-3 mb-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-800">AI Data Analysis</span>
            <Badge variant={routeColor === 'blue' ? 'info' : routeColor === 'purple' ? 'purple' : 'neutral'} size="sm">
              {routeLabel}
            </Badge>
          </div>

          <div className="flex items-center gap-2">
            {evaluationPassed && (
              <span className="inline-flex items-center gap-1 text-[11px] text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                <CheckCircle2 className="h-3 w-3" /> Evaluated
              </span>
            )}
            <span className="text-[10px] text-slate-400 font-mono">
              {formatDate(message.timestamp || message.created_at)}
            </span>
          </div>
        </div>

        {/* Error notice if present */}
        {message.error && (
          <div className="p-3 mb-3 bg-rose-50 border border-rose-200 rounded-md text-xs text-rose-700 flex items-start gap-2">
            <AlertCircle className="h-4 w-4 shrink-0 text-rose-600 mt-0.5" />
            <div>
              <p className="font-semibold">Analysis Warning / Error</p>
              <p className="text-[11px] mt-0.5">{message.error}</p>
            </div>
          </div>
        )}

        {/* Main Text Content */}
        <div className="text-sm text-slate-800 leading-relaxed space-y-2 whitespace-pre-wrap">
          {message.answer || message.result_summary || message.content}
        </div>

        {/* SQL Viewer */}
        {sqlQuery && <SqlViewer sqlQuery={sqlQuery} />}

        {/* Chart Visualization if applicable */}
        {chartData.length > 1 && (
          <div className="my-4 p-4 border border-slate-200 rounded-md bg-slate-50/50">
            <SimpleBarChart data={chartData} title="Data Visualization" />
          </div>
        )}

        {/* Structured Results Table */}
        {tableRows.length > 0 && (
          <div className="my-3">
            <StructuredTable rows={tableRows} columns={tableCols} title="Extracted Data Records" />
          </div>
        )}

        {/* Document Citations */}
        {citations.length > 0 && (
          <div className="my-3 pt-3 border-t border-slate-100">
            <h4 className="text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">
              Source Citations & Evidentiary Chunks
            </h4>
            <div className="space-y-2">
              {citations.map((cGroup, gIdx) => {
                // cGroup may be { document_id, chunks: [...] } or flat citation
                if (cGroup.chunks && Array.isArray(cGroup.chunks)) {
                  return cGroup.chunks.map((chk, cIdx) => (
                    <CitationCard key={`${gIdx}-${cIdx}`} citation={chk} />
                  ));
                }
                return <CitationCard key={gIdx} citation={cGroup} />;
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
