import { useState, useEffect } from 'react';
import {
  Database,
  Plus,
  PowerOff,
  Power,
  Trash2,
  Table,
  CheckCircle2,
  AlertCircle,
  Eye,
  ShieldCheck,
} from 'lucide-react';
import { databasesApi } from '../api/databases';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import Modal from '../components/common/Modal';
import ConfirmDialog from '../components/common/ConfirmDialog';
import EmptyState from '../components/common/EmptyState';
import { Input, Select } from '../components/common/Input';
import { LoadingSpinner, SkeletonRow } from '../components/common/LoadingSpinner';
import { getStatusBadge } from '../utils/helpers';

export default function DatabasesPage() {
  const [databases, setDatabases] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [bannerSuccess, setBannerSuccess] = useState(null);

  // Connection modal state
  const [isConnectModalOpen, setIsConnectModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    database_type: 'mysql',
    source_name: '',
    host: 'localhost',
    port: '3306',
    database: '',
    username: 'root',
    password: '',
    ssl_enabled: false,
  });
  const [testResult, setTestResult] = useState(null);
  const [isTesting, setIsTesting] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [formError, setFormError] = useState(null);

  // Schema Drawer/Modal state
  const [schemaData, setSchemaData] = useState(null);
  const [isLoadingSchema, setIsLoadingSchema] = useState(false);
  const [isSchemaModalOpen, setIsSchemaModalOpen] = useState(false);
  const [selectedDb, setSelectedDb] = useState(null);

  // Delete modal state
  const [dbToDelete, setDbToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const fetchDatabases = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await databasesApi.list();
      setDatabases(data || []);
    } catch (err) {
      setError(err.message || 'Failed to load external databases.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDatabases();
  }, []);

  const handleTypeChange = (newType) => {
    setFormData((prev) => ({
      ...prev,
      database_type: newType,
      port: newType === 'mysql' ? '3306' : '5432',
    }));
  };

  const handleTestConnection = async () => {
    setTestResult(null);
    setFormError(null);
    if (!formData.source_name || !formData.host || !formData.database || !formData.username) {
      setFormError('Please fill in all connection fields first.');
      return;
    }

    setIsTesting(true);
    try {
      const res = await databasesApi.testConnection(formData);
      setTestResult({ success: true, message: res.message || 'Connection successful!' });
    } catch (err) {
      setTestResult({ success: false, message: err.message || 'Connection test failed.' });
    } finally {
      setIsTesting(false);
    }
  };

  const handleConnectSubmit = async (e) => {
    e.preventDefault();
    setFormError(null);
    setIsConnecting(true);

    try {
      const newSource = await databasesApi.connect(formData);
      setIsConnectModalOpen(false);
      setBannerSuccess(`Connected to external database "${newSource.source_name}" successfully.`);
      // Reset form
      setFormData({
        database_type: 'mysql',
        source_name: '',
        host: 'localhost',
        port: '3306',
        database: '',
        username: 'root',
        password: '',
        ssl_enabled: false,
      });
      setTestResult(null);
      await fetchDatabases();
    } catch (err) {
      setFormError(err.message || 'Unable to establish database connection.');
    } finally {
      setIsConnecting(false);
    }
  };

  const handleViewSchema = async (db) => {
    setSelectedDb(db);
    setIsSchemaModalOpen(true);
    setIsLoadingSchema(true);
    setSchemaData(null);

    try {
      const res = await databasesApi.getSchema(db.id);
      setSchemaData(res);
    } catch (err) {
      setError(err.message || 'Could not discover schema. The database may be disconnected.');
      setIsSchemaModalOpen(false);
    } finally {
      setIsLoadingSchema(false);
    }
  };

  const handleToggleConnection = async (db) => {
    try {
      if (db.connection_status === 'connected') {
        await databasesApi.disconnect(db.id);
        setBannerSuccess(`Disconnected "${db.source_name}".`);
      } else {
        await databasesApi.reconnect(db.id);
        setBannerSuccess(`Reconnected "${db.source_name}".`);
      }
      await fetchDatabases();
    } catch (err) {
      setError(err.message || 'Unable to update database connection status.');
    }
  };

  const handleDeleteConfirm = async () => {
    if (!dbToDelete) return;
    setIsDeleting(true);
    try {
      await databasesApi.delete(dbToDelete.id);
      setDbToDelete(null);
      setBannerSuccess(`Database connection "${dbToDelete.source_name}" removed.`);
      await fetchDatabases();
    } catch (err) {
      setError(err.message || 'Unable to delete database connection.');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-slate-900">Database Connectors</h2>
          <p className="text-xs text-slate-500 mt-1">
            Connect live MySQL and PostgreSQL instances with encrypted credentials.
          </p>
        </div>

        <Button
          variant="primary"
          size="sm"
          icon={Plus}
          onClick={() => {
            setTestResult(null);
            setFormError(null);
            setIsConnectModalOpen(true);
          }}
        >
          Connect Database
        </Button>
      </div>

      {bannerSuccess && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-md text-xs text-emerald-700 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
            <span>{bannerSuccess}</span>
          </div>
          <button
            type="button"
            onClick={() => setBannerSuccess(null)}
            className="text-emerald-500 hover:text-emerald-700 text-xs"
          >
            Dismiss
          </button>
        </div>
      )}

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

      {/* Databases List */}
      <Card
        title={`Connected Databases (${databases.length})`}
        subtitle="Live connectors available for AI SQL query generation and schema inspection"
      >
        {isLoading ? (
          <div className="py-8">
            <SkeletonRow cols={5} rows={3} />
          </div>
        ) : databases.length === 0 ? (
          <EmptyState
            icon={Database}
            title="No databases connected yet"
            description="Add an external MySQL or PostgreSQL database to enable natural language SQL generation."
            actionText="Connect Database"
            onAction={() => setIsConnectModalOpen(true)}
          />
        ) : (
          <div className="overflow-x-auto -mx-5 -mb-5">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-600">
                  <th className="px-5 py-3">Source Name</th>
                  <th className="px-5 py-3">Engine</th>
                  <th className="px-5 py-3">Status</th>
                  <th className="px-5 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs">
                {databases.map((db) => {
                  const status = getStatusBadge(db.connection_status);
                  const isConnected = db.connection_status === 'connected';

                  return (
                    <tr key={db.id} className="hover:bg-slate-50/70 transition-colors">
                      <td className="px-5 py-3.5 font-medium text-slate-800">
                        <div className="flex items-center gap-2.5">
                          <div className="p-1.5 rounded bg-purple-50 text-purple-600 shrink-0">
                            <Database className="h-4 w-4" />
                          </div>
                          <span className="truncate max-w-xs">{db.source_name}</span>
                        </div>
                      </td>

                      <td className="px-5 py-3.5 text-slate-600 uppercase font-mono text-[11px]">
                        {db.source_type}
                      </td>

                      <td className="px-5 py-3.5">
                        <Badge
                          variant={
                            status.type === 'success'
                              ? 'success'
                              : status.type === 'error'
                              ? 'error'
                              : 'neutral'
                          }
                          size="sm"
                        >
                          {status.label}
                        </Badge>
                      </td>

                      <td className="px-5 py-3.5 text-right whitespace-nowrap">
                        <div className="flex items-center justify-end gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            icon={Eye}
                            disabled={!isConnected}
                            onClick={() => handleViewSchema(db)}
                          >
                            Schema
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            icon={isConnected ? PowerOff : Power}
                            className={isConnected ? 'text-amber-600 hover:text-amber-700' : 'text-emerald-600 hover:text-emerald-700'}
                            onClick={() => handleToggleConnection(db)}
                          >
                            {isConnected ? 'Disconnect' : 'Reconnect'}
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-rose-600 hover:text-rose-700 hover:bg-rose-50"
                            icon={Trash2}
                            onClick={() => setDbToDelete(db)}
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

      {/* Connect Database Modal */}
      <Modal
        isOpen={isConnectModalOpen}
        onClose={() => setIsConnectModalOpen(false)}
        title="Connect External Database"
        subtitle="Credentials are encrypted at rest with Fernet and never sent back to the browser."
        maxWidth="max-w-lg"
      >
        <form onSubmit={handleConnectSubmit} className="space-y-4 text-xs">
          {formError && (
            <div className="p-3 bg-rose-50 border border-rose-200 rounded text-rose-700 flex items-start gap-2">
              <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
              <span>{formError}</span>
            </div>
          )}

          {testResult && (
            <div
              className={`p-3 rounded border flex items-start gap-2 ${
                testResult.success
                  ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
                  : 'bg-rose-50 border-rose-200 text-rose-800'
              }`}
            >
              {testResult.success ? (
                <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0 mt-0.5" />
              ) : (
                <AlertCircle className="h-4 w-4 text-rose-600 shrink-0 mt-0.5" />
              )}
              <span>{testResult.message}</span>
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <Select
              label="Database Type"
              value={formData.database_type}
              onChange={(e) => handleTypeChange(e.target.value)}
              options={[
                { value: 'mysql', label: 'MySQL 8.0+' },
                { value: 'postgresql', label: 'PostgreSQL' },
              ]}
            />
            <Input
              label="Connection Display Name"
              placeholder="e.g., Production Warehouse"
              value={formData.source_name}
              onChange={(e) => setFormData({ ...formData, source_name: e.target.value })}
              required
            />
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div className="col-span-2">
              <Input
                label="Host / Endpoint"
                placeholder="db.company.com or 127.0.0.1"
                value={formData.host}
                onChange={(e) => setFormData({ ...formData, host: e.target.value })}
                required
              />
            </div>
            <div>
              <Input
                label="Port"
                type="number"
                placeholder="3306"
                value={formData.port}
                onChange={(e) => setFormData({ ...formData, port: e.target.value })}
                required
              />
            </div>
          </div>

          <Input
            label="Database Name"
            placeholder="analytics_db"
            value={formData.database}
            onChange={(e) => setFormData({ ...formData, database: e.target.value })}
            required
          />

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Username"
              placeholder="readonly_user"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              required
            />
            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required
            />
          </div>

          <label className="flex items-center gap-2 cursor-pointer pt-1">
            <input
              type="checkbox"
              checked={formData.ssl_enabled}
              onChange={(e) => setFormData({ ...formData, ssl_enabled: e.target.checked })}
              className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 h-4 w-4"
            />
            <span className="text-slate-700 font-medium text-xs">Enable SSL / TLS encryption</span>
          </label>

          <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
            <Button
              type="button"
              variant="outline"
              size="sm"
              icon={ShieldCheck}
              onClick={handleTestConnection}
              isLoading={isTesting}
            >
              Test Connection
            </Button>

            <div className="flex gap-2">
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => setIsConnectModalOpen(false)}
                disabled={isConnecting}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                size="sm"
                isLoading={isConnecting}
              >
                Save & Connect
              </Button>
            </div>
          </div>
        </form>
      </Modal>

      {/* Schema Inspection Modal */}
      <Modal
        isOpen={isSchemaModalOpen}
        onClose={() => setIsSchemaModalOpen(false)}
        title={selectedDb ? `Schema: ${selectedDb.source_name}` : 'Discovered Schema'}
        subtitle="Tables and column definitions discovered from external database metadata"
        maxWidth="max-w-2xl"
      >
        {isLoadingSchema ? (
          <div className="py-12 flex flex-col items-center justify-center gap-3">
            <LoadingSpinner size="md" />
            <span className="text-xs text-slate-500">Discovering tables and column types...</span>
          </div>
        ) : !schemaData?.schema || Object.keys(schemaData.schema).length === 0 ? (
          <p className="text-xs text-slate-500 py-6 text-center">
            No tables discovered in this external database.
          </p>
        ) : (
          <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-1 text-xs">
            {Object.entries(schemaData.schema).map(([tableName, columns]) => (
              <div key={tableName} className="border border-slate-200 rounded-md overflow-hidden bg-white">
                <div className="px-3 py-2 bg-slate-50 border-b border-slate-200 font-semibold text-slate-800 flex items-center gap-2">
                  <Table className="h-3.5 w-3.5 text-blue-600" />
                  <span>{tableName}</span>
                  <span className="text-[10px] text-slate-400 font-mono font-normal">
                    ({Array.isArray(columns) ? columns.length : 0} columns)
                  </span>
                </div>

                <div className="p-2 overflow-x-auto">
                  <table className="w-full text-left border-collapse text-[11px] font-mono">
                    <thead className="text-slate-500 border-b border-slate-100">
                      <tr>
                        <th className="px-2 py-1">Column</th>
                        <th className="px-2 py-1">Type</th>
                        <th className="px-2 py-1">Nullable</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                      {Array.isArray(columns) &&
                        columns.map((col, idx) => (
                          <tr key={idx} className="hover:bg-slate-50">
                            <td className="px-2 py-1 font-medium text-slate-800">
                              {col.column_name || col.name || String(col)}
                            </td>
                            <td className="px-2 py-1 text-blue-600">
                              {col.data_type || col.type || 'varchar'}
                            </td>
                            <td className="px-2 py-1 text-slate-500">
                              {col.is_nullable ? 'YES' : 'NO'}
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ))}
          </div>
        )}
      </Modal>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={Boolean(dbToDelete)}
        onClose={() => setDbToDelete(null)}
        onConfirm={handleDeleteConfirm}
        title="Disconnect Database"
        message={`Are you sure you want to disconnect and delete "${dbToDelete?.source_name}"? If there are any datasets referencing this database, they must be unlinked first.`}
        confirmText="Disconnect Database"
        isLoading={isDeleting}
      />
    </div>
  );
}
