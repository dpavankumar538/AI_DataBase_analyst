import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Sparkles,
  FileSpreadsheet,
  Database,
  FileText,
  History,
  ArrowRight,
  Plus,
  Clock,
  CheckCircle2,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { datasetsApi } from '../api/datasets';
import { databasesApi } from '../api/databases';
import { documentsApi } from '../api/documents';
import { analysisApi } from '../api/analysis';
import MetricTrend from '../components/charts/MetricTrend';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import EmptyState from '../components/common/EmptyState';
import { SkeletonCard } from '../components/common/LoadingSpinner';
import { formatRelativeTime } from '../utils/formatters';
import { getRouteLabel } from '../utils/helpers';

export default function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [isLoading, setIsLoading] = useState(true);
  const [metrics, setMetrics] = useState({
    datasetsCount: 0,
    databasesCount: 0,
    documentsCount: 0,
    analysesCount: 0,
  });
  const [recentDatasets, setRecentDatasets] = useState([]);
  const [recentAnalyses, setRecentAnalyses] = useState([]);
  const [quickQuestion, setQuickQuestion] = useState('');

  useEffect(() => {
    let isMounted = true;

    async function loadDashboardData() {
      setIsLoading(true);
      try {
        const [dsRes, dbRes, docRes, anRes] = await Promise.allSettled([
          datasetsApi.list(),
          databasesApi.list(),
          documentsApi.list(),
          analysisApi.list(5, 0),
        ]);

        if (!isMounted) return;

        const datasets = dsRes.status === 'fulfilled' ? dsRes.value || [] : [];
        const databases = dbRes.status === 'fulfilled' ? dbRes.value || [] : [];
        const documents = docRes.status === 'fulfilled' ? docRes.value || [] : [];
        const analyses = anRes.status === 'fulfilled' ? anRes.value || [] : [];

        setMetrics({
          datasetsCount: datasets.length,
          databasesCount: databases.length,
          documentsCount: documents.length,
          analysesCount: analyses.length,
        });

        setRecentDatasets(datasets.slice(0, 4));
        setRecentAnalyses(analyses.slice(0, 4));
      } catch (err) {
        console.error('Failed to load dashboard metrics:', err);
      } finally {
        if (isMounted) setIsLoading(false);
      }
    }

    loadDashboardData();
    return () => {
      isMounted = false;
    };
  }, []);

  const handleQuickAnalyze = (e) => {
    e.preventDefault();
    if (!quickQuestion.trim()) return;
    navigate('/analyst', { state: { initialQuestion: quickQuestion } });
  };

  return (
    <div className="space-y-6">
      {/* Welcome & Overview Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-slate-900">
            Welcome back, {user?.name || 'Analyst'}
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Synthesize insights from MySQL, PostgreSQL, CSV/Excel datasets, and PDF knowledge bases.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            icon={Plus}
            onClick={() => navigate('/datasets')}
          >
            Upload Data
          </Button>
          <Button
            size="sm"
            variant="primary"
            icon={Sparkles}
            onClick={() => navigate('/analyst')}
          >
            New Analysis
          </Button>
        </div>
      </div>

      {/* Prominent AI Analyst Entry Point */}
      <div className="relative overflow-hidden rounded-xl border border-blue-200 bg-linear-to-r from-blue-600 to-indigo-700 p-6 text-white shadow-sm">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-blue-500/40 border border-blue-400/40 text-[11px] font-semibold text-blue-100 mb-3">
            <Sparkles className="h-3.5 w-3.5 text-blue-200" />
            AI Multimodal Data Engine
          </div>
          <h3 className="text-lg font-bold">Ask anything about your connected data</h3>
          <p className="text-xs text-blue-100 mt-1 mb-4 leading-relaxed">
            AI Data Analysis automatically routes your question to SQL generation, vector document retrieval, or hybrid multi-source reasoning.
          </p>

          <form onSubmit={handleQuickAnalyze} className="flex gap-2">
            <input
              type="text"
              placeholder="e.g., What was the total sales volume across all regions in Q3?"
              value={quickQuestion}
              onChange={(e) => setQuickQuestion(e.target.value)}
              className="flex-1 rounded-md bg-white text-slate-900 placeholder:text-slate-400 px-3.5 py-2 text-xs focus:outline-none focus:ring-2 focus:ring-blue-300 shadow-2xs"
            />
            <Button
              type="submit"
              variant="secondary"
              size="md"
              className="bg-white text-blue-700 hover:bg-blue-50 font-semibold"
            >
              Analyze
            </Button>
          </form>
        </div>
      </div>

      {/* Key Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {isLoading ? (
          <>
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </>
        ) : (
          <>
            <MetricTrend
              label="Tabular Datasets"
              value={metrics.datasetsCount}
              subtitle="CSV, XLSX, and JSON files"
              icon={FileSpreadsheet}
            />
            <MetricTrend
              label="Connected Databases"
              value={metrics.databasesCount}
              subtitle="External MySQL and PostgreSQL"
              icon={Database}
            />
            <MetricTrend
              label="Ingested Documents"
              value={metrics.documentsCount}
              subtitle="Vectorized PDF manuals & reports"
              icon={FileText}
            />
            <MetricTrend
              label="Total Analyses"
              value={metrics.analysesCount}
              subtitle="Saved historical queries & reports"
              icon={History}
            />
          </>
        )}
      </div>

      {/* Two Column Grid: Recent Analyses & Datasets */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Analyses (2 cols on large screen) */}
        <div className="lg:col-span-2">
          <Card
            title="Recent Analyses"
            subtitle="Recent questions answered by AI Data Analysis"
            actions={
              <Link
                to="/history"
                className="text-xs font-medium text-blue-600 hover:text-blue-700 flex items-center gap-1"
              >
                View all <ArrowRight className="h-3 w-3" />
              </Link>
            }
          >
            {recentAnalyses.length === 0 ? (
              <EmptyState
                icon={History}
                title="No analyses conducted yet"
                description="Ask your first data analysis question in the AI Analyst workspace."
                actionText="Go to AI Analyst"
                onAction={() => navigate('/analyst')}
              />
            ) : (
              <div className="divide-y divide-slate-100">
                {recentAnalyses.map((analysis) => {
                  const { label: routeLabel, color: routeColor } = getRouteLabel(analysis.route);
                  return (
                    <div
                      key={analysis.id}
                      onClick={() => navigate('/history', { state: { openAnalysisId: analysis.id } })}
                      className="py-3 px-2 -mx-2 flex flex-col sm:flex-row sm:items-center justify-between gap-2 hover:bg-slate-50/80 rounded-md transition-colors cursor-pointer"
                    >
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2 mb-1">
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
                          {analysis.evaluation_result === 'passed' && (
                            <span className="text-[11px] text-emerald-600 flex items-center gap-1">
                              <CheckCircle2 className="h-3 w-3" /> Verified
                            </span>
                          )}
                        </div>
                        <p className="text-xs font-semibold text-slate-800 truncate">
                          {analysis.question}
                        </p>
                        {analysis.result_summary && (
                          <p className="text-[11px] text-slate-500 truncate mt-0.5">
                            {analysis.result_summary}
                          </p>
                        )}
                      </div>

                      <div className="text-[11px] text-slate-400 font-mono shrink-0 flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatRelativeTime(analysis.created_at)}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </Card>
        </div>

        {/* Recent Datasets (1 col on large screen) */}
        <div>
          <Card
            title="Uploaded Datasets"
            subtitle="Available structured tables"
            actions={
              <Link
                to="/datasets"
                className="text-xs font-medium text-blue-600 hover:text-blue-700 flex items-center gap-1"
              >
                Manage <ArrowRight className="h-3 w-3" />
              </Link>
            }
          >
            {recentDatasets.length === 0 ? (
              <EmptyState
                icon={FileSpreadsheet}
                title="No datasets available"
                description="Upload CSV, XLSX or JSON files to begin tabular querying."
                actionText="Upload Dataset"
                onAction={() => navigate('/datasets')}
              />
            ) : (
              <div className="divide-y divide-slate-100">
                {recentDatasets.map((dataset) => (
                  <div
                    key={dataset.id}
                    onClick={() => navigate('/datasets')}
                    className="py-2.5 px-2 -mx-2 flex items-center justify-between hover:bg-slate-50 rounded-md transition-colors cursor-pointer"
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className="p-1.5 rounded bg-blue-50 text-blue-600 shrink-0">
                        <FileSpreadsheet className="h-4 w-4" />
                      </div>
                      <div className="truncate">
                        <p className="text-xs font-medium text-slate-800 truncate">
                          {dataset.dataset_name}
                        </p>
                        <p className="text-[10px] text-slate-400">
                          {dataset.row_count ? `${dataset.row_count} rows` : ''}{' '}
                          {dataset.column_count ? `• ${dataset.column_count} cols` : ''}
                        </p>
                      </div>
                    </div>

                    <span className="text-[10px] text-slate-400 font-mono shrink-0">
                      {formatRelativeTime(dataset.created_at)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
