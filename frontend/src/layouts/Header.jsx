import { useState, useRef, useEffect } from 'react';
import { Menu, Bell, LogOut, Settings, ExternalLink } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useLocation, Link } from 'react-router-dom';

export default function Header({ onOpenMobile }) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const profileMenuRef = useRef(null);

  // Derive title from pathname
  const getPageTitle = (pathname) => {
    switch (pathname) {
      case '/':
        return 'Dashboard Overview';
      case '/analyst':
        return 'AI Analyst Workspace';
      case '/datasets':
        return 'Dataset Management';
      case '/databases':
        return 'Database Connectors';
      case '/documents':
        return 'Document Knowledge Base';
      case '/history':
        return 'Analysis History';
      case '/settings':
        return 'Account & Workspace Settings';
      default:
        if (pathname.startsWith('/history/')) {
          return 'Analysis Details';
        }
        return 'AI Data Analysis';
    }
  };

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (profileMenuRef.current && !profileMenuRef.current.contains(e.target)) {
        setShowProfileMenu(false);
        setShowNotifications(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-200 bg-white/95 px-4 lg:px-8 backdrop-blur-xs">
      {/* Left: Mobile hamburger & Page Title */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onOpenMobile}
          className="lg:hidden p-2 rounded-md text-slate-600 hover:bg-slate-100"
          aria-label="Open navigation drawer"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div>
          <h1 className="text-base font-semibold text-slate-900 leading-tight">
            {getPageTitle(location.pathname)}
          </h1>
          <p className="hidden sm:block text-[11px] text-slate-500">
            AI-powered structured and unstructured intelligence
          </p>
        </div>
      </div>

      {/* Right Actions: API Status, Notifications, Profile */}
      <div className="flex items-center gap-3" ref={profileMenuRef}>
        {/* Backend Online indicator */}
        <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-50 border border-slate-200 text-[11px] text-slate-600">
          <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>API Connected</span>
        </div>

        {/* Notifications Button */}
        <div className="relative">
          <button
            type="button"
            onClick={() => {
              setShowNotifications((prev) => !prev);
              setShowProfileMenu(false);
            }}
            className="p-2 rounded-md text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors relative"
            aria-label="Notifications"
          >
            <Bell className="h-4 w-4" />
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-72 rounded-lg border border-slate-200 bg-white p-4 shadow-lg text-xs z-50">
              <div className="flex items-center justify-between border-b border-slate-100 pb-2 mb-2 font-semibold text-slate-800">
                <span>Notifications</span>
                <span className="text-[10px] text-slate-400 font-normal">All systems normal</span>
              </div>
              <p className="text-slate-500 text-[11px] py-2 text-center">
                No new critical alerts. Your database and document vectors are synced.
              </p>
            </div>
          )}
        </div>

        {/* Profile Avatar & Dropdown */}
        <div className="relative">
          <button
            type="button"
            onClick={() => {
              setShowProfileMenu((prev) => !prev);
              setShowNotifications(false);
            }}
            className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-slate-100 transition-colors text-slate-700"
          >
            <div className="h-7 w-7 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-semibold shadow-2xs">
              {user?.name ? user.name.charAt(0).toUpperCase() : 'U'}
            </div>
            <span className="hidden sm:block text-xs font-medium text-slate-800 truncate max-w-[120px]">
              {user?.name || 'Account'}
            </span>
          </button>

          {showProfileMenu && (
            <div className="absolute right-0 mt-2 w-56 rounded-lg border border-slate-200 bg-white py-2 shadow-lg text-xs z-50 divide-y divide-slate-100">
              <div className="px-4 py-2">
                <p className="font-semibold text-slate-900 truncate">{user?.name}</p>
                <p className="text-[11px] text-slate-500 truncate">{user?.email}</p>
              </div>

              <div className="py-1">
                <Link
                  to="/settings"
                  onClick={() => setShowProfileMenu(false)}
                  className="flex items-center gap-2 px-4 py-2 text-slate-700 hover:bg-slate-50"
                >
                  <Settings className="h-3.5 w-3.5 text-slate-400" />
                  <span>Workspace Settings</span>
                </Link>
                <Link
                  to="/analyst"
                  onClick={() => setShowProfileMenu(false)}
                  className="flex items-center gap-2 px-4 py-2 text-slate-700 hover:bg-slate-50"
                >
                  <ExternalLink className="h-3.5 w-3.5 text-slate-400" />
                  <span>Open AI Analyst</span>
                </Link>
              </div>

              <div className="py-1">
                <button
                  type="button"
                  onClick={() => {
                    setShowProfileMenu(false);
                    logout();
                  }}
                  className="flex w-full items-center gap-2 px-4 py-2 text-rose-600 hover:bg-rose-50 transition-colors"
                >
                  <LogOut className="h-3.5 w-3.5 text-rose-500" />
                  <span>Log Out</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
