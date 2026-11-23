import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  History,
  Search,
  Filter,
  Sparkles,
  RefreshCw,
  Clock,
  CheckCircle2,
  AlertCircle,
  FileSpreadsheet,
  Database,
  FileText,
  ChevronRight,
  ExternalLink,
} from 'lucide-react';
import { analysisApi } from '../api/analysis';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import EmptyState from '../components/common/EmptyState';
import { SkeletonRow } from '../components/common/LoadingSpinner';
import { formatDate, formatRelativeTime } from '../utils/formatters';
import { getRouteLabel } from '../utils/helpers';

export default function HistoryPage() {
  const navigate = useNavigate();

  const [analyses, setAnalyses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [routeFilter, setRouteFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');

  const fetchAnalyses = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await analysisApi.list(100, 0);
      setAnalyses(data || []);
    } catch (err) {
      setError(err.message || 'Failed to load analysis history.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalyses();
  }, []);

  // Filter analyses
  const filteredAnalyses = analyses.filter((item) => {
    // Search query filter
    const matchesSearch =
      !searchQuery.trim() ||
      item.question?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.result_summary?.toLowerCase().includes(searchQuery.toLowerCase());

    // Route filter
    const matchesRoute =
      routeFilter === 'all' ||
      item.route === routeFilter ||
      (routeFilter === 'document' && item.route === 'unstructured');

    // Status filter
    let matchesStatus = true;
    if (statusFilter === 'passed') {
      matchesStatus = item.evaluation_result === 'passed' || item.evaluation_result === 'acceptable';
    } else if (statusFilter === 'error') {
      matchesStatus = Boolean(item.error);
    }

    return matchesSearch && matchesRoute && matchesStatus;
  });

  const getResourceCounts = (item) => {
    const resources = item.selected_resources || {};
    const datasets = resources.dataset_ids?.length || (item.dataset_id ? 1 : 0);
    const databases = resources.data_source_ids?.length || 0;
    const documents = resources.document_ids?.length || 0;
    return { datasets, databases, documents, total: datasets + databases + documents };
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
            <History className="h-5 w-5 text-blue-600" />
            Analysis History
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Browse and inspect all historical AI queries, generated SQL execution, and document citations.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            icon={RefreshCw}
            onClick={fetchAnalyses}
            disabled={isLoading}
          >
            Refresh
          </Button>
          <Button
            variant="primary"
            size="sm"
            icon={Sparkles}
            onClick={() => navigate('/analyst')}
          >
            New Analysis
          </Button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs">
        {/* Search */}
        <div className="relative flex-1 min-w-[220px]">
          <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by question or result keywords..."
            className="w-full pl-9 pr-3 py-1.5 text-xs rounded-md border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Route Filter Dropdown */}
        <div className="flex items-center gap-2">
          <Filter className="h-3.5 w-3.5 text-slate-400 shrink-0" />
          <select
            value={routeFilter}
            onChange={(e) => setRouteFilter(e.target.value)}
            className="text-xs py-1.5 px-2.5 rounded-md border border-slate-300 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Routes</option>
            <option value="structured">Structured SQL</option>
            <option value="document">Document RAG</option>
            <option value="hybrid">Hybrid Analysis</option>
            <option value="general">General AI</option>
          </select>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-xs py-1.5 px-2.5 rounded-md border border-slate-300 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Evaluations</option>
            <option value="passed">Verified / Passed</option>
            <option value="error">Has Errors</option>
          </select>
        </div>
      </div>

      {/* Error alert */}
      {error && (
        <div className="p-3 bg-rose-50 border border-rose-200 rounded-md text-xs text-rose-700 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-rose-600" />
            <span>{error}</span>
          </div>
          <button
            type="button"
            onClick={() => setError(null)}
            className="text-rose-500 hover:text-rose-700 text-xs"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Analyses List Card */}
      <Card
        title={`Saved Analyses (${filteredAnalyses.length})`}
        subtitle="Chronological list of analytical inquiries and verification records"
      >
        {isLoading ? (
          <div className="py-6">
            <SkeletonRow cols={4} rows={5} />
          </div>
        ) : filteredAnalyses.length === 0 ? (
          searchQuery || routeFilter !== 'all' || statusFilter !== 'all' ? (
            <div className="text-center py-10 px-4">
              <History className="h-8 w-8 text-slate-300 mx-auto mb-2" />
              <p className="text-xs font-semibold text-slate-700">No matching analyses found</p>
              <p className="text-[11px] text-slate-500 mt-1 mb-4">
                Try adjusting your search query or route filters.
              </p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setSearchQuery('');
                  setRouteFilter('all');
                  setStatusFilter('all');
                }}
              >
                Clear Filters
              </Button>
            </div>
          ) : (
            <EmptyState
              icon={History}
              title="No analyses recorded yet"
              description="Start a data analysis session in the AI Analyst workspace to build your history."
              actionText="Open AI Analyst"
              onAction={() => navigate('/analyst')}
            />
          )
        ) : (
          <div className="divide-y divide-slate-100 -mx-5 -mb-5">
            {filteredAnalyses.map((analysis) => {
              const { label: routeLabel, color: routeColor } = getRouteLabel(analysis.route);
              const resourceCounts = getResourceCounts(analysis);
              const isVerified =
                analysis.evaluation_result === 'passed' ||
                analysis.evaluation_result === 'acceptable';

              return (
                <div
                  key={analysis.id}
                  onClick={() => navigate(`/history/${analysis.id}`)}
                  className="p-4 hover:bg-slate-50/80 transition-colors cursor-pointer group flex flex-col md:flex-row md:items-center justify-between gap-3"
                >
                  {/* Left Column: Metadata & Question */}
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 mb-1.5">
                      <Badge
                        variant={
                          routeColor === 'blue'
                            ? 'info'
                            : routeColor === 'purple'
                            ? 'purple'
                            : 'neutral'
                        }
                        size="sm"
                      >
                        {routeLabel}
                      </Badge>

                      {isVerified && (
                        <span className="text-[11px] text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 inline-flex items-center gap-1 font-medium">
                          <CheckCircle2 className="h-3 w-3" /> Verified
                        </span>
                      )}

                      {analysis.error && (
                        <span className="text-[11px] text-rose-700 bg-rose-50 px-2 py-0.5 rounded border border-rose-200 inline-flex items-center gap-1 font-medium">
                          <AlertCircle className="h-3 w-3" /> Warning
                        </span>
                      )}

                      {/* Resource Pills */}
                      {resourceCounts.datasets > 0 && (
                        <span className="text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded flex items-center gap-1">
                          <FileSpreadsheet className="h-3 w-3 text-blue-600" />
                          {resourceCounts.datasets} dataset{resourceCounts.datasets > 1 ? 's' : ''}
                        </span>
                      )}
                      {resourceCounts.databases > 0 && (
                        <span className="text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded flex items-center gap-1">
                          <Database className="h-3 w-3 text-indigo-600" />
                          {resourceCounts.databases} database{resourceCounts.databases > 1 ? 's' : ''}
                        </span>
                      )}
                      {resourceCounts.documents > 0 && (
                        <span className="text-[10px] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded flex items-center gap-1">
                          <FileText className="h-3 w-3 text-amber-600" />
                          {resourceCounts.documents} doc{resourceCounts.documents > 1 ? 's' : ''}
                        </span>
                      )}
                    </div>

                    <h4 className="text-xs font-semibold text-slate-800 group-hover:text-blue-600 transition-colors line-clamp-1">
                      {analysis.question}
                    </h4>

                    {analysis.result_summary && (
                      <p className="text-[11px] text-slate-500 line-clamp-2 mt-1 leading-relaxed">
                        {analysis.result_summary}
                      </p>
                    )}
                  </div>

                  {/* Right Column: Timestamps & Navigation Actions */}
                  <div className="flex items-center justify-between md:justify-end gap-3 shrink-0 pt-2 md:pt-0 border-t md:border-t-0 border-slate-100">
                    <div className="text-right">
                      <div className="text-[11px] text-slate-400 font-mono flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatRelativeTime(analysis.created_at)}
                      </div>
                      <div className="text-[10px] text-slate-400 font-mono hidden sm:block">
                        {formatDate(analysis.created_at)}
                      </div>
                    </div>

                    <div className="flex items-center gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate('/analyst', {
                            state: {
                              initialQuestion: analysis.question,
                              selectedDatasetIds: analysis.selected_resources?.dataset_ids || (analysis.dataset_id ? [analysis.dataset_id] : []),
                              selectedDataSourceIds: analysis.selected_resources?.data_source_ids || [],
                              selectedDocumentIds: analysis.selected_resources?.document_ids || [],
                            },
                          });
                        }}
                        title="Re-run query in AI Analyst"
                        className="text-slate-400 hover:text-blue-600"
                      >
                        <ExternalLink className="h-3.5 w-3.5" />
                      </Button>

                      <div className="p-1 rounded-md text-slate-400 group-hover:text-blue-600 group-hover:translate-x-0.5 transition-all">
                        <ChevronRight className="h-4 w-4" />
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Card>
    </div>
  );
}
