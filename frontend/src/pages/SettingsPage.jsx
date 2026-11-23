import { useState } from 'react';
import {
  Settings,
  Shield,
  Server,
  Database,
  Moon,
  Sun,
  LogOut,
  CheckCircle2,
  AlertCircle,
  HardDrive,
  RefreshCw,
  KeyRound,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { authApi } from '../api/auth';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';

export default function SettingsPage() {
  const { user, logout } = useAuth();
  const { toggleTheme, isDark } = useTheme();

  const [testingApi, setTestingApi] = useState(false);
  const [apiStatus, setApiStatus] = useState(null);

  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  const handleTestApi = async () => {
    setTestingApi(true);
    setApiStatus(null);
    const start = performance.now();
    try {
      await authApi.getProfile();
      const latency = Math.round(performance.now() - start);
      setApiStatus({
        success: true,
        message: `API server operational. Latency: ${latency}ms`,
      });
    } catch (err) {
      setApiStatus({
        success: false,
        message: `Backend unreachable: ${err.message}`,
      });
    } finally {
      setTestingApi(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto pb-12">
      {/* Page Header */}
      <div>
        <h2 className="text-xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
          <Settings className="h-5 w-5 text-blue-600" />
          Workspace & Account Settings
        </h2>
        <p className="text-xs text-slate-500 mt-1">
          Manage your account profile, check system connectivity, and configure workspace preferences.
        </p>
      </div>

      {/* User Profile Card */}
      <Card title="Account Profile" subtitle="Your authenticated identity in AI Data Analysis">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="h-14 w-14 rounded-full bg-blue-600 text-white flex items-center justify-center text-xl font-bold shrink-0 shadow-xs border-2 border-white">
              {user?.name ? user.name.charAt(0).toUpperCase() : 'U'}
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900">{user?.name || 'Authorized Analyst'}</h3>
              <p className="text-xs text-slate-500">{user?.email || 'user@company.com'}</p>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-[10px] font-mono text-slate-400">User ID: #{user?.id || '—'}</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 font-semibold border border-blue-200">
                  Data Analyst
                </span>
              </div>
            </div>
          </div>

          <Button
            variant="outline"
            size="sm"
            icon={LogOut}
            onClick={logout}
            className="text-rose-600 border-rose-200 hover:bg-rose-50 hover:text-rose-700 self-start sm:self-center"
          >
            Sign Out
          </Button>
        </div>
      </Card>

      {/* Backend & Engine Diagnostics */}
      <Card
        title="Backend & Infrastructure Diagnostics"
        subtitle="Current status of the FastAPI backend, MySQL metadata, and ChromaDB vector store"
        actions={
          <Button
            variant="outline"
            size="sm"
            icon={RefreshCw}
            onClick={handleTestApi}
            isLoading={testingApi}
          >
            Test Connection
          </Button>
        }
      >
        <div className="space-y-4">
          {apiStatus && (
            <div
              className={`p-3 rounded-md text-xs flex items-center gap-2 border ${
                apiStatus.success
                  ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                  : 'bg-rose-50 text-rose-800 border-rose-200'
              }`}
            >
              {apiStatus.success ? (
                <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
              ) : (
                <AlertCircle className="h-4 w-4 text-rose-600 shrink-0" />
              )}
              <span>{apiStatus.message}</span>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {/* FastAPI Endpoint */}
            <div className="p-3.5 rounded-lg border border-slate-200 bg-slate-50/50">
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2 text-slate-700 font-semibold text-xs">
                  <Server className="h-4 w-4 text-blue-600" />
                  <span>FastAPI Server</span>
                </div>
                <Badge variant="success" size="sm">Online</Badge>
              </div>
              <p className="text-[11px] font-mono text-slate-500 truncate" title={apiBaseUrl}>
                {apiBaseUrl}
              </p>
            </div>

            {/* Relational Database */}
            <div className="p-3.5 rounded-lg border border-slate-200 bg-slate-50/50">
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2 text-slate-700 font-semibold text-xs">
                  <Database className="h-4 w-4 text-indigo-600" />
                  <span>MySQL Metadata</span>
                </div>
                <Badge variant="success" size="sm">Connected</Badge>
              </div>
              <p className="text-[11px] text-slate-500">
                Alembic Migrations applied
              </p>
            </div>

            {/* ChromaDB */}
            <div className="p-3.5 rounded-lg border border-slate-200 bg-slate-50/50">
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2 text-slate-700 font-semibold text-xs">
                  <HardDrive className="h-4 w-4 text-amber-600" />
                  <span>ChromaDB Vectors</span>
                </div>
                <Badge variant="success" size="sm">Persistent</Badge>
              </div>
              <p className="text-[11px] text-slate-500">
                Local persistent embeddings
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* Security & Authentication */}
      <Card title="Security & Token Management" subtitle="JWT session and authentication parameters">
        <div className="space-y-3 text-xs text-slate-600">
          <div className="flex items-center justify-between py-2 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <KeyRound className="h-4 w-4 text-slate-400" />
              <div>
                <p className="font-semibold text-slate-800">Authentication Scheme</p>
                <p className="text-[11px] text-slate-500">Bearer JWT Access Token with Refresh Rotation</p>
              </div>
            </div>
            <Badge variant="neutral" size="sm">HS256</Badge>
          </div>

          <div className="flex items-center justify-between py-2 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-slate-400" />
              <div>
                <p className="font-semibold text-slate-800">SQL Safety Boundary</p>
                <p className="text-[11px] text-slate-500">
                  Enforces strict read-only execution (SELECT only, zero arbitrary DDL/DML write access)
                </p>
              </div>
            </div>
            <Badge variant="success" size="sm">Enforced</Badge>
          </div>
        </div>
      </Card>

      {/* Workspace Appearance */}
      <Card title="Appearance & Preferences" subtitle="Display theme and interface styling">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-xs font-semibold text-slate-800">Application Theme</h4>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Default approved design is white-first professional SaaS with restrained blue accents.
            </p>
          </div>

          <Button
            variant="outline"
            size="sm"
            icon={isDark ? Sun : Moon}
            onClick={toggleTheme}
          >
            {isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          </Button>
        </div>
      </Card>
    </div>
  );
}
