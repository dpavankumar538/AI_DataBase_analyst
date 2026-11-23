import { useState, useEffect, useRef } from 'react';
import {
  FileSpreadsheet,
  Upload,
  Trash2,
  Eye,
  AlertCircle,
  CheckCircle2,
} from 'lucide-react';
import { datasetsApi } from '../api/datasets';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Modal from '../components/common/Modal';
import ConfirmDialog from '../components/common/ConfirmDialog';
import EmptyState from '../components/common/EmptyState';
import { LoadingSpinner, SkeletonRow } from '../components/common/LoadingSpinner';
import DistributionChart from '../components/charts/DistributionChart';
import { formatDate, formatBytes } from '../utils/formatters';

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(null);

  // Upload state
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const fileInputRef = useRef(null);

  // Schema & Analysis modal state
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const [isLoadingAnalysis, setIsLoadingAnalysis] = useState(false);
  const [isAnalysisModalOpen, setIsAnalysisModalOpen] = useState(false);

  // Delete modal state
  const [datasetToDelete, setDatasetToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const fetchDatasets = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await datasetsApi.list();
      setDatasets(data || []);
    } catch (err) {
      setError(err.message || 'Failed to load datasets.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Reset input
    e.target.value = '';

    const validExtensions = ['.csv', '.xlsx', '.json'];
    const hasValidExt = validExtensions.some((ext) => file.name.toLowerCase().endsWith(ext));

    if (!hasValidExt) {
      setUploadError('Unsupported file type. Please upload a CSV, XLSX, or JSON file.');
      return;
    }

    if (file.size > 16 * 1024 * 1024) {
      setUploadError('File exceeds the maximum limit of 16 MB.');
      return;
    }

    setIsUploading(true);
    setUploadError(null);
    setUploadSuccess(null);

    try {
      const res = await datasetsApi.upload(file);
      setUploadSuccess(`Successfully uploaded "${res.dataset_name}".`);
      await fetchDatasets();
    } catch (err) {
      setUploadError(err.message || 'Upload failed. Ensure the tabular file is not corrupted.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleViewAnalysis = async (dataset) => {
    setSelectedDataset(dataset);
    setIsAnalysisModalOpen(true);
    setIsLoadingAnalysis(true);
    setAnalysisData(null);

    try {
      const data = await datasetsApi.getAnalysis(dataset.id);
      setAnalysisData(data);
    } catch (err) {
      console.error('Failed to load dataset schema/analysis:', err);
    } finally {
      setIsLoadingAnalysis(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!datasetToDelete) return;
    setIsDeleting(true);
    try {
      await datasetsApi.delete(datasetToDelete.id);
      setDatasetToDelete(null);
      await fetchDatasets();
    } catch (err) {
      setError(err.message || 'Unable to delete dataset.');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-slate-900">Dataset Management</h2>
          <p className="text-xs text-slate-500 mt-1">
            Upload and explore CSV, Excel (.xlsx), and JSON tabular datasets.
          </p>
        </div>

        <div>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".csv,.xlsx,.json"
            className="hidden"
          />
          <Button
            variant="primary"
            size="sm"
            icon={Upload}
            onClick={() => fileInputRef.current?.click()}
            isLoading={isUploading}
          >
            Upload Dataset
          </Button>
        </div>
      </div>

      {/* Upload alerts */}
      {uploadSuccess && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-md text-xs text-emerald-700 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
            <span>{uploadSuccess}</span>
          </div>
          <button
            type="button"
            onClick={() => setUploadSuccess(null)}
            className="text-emerald-500 hover:text-emerald-700 text-xs"
          >
            Dismiss
          </button>
        </div>
      )}

      {uploadError && (
        <div className="p-3 bg-rose-50 border border-rose-200 rounded-md text-xs text-rose-700 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-rose-600" />
            <span>{uploadError}</span>
          </div>
          <button
            type="button"
            onClick={() => setUploadError(null)}
            className="text-rose-500 hover:text-rose-700 text-xs"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Datasets Table Card */}
      <Card
        title={`All Datasets (${datasets.length})`}
        subtitle="Manage ingested tabular tables and examine inferred schemas"
      >
        {isLoading ? (
          <div className="py-8">
            <SkeletonRow cols={5} rows={4} />
          </div>
        ) : error ? (
          <div className="p-4 bg-rose-50 border border-rose-200 rounded text-xs text-rose-700">
            {error}
          </div>
        ) : datasets.length === 0 ? (
          <EmptyState
            icon={FileSpreadsheet}
            title="No datasets uploaded yet"
            description="Upload your first CSV, XLSX, or JSON spreadsheet to run automated data profiling and queries."
            actionText="Upload Dataset"
            onAction={() => fileInputRef.current?.click()}
          />
        ) : (
          <div className="overflow-x-auto -mx-5 -mb-5">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-600">
                  <th className="px-5 py-3">Dataset Name</th>
                  <th className="px-5 py-3">Rows</th>
                  <th className="px-5 py-3">Columns</th>
                  <th className="px-5 py-3">Uploaded Date</th>
                  <th className="px-5 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs">
                {datasets.map((dataset) => (
                  <tr key={dataset.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="px-5 py-3.5 font-medium text-slate-800">
                      <div className="flex items-center gap-2.5">
                        <div className="p-1.5 rounded bg-blue-50 text-blue-600 shrink-0">
                          <FileSpreadsheet className="h-4 w-4" />
                        </div>
                        <span className="truncate max-w-xs">{dataset.dataset_name}</span>
                      </div>
                    </td>

                    <td className="px-5 py-3.5 text-slate-600 font-mono">
                      {dataset.row_count ? dataset.row_count.toLocaleString() : '—'}
                    </td>

                    <td className="px-5 py-3.5 text-slate-600 font-mono">
                      {dataset.column_count || '—'}
                    </td>

                    <td className="px-5 py-3.5 text-slate-500 font-mono">
                      {formatDate(dataset.created_at)}
                    </td>

                    <td className="px-5 py-3.5 text-right whitespace-nowrap">
                      <div className="flex items-center justify-end gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          icon={Eye}
                          onClick={() => handleViewAnalysis(dataset)}
                        >
                          Schema & Stats
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-rose-600 hover:text-rose-700 hover:bg-rose-50"
                          icon={Trash2}
                          onClick={() => setDatasetToDelete(dataset)}
                        />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Schema & Analysis Modal */}
      <Modal
        isOpen={isAnalysisModalOpen}
        onClose={() => setIsAnalysisModalOpen(false)}
        title={selectedDataset ? selectedDataset.dataset_name : 'Dataset Details'}
        subtitle="Inferred column types, missing values, and numerical summary statistics"
        maxWidth="max-w-3xl"
      >
        {isLoadingAnalysis ? (
          <div className="py-12 flex flex-col items-center justify-center gap-3">
            <LoadingSpinner size="md" />
            <span className="text-xs text-slate-500">Loading dataset overview and statistics...</span>
          </div>
        ) : !analysisData ? (
          <p className="text-xs text-slate-500 py-6 text-center">Unable to load dataset metadata.</p>
        ) : (
          <div className="space-y-6 text-xs">
            {/* Overview summary cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3 bg-slate-50 rounded-md border border-slate-200">
                <span className="text-[10px] uppercase font-semibold text-slate-400 block">Total Rows</span>
                <span className="text-base font-bold text-slate-800">
                  {analysisData.overview?.row_count?.toLocaleString()}
                </span>
              </div>
              <div className="p-3 bg-slate-50 rounded-md border border-slate-200">
                <span className="text-[10px] uppercase font-semibold text-slate-400 block">Total Columns</span>
                <span className="text-base font-bold text-slate-800">
                  {analysisData.overview?.column_count}
                </span>
              </div>
              <div className="p-3 bg-slate-50 rounded-md border border-slate-200">
                <span className="text-[10px] uppercase font-semibold text-slate-400 block">Memory Usage</span>
                <span className="text-base font-bold text-slate-800">
                  {formatBytes(analysisData.overview?.memory_usage_bytes)}
                </span>
              </div>
              <div className="p-3 bg-slate-50 rounded-md border border-slate-200">
                <span className="text-[10px] uppercase font-semibold text-slate-400 block">ID Reference</span>
                <span className="text-base font-bold text-slate-800 font-mono">
                  #{analysisData.dataset_id}
                </span>
              </div>
            </div>

            {/* Inferred Column Schema Table */}
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-700 mb-2">
                Column Schemas & Missing Values
              </h4>
              <div className="border border-slate-200 rounded-md overflow-hidden max-h-60 overflow-y-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead className="bg-slate-50 border-b border-slate-200 font-semibold text-slate-600 sticky top-0">
                    <tr>
                      <th className="px-3 py-2">Column Name</th>
                      <th className="px-3 py-2">Data Type</th>
                      <th className="px-3 py-2">Missing Values</th>
                      <th className="px-3 py-2">Unique Count</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-mono text-[11px]">
                    {(analysisData.overview?.columns || []).map((col, idx) => (
                      <tr key={idx} className="hover:bg-slate-50">
                        <td className="px-3 py-2 font-medium text-slate-800">{col.name}</td>
                        <td className="px-3 py-2 text-blue-600">{col.data_type}</td>
                        <td className="px-3 py-2 text-slate-600">{col.missing_values}</td>
                        <td className="px-3 py-2 text-slate-600">{col.unique_values}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Numerical Statistics Distributions */}
            {analysisData.statistics && Object.keys(analysisData.statistics).length > 0 && (
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-700 mb-2">
                  Numerical Distributions (IQR & Means)
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {Object.entries(analysisData.statistics).map(([colName, stats]) => (
                    <DistributionChart key={colName} title={colName} stats={stats} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={Boolean(datasetToDelete)}
        onClose={() => setDatasetToDelete(null)}
        onConfirm={handleDeleteConfirm}
        title="Delete Dataset"
        message={`Are you sure you want to delete "${datasetToDelete?.dataset_name}"? Any past analysis referencing this dataset will remain, but the physical file and future query references will be removed.`}
        confirmText="Delete Dataset"
        isLoading={isDeleting}
      />
    </div>
  );
}
