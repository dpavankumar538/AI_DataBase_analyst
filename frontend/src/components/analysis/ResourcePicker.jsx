import { useState, useId } from 'react';
import { Database, FileSpreadsheet, FileText, ChevronDown, ChevronUp } from 'lucide-react';
import Badge from '../common/Badge';

export default function ResourcePicker({
  datasets = [],
  databases = [],
  documents = [],
  selectedDatasetIds = [],
  selectedDataSourceIds = [],
  selectedDocumentIds = [],
  onToggleDataset,
  onToggleDatabase,
  onToggleDocument,
  disabled = false,
}) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownId = useId();

  const totalSelected =
    selectedDatasetIds.length + selectedDataSourceIds.length + selectedDocumentIds.length;

  return (
    <div className="w-full relative">
      <div className="flex flex-wrap items-center justify-between gap-2 p-3 bg-white border border-slate-200 rounded-lg shadow-2xs">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Selected Sources:
          </span>

          {totalSelected === 0 ? (
            <span className="text-xs text-slate-400 italic">
              No sources selected (AI will respond using general knowledge)
            </span>
          ) : (
            <div className="flex flex-wrap gap-1.5">
              {selectedDatasetIds.map((id) => {
                const item = datasets.find((d) => d.id === id);
                return (
                  <Badge key={`ds-${id}`} variant="info" size="sm" className="gap-1">
                    <FileSpreadsheet className="h-3 w-3" />
                    {item ? item.dataset_name : `Dataset #${id}`}
                  </Badge>
                );
              })}
              {selectedDataSourceIds.map((id) => {
                const item = databases.find((d) => d.id === id);
                return (
                  <Badge key={`db-${id}`} variant="purple" size="sm" className="gap-1">
                    <Database className="h-3 w-3" />
                    {item ? item.source_name : `DB #${id}`}
                  </Badge>
                );
              })}
              {selectedDocumentIds.map((id) => {
                const item = documents.find((d) => d.id === id);
                return (
                  <Badge key={`doc-${id}`} variant="warning" size="sm" className="gap-1">
                    <FileText className="h-3 w-3" />
                    {item ? item.filename : `Doc #${id}`}
                  </Badge>
                );
              })}
            </div>
          )}
        </div>

        <button
          type="button"
          onClick={() => setIsOpen((prev) => !prev)}
          disabled={disabled}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-md transition-colors"
        >
          <span>Choose Sources ({totalSelected})</span>
          {isOpen ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
        </button>
      </div>

      {isOpen && (
        <div className="mt-2 p-4 bg-white border border-slate-200 rounded-lg shadow-lg grid grid-cols-1 md:grid-cols-3 gap-4 z-20">
          {/* Datasets Column */}
          <div className="space-y-2 border-b md:border-b-0 md:border-r border-slate-100 pb-3 md:pb-0 md:pr-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
                <FileSpreadsheet className="h-3.5 w-3.5 text-blue-600" />
                Datasets ({datasets.length})
              </span>
            </div>
            {datasets.length === 0 ? (
              <p className="text-[11px] text-slate-400 py-2">No datasets uploaded yet.</p>
            ) : (
              <div className="max-h-48 overflow-y-auto space-y-1.5 pr-1">
                {datasets.map((ds) => {
                  const isChecked = selectedDatasetIds.includes(ds.id);
                  const inputId = `${dropdownId}-ds-${ds.id}`;
                  return (
                    <label
                      key={ds.id}
                      htmlFor={inputId}
                      className={`flex items-center justify-between p-2 rounded text-xs cursor-pointer border transition-colors ${
                        isChecked
                          ? 'bg-blue-50/70 border-blue-200 text-blue-900'
                          : 'hover:bg-slate-50 border-transparent text-slate-700'
                      }`}
                    >
                      <div className="truncate pr-2">
                        <span className="font-medium truncate block">{ds.dataset_name}</span>
                        <span className="text-[10px] text-slate-500">
                          {ds.row_count ? `${ds.row_count} rows` : ''} {ds.column_count ? `• ${ds.column_count} cols` : ''}
                        </span>
                      </div>
                      <input
                        id={inputId}
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => onToggleDataset(ds.id)}
                        className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 h-3.5 w-3.5"
                      />
                    </label>
                  );
                })}
              </div>
            )}
          </div>

          {/* External Databases Column */}
          <div className="space-y-2 border-b md:border-b-0 md:border-r border-slate-100 pb-3 md:pb-0 md:pr-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
                <Database className="h-3.5 w-3.5 text-purple-600" />
                Databases ({databases.length})
              </span>
            </div>
            {databases.length === 0 ? (
              <p className="text-[11px] text-slate-400 py-2">No databases connected yet.</p>
            ) : (
              <div className="max-h-48 overflow-y-auto space-y-1.5 pr-1">
                {databases.map((db) => {
                  const isChecked = selectedDataSourceIds.includes(db.id);
                  const isConnected = db.connection_status === 'connected';
                  const inputId = `${dropdownId}-db-${db.id}`;
                  return (
                    <label
                      key={db.id}
                      htmlFor={inputId}
                      className={`flex items-center justify-between p-2 rounded text-xs cursor-pointer border transition-colors ${
                        !isConnected ? 'opacity-50 cursor-not-allowed' : ''
                      } ${
                        isChecked
                          ? 'bg-purple-50/70 border-purple-200 text-purple-900'
                          : 'hover:bg-slate-50 border-transparent text-slate-700'
                      }`}
                    >
                      <div className="truncate pr-2">
                        <span className="font-medium truncate block">{db.source_name}</span>
                        <span className="text-[10px] uppercase text-slate-500">
                          {db.source_type} {db.connection_status ? `(${db.connection_status})` : ''}
                        </span>
                      </div>
                      <input
                        id={inputId}
                        type="checkbox"
                        disabled={!isConnected}
                        checked={isChecked}
                        onChange={() => onToggleDatabase(db.id)}
                        className="rounded border-slate-300 text-purple-600 focus:ring-purple-500 h-3.5 w-3.5"
                      />
                    </label>
                  );
                })}
              </div>
            )}
          </div>

          {/* Documents Column */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
                <FileText className="h-3.5 w-3.5 text-amber-600" />
                Documents ({documents.length})
              </span>
            </div>
            {documents.length === 0 ? (
              <p className="text-[11px] text-slate-400 py-2">No PDF documents uploaded yet.</p>
            ) : (
              <div className="max-h-48 overflow-y-auto space-y-1.5 pr-1">
                {documents.map((doc) => {
                  const isChecked = selectedDocumentIds.includes(doc.id);
                  const isReady = doc.processing_status === 'completed';
                  const inputId = `${dropdownId}-doc-${doc.id}`;
                  return (
                    <label
                      key={doc.id}
                      htmlFor={inputId}
                      className={`flex items-center justify-between p-2 rounded text-xs cursor-pointer border transition-colors ${
                        !isReady ? 'opacity-50 cursor-not-allowed' : ''
                      } ${
                        isChecked
                          ? 'bg-amber-50/70 border-amber-200 text-amber-900'
                          : 'hover:bg-slate-50 border-transparent text-slate-700'
                      }`}
                    >
                      <div className="truncate pr-2">
                        <span className="font-medium truncate block">{doc.filename}</span>
                        <span className="text-[10px] text-slate-500">
                          {doc.page_count ? `${doc.page_count} pages` : doc.processing_status}
                        </span>
                      </div>
                      <input
                        id={inputId}
                        type="checkbox"
                        disabled={!isReady}
                        checked={isChecked}
                        onChange={() => onToggleDocument(doc.id)}
                        className="rounded border-slate-300 text-amber-600 focus:ring-amber-500 h-3.5 w-3.5"
                      />
                    </label>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
