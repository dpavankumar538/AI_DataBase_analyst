import { useState, useEffect, useRef } from 'react';
import {
  FileText,
  Upload,
  Trash2,
  Eye,
  AlertCircle,
  CheckCircle2,
  FileCheck,
} from 'lucide-react';
import { documentsApi } from '../api/documents';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import Modal from '../components/common/Modal';
import ConfirmDialog from '../components/common/ConfirmDialog';
import EmptyState from '../components/common/EmptyState';
import { LoadingSpinner, SkeletonRow } from '../components/common/LoadingSpinner';
import { formatDate } from '../utils/formatters';
import { getStatusBadge } from '../utils/helpers';

export default function DocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(null);

  // Upload state
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const fileInputRef = useRef(null);

  // Details Modal state
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [docDetails, setDocDetails] = useState(null);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);

  // Delete modal state
  const [docToDelete, setDocToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const fetchDocuments = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await documentsApi.list();
      setDocuments(data || []);
    } catch (err) {
      setError(err.message || 'Failed to load documents.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Reset input
    e.target.value = '';

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setUploadError('Only PDF files (.pdf) are supported.');
      return;
    }

    if (file.size > 16 * 1024 * 1024) {
      setUploadError('PDF file exceeds the 16 MB size limit.');
      return;
    }

    setIsUploading(true);
    setUploadError(null);
    setUploadSuccess(null);

    try {
      const res = await documentsApi.upload(file);
      setUploadSuccess(
        `"${res.filename}" uploaded & vectorized successfully (${res.page_count} pages, ${res.chunk_count} chunks).`
      );
      await fetchDocuments();
    } catch (err) {
      setUploadError(err.message || 'Unable to process PDF. Check that it is a valid PDF document.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleViewDetails = async (doc) => {
    setSelectedDoc(doc);
    setIsDetailsModalOpen(true);
    setIsLoadingDetails(true);
    setDocDetails(null);

    try {
      const res = await documentsApi.getDetails(doc.id);
      setDocDetails(res);
    } catch (err) {
      console.error('Failed to load document details:', err);
    } finally {
      setIsLoadingDetails(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!docToDelete) return;
    setIsDeleting(true);
    try {
      await documentsApi.delete(docToDelete.id);
      setDocToDelete(null);
      setUploadSuccess(`Document "${docToDelete.filename}" and its vector embeddings deleted.`);
      await fetchDocuments();
    } catch (err) {
      setError(err.message || 'Unable to delete document.');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-slate-900">
            Document Knowledge Base
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Ingest technical manuals, financial reports, and policy PDFs with text & table chunking.
          </p>
        </div>

        <div>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".pdf,application/pdf"
            className="hidden"
          />
          <Button
            variant="primary"
            size="sm"
            icon={Upload}
            onClick={() => fileInputRef.current?.click()}
            isLoading={isUploading}
          >
            Upload PDF Document
          </Button>
        </div>
      </div>

      {/* Upload Alerts */}
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

      {/* Documents List Card */}
      <Card
        title={`All Documents (${documents.length})`}
        subtitle="PDFs indexed in ChromaDB for similarity search and contextual citations"
      >
        {isLoading ? (
          <div className="py-8">
            <SkeletonRow cols={5} rows={3} />
          </div>
        ) : error ? (
          <div className="p-4 bg-rose-50 border border-rose-200 rounded text-xs text-rose-700">
            {error}
          </div>
        ) : documents.length === 0 ? (
          <EmptyState
            icon={FileText}
            title="No documents uploaded yet"
            description="Upload PDF documents to enable vector similarity retrieval with page-level citations."
            actionText="Upload PDF"
            onAction={() => fileInputRef.current?.click()}
          />
        ) : (
          <div className="overflow-x-auto -mx-5 -mb-5">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-600">
                  <th className="px-5 py-3">Document Name</th>
                  <th className="px-5 py-3">Page Count</th>
                  <th className="px-5 py-3">Processing Status</th>
                  <th className="px-5 py-3">Uploaded Date</th>
                  <th className="px-5 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs">
                {documents.map((doc) => {
                  const status = getStatusBadge(doc.processing_status);

                  return (
                    <tr key={doc.id} className="hover:bg-slate-50/70 transition-colors">
                      <td className="px-5 py-3.5 font-medium text-slate-800">
                        <div className="flex items-center gap-2.5">
                          <div className="p-1.5 rounded bg-amber-50 text-amber-600 shrink-0">
                            <FileText className="h-4 w-4" />
                          </div>
                          <span className="truncate max-w-xs">{doc.filename}</span>
                        </div>
                      </td>

                      <td className="px-5 py-3.5 text-slate-600 font-mono">
                        {doc.page_count ? `${doc.page_count} pages` : '—'}
                      </td>

                      <td className="px-5 py-3.5">
                        <Badge
                          variant={
                            status.type === 'success'
                              ? 'success'
                              : status.type === 'error'
                              ? 'error'
                              : 'warning'
                          }
                          size="sm"
                        >
                          {status.label}
                        </Badge>
                      </td>

                      <td className="px-5 py-3.5 text-slate-500 font-mono">
                        {formatDate(doc.created_at)}
                      </td>

                      <td className="px-5 py-3.5 text-right whitespace-nowrap">
                        <div className="flex items-center justify-end gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            icon={Eye}
                            onClick={() => handleViewDetails(doc)}
                          >
                            Details
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-rose-600 hover:text-rose-700 hover:bg-rose-50"
                            icon={Trash2}
                            onClick={() => setDocToDelete(doc)}
                          />
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Details Modal */}
      <Modal
        isOpen={isDetailsModalOpen}
        onClose={() => setIsDetailsModalOpen(false)}
        title={selectedDoc ? selectedDoc.filename : 'Document Details'}
        subtitle="Document metadata, page structure, and vector index health"
        maxWidth="max-w-md"
      >
        {isLoadingDetails ? (
          <div className="py-8 flex flex-col items-center justify-center gap-2">
            <LoadingSpinner size="sm" />
            <span className="text-xs text-slate-500">Loading document metadata...</span>
          </div>
        ) : !docDetails ? (
          <p className="text-xs text-slate-500 py-4 text-center">Unable to load document details.</p>
        ) : (
          <div className="space-y-4 text-xs">
            <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-md border border-slate-200">
              <div className="p-2 rounded bg-amber-100 text-amber-700">
                <FileCheck className="h-5 w-5" />
              </div>
              <div className="truncate">
                <p className="font-semibold text-slate-800 truncate">{docDetails.filename}</p>
                <p className="text-[11px] text-slate-500 font-mono">Document #{docDetails.id}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-white rounded border border-slate-200">
                <span className="text-[10px] uppercase font-semibold text-slate-400 block">Total Pages</span>
                <span className="text-sm font-bold text-slate-800">
                  {docDetails.page_count || 1}
                </span>
              </div>
              <div className="p-3 bg-white rounded border border-slate-200">
                <span className="text-[10px] uppercase font-semibold text-slate-400 block">Vector Status</span>
                <span className="text-sm font-bold text-emerald-600 capitalize">
                  {docDetails.processing_status}
                </span>
              </div>
            </div>

            <div className="p-3 bg-slate-50 rounded border border-slate-200 space-y-1.5 font-mono text-[11px]">
              <div className="flex justify-between">
                <span className="text-slate-500">Created:</span>
                <span className="text-slate-800">{formatDate(docDetails.created_at)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Vector Store:</span>
                <span className="text-slate-800">ChromaDB Cosine Space</span>
              </div>
            </div>
          </div>
        )}
      </Modal>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={Boolean(docToDelete)}
        onClose={() => setDocToDelete(null)}
        onConfirm={handleDeleteConfirm}
        title="Delete Document"
        message={`Are you sure you want to delete "${docToDelete?.filename}"? This will permanently delete the physical PDF and all associated vector embeddings from ChromaDB.`}
        confirmText="Delete Document"
        isLoading={isDeleting}
      />
    </div>
  );
}
