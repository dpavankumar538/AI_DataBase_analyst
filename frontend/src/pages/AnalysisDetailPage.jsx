import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Clock,
  CheckCircle2,
  AlertCircle,
  FileSpreadsheet,
  Database,
  FileText,
  Copy,
  Check,
  ExternalLink,
} from 'lucide-react';
import { analysisApi } from '../api/analysis';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import SqlViewer from '../components/analysis/SqlViewer';
import StructuredTable from '../components/analysis/StructuredTable';
import CitationCard from '../components/analysis/CitationCard';
import SimpleBarChart from '../components/charts/SimpleBarChart';
import { SkeletonCard } from '../components/common/LoadingSpinner';
import { formatDate, formatRelativeTime } from '../utils/formatters';
import { getRouteLabel } from '../utils/helpers';

export default function AnalysisDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [analysis, setAnalysis] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copiedAnswer, setCopiedAnswer] = useState(false);

  useEffect(() => {
    async function fetchDetail() {
      if (!id) return;
      setIsLoading(true);
      setError(null);
      try {
        const data = await analysisApi.getDetail(id);
        setAnalysis(data);
      } catch (err) {
        setError(err.message || 'Unable to retrieve analysis details.');
      } finally {
        setIsLoading(false);
      }
    }
    fetchDetail();
  }, [id]);

  const handleCopyAnswer = () => {
    if (!analysis?.result_summary) return;
    navigator.clipboard.writeText(analysis.result_summary);
    setCopiedAnswer(true);
    setTimeout(() => setCopiedAnswer(false), 2000);
  };

  const handleOpenInAnalyst = () => {
    if (!analysis) return;
    navigate('/analyst', {
      state: {
        initialQuestion: analysis.question,
        selectedDatasetIds: analysis.selected_resources?.dataset_ids || (analysis.dataset_id ? [analysis.dataset_id] : []),
        selectedDataSourceIds: analysis.selected_resources?.data_source_ids || [],
        selectedDocumentIds: analysis.selected_resources?.document_ids || [],
      },
    });
  };

  if (isLoading) {
    return (
      <div className="space-y-6 max-w-5xl mx-auto py-4">
        <div className="flex items-center gap-3">
          <div className="h-8 w-24 bg-slate-200 rounded animate-pulse" />
        </div>
        <SkeletonCard />
        <SkeletonCard />
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="max-w-2xl mx-auto py-12 text-center">
        <div className="p-3 bg-rose-50 text-rose-600 rounded-full inline-flex mb-3 border border-rose-100">
          <AlertCircle className="h-6 w-6" />
        </div>
        <h3 className="text-base font-bold text-slate-800">Analysis Not Found</h3>
        <p className="text-xs text-slate-500 mt-1 mb-6">
          {error || 'The requested analysis record does not exist or has been removed.'}
        </p>
        <Button variant="outline" size="sm" icon={ArrowLeft} onClick={() => navigate('/history')}>
          Back to Analysis History
        </Button>
      </div>
    );
  }

  const { label: routeLabel, color: routeColor } = getRouteLabel(analysis.route);
  const isVerified =
    analysis.evaluation_result === 'passed' || analysis.evaluation_result === 'acceptable';

  // Extract tabular rows if present
  let tableRows = [];
  let tableCols = [];
  let chartData = [];
  let extractedSql = analysis.generated_query;

  if (analysis.structured_result && typeof analysis.structured_result === 'object') {
    const datasets = analysis.structured_result.datasets || [];
    for (const ds of datasets) {
      if (ds.sql_query && !extractedSql) extractedSql = ds.sql_query;
      if (ds.generated_sql && !extractedSql) extractedSql = ds.generated_sql;

      if (ds.result && Array.isArray(ds.result)) {
        tableRows = ds.result;
      } else if (ds.overview?.columns) {
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

  // Extract chart data if numerical
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

  // Citations
  const citations = analysis.document_citations || [];

  // Selected Resources breakdown
  const resources = analysis.selected_resources || {};
  const datasetIds = resources.dataset_ids || (analysis.dataset_id ? [analysis.dataset_id] : []);
  const dataSourceIds = resources.data_source_ids || [];
  const documentIds = resources.document_ids || [];

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-12">
      {/* Top Navigation & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <Link
          to="/history"
          className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-500 hover:text-slate-800 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Analysis History</span>
        </Link>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            icon={copiedAnswer ? Check : Copy}
            onClick={handleCopyAnswer}
          >
            {copiedAnswer ? 'Copied Answer' : 'Copy Answer'}
          </Button>
          <Button
            variant="primary"
            size="sm"
            icon={ExternalLink}
            onClick={handleOpenInAnalyst}
          >
            Open in AI Analyst
          </Button>
        </div>
      </div>

      {/* Main Analysis Card */}
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-xs">
        {/* Route & Provenance Header */}
        <div className="flex flex-wrap items-center justify-between gap-2 pb-4 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <Badge
              variant={
                routeColor === 'blue'
                  ? 'info'
                  : routeColor === 'purple'
                  ? 'purple'
                  : 'neutral'
              }
              size="md"
            >
              {routeLabel}
            </Badge>

            {isVerified && (
              <span className="text-xs text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded border border-emerald-200 inline-flex items-center gap-1 font-semibold">
                <CheckCircle2 className="h-3.5 w-3.5" /> Quality Evaluated
              </span>
            )}

            {analysis.error && (
              <span className="text-xs text-rose-700 bg-rose-50 px-2.5 py-0.5 rounded border border-rose-200 inline-flex items-center gap-1 font-semibold">
                <AlertCircle className="h-3.5 w-3.5" /> Warning
              </span>
            )}
          </div>

          <div className="text-xs text-slate-400 font-mono flex items-center gap-1.5">
            <Clock className="h-3.5 w-3.5" />
            <span>{formatDate(analysis.created_at)}</span>
            <span>({formatRelativeTime(analysis.created_at)})</span>
          </div>
        </div>

        {/* Inquired Question */}
        <div className="py-5 border-b border-slate-100">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-1">
            Inquired Prompt
          </span>
          <h2 className="text-base font-bold text-slate-900 leading-snug">
            {analysis.question}
          </h2>
        </div>

        {/* Selected Provenance Sources */}
        <div className="py-4 border-b border-slate-100 bg-slate-50/50 -mx-6 px-6">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 block mb-2">
            Connected Knowledge Sources Used
          </span>
          <div className="flex flex-wrap items-center gap-2 text-xs">
            {datasetIds.length > 0 && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-blue-50 border border-blue-200 text-blue-700 font-medium">
                <FileSpreadsheet className="h-3.5 w-3.5 text-blue-600" />
                {datasetIds.length} Dataset{datasetIds.length > 1 ? 's' : ''} (ID: {datasetIds.join(', ')})
              </span>
            )}
            {dataSourceIds.length > 0 && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-indigo-50 border border-indigo-200 text-indigo-700 font-medium">
                <Database className="h-3.5 w-3.5 text-indigo-600" />
                {dataSourceIds.length} Database{dataSourceIds.length > 1 ? 's' : ''} (ID: {dataSourceIds.join(', ')})
              </span>
            )}
            {documentIds.length > 0 && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-amber-50 border border-amber-200 text-amber-700 font-medium">
                <FileText className="h-3.5 w-3.5 text-amber-600" />
                {documentIds.length} Document{documentIds.length > 1 ? 's' : ''} (ID: {documentIds.join(', ')})
              </span>
            )}
            {datasetIds.length === 0 && dataSourceIds.length === 0 && documentIds.length === 0 && (
              <span className="text-slate-400 italic">No explicit resource IDs attached (General domain inference)</span>
            )}
          </div>
        </div>

        {/* Synthesized Answer */}
        <div className="pt-5">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-2">
            AI Synthesis & Answer
          </span>
          <div className="text-sm text-slate-800 leading-relaxed space-y-3 whitespace-pre-wrap font-sans">
            {analysis.result_summary || 'No answer content recorded.'}
          </div>
        </div>

        {/* Error message banner if present */}
        {analysis.error && (
          <div className="mt-4 p-3.5 bg-rose-50 border border-rose-200 rounded-md text-xs text-rose-700 flex items-start gap-2">
            <AlertCircle className="h-4 w-4 shrink-0 text-rose-600 mt-0.5" />
            <div>
              <p className="font-semibold">Analysis Warning / Execution Notice</p>
              <p className="text-[11px] mt-0.5">{analysis.error}</p>
            </div>
          </div>
        )}
      </div>

      {/* Generated SQL Section (if any) */}
      {extractedSql && (
        <Card title="Generated Read-Only SQL Query" subtitle="Exact query evaluated against the data engine">
          <SqlViewer sqlQuery={extractedSql} />
        </Card>
      )}

      {/* Structured Results & Chart Section */}
      {tableRows.length > 0 && (
        <Card title="Structured Data Output" subtitle={`Returned ${tableRows.length} rows`}>
          {chartData.length > 1 && (
            <div className="mb-4 p-4 border border-slate-200 rounded-md bg-slate-50/50">
              <SimpleBarChart data={chartData} title="Data Distribution" />
            </div>
          )}
          <StructuredTable rows={tableRows} columns={tableCols} />
        </Card>
      )}

      {/* Evidentiary Citations (if any) */}
      {citations.length > 0 && (
        <Card
          title="Document Citations & Evidence"
          subtitle="Specific text and table chunks retrieved from indexed PDFs"
        >
          <div className="space-y-3">
            {citations.map((cGroup, gIdx) => {
              if (cGroup.chunks && Array.isArray(cGroup.chunks)) {
                return cGroup.chunks.map((chk, cIdx) => (
                  <CitationCard key={`${gIdx}-${cIdx}`} citation={chk} />
                ));
              }
              return <CitationCard key={gIdx} citation={cGroup} />;
            })}
          </div>
        </Card>
      )}
    </div>
  );
}
