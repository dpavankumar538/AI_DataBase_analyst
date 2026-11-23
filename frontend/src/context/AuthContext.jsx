import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authApi } from '../api/auth';
import { getTokens, clearTokens } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const checkAuth = useCallback(async () => {
    const { access_token } = getTokens();
    if (!access_token) {
      setUser(null);
      setIsLoading(false);
      return;
    }

    try {
      const profile = await authApi.getProfile();
      setUser(profile);
      setError(null);
    } catch {
      // Token may be invalid or server unreachable
      clearTokens();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();

    const handleAuthCleared = () => {
      setUser(null);
    };

    window.addEventListener('ai_analysis:auth_cleared', handleAuthCleared);
    window.addEventListener('datapilot:auth_cleared', handleAuthCleared);
    return () => {
      window.removeEventListener('ai_analysis:auth_cleared', handleAuthCleared);
      window.removeEventListener('datapilot:auth_cleared', handleAuthCleared);
    };
  }, [checkAuth]);

  const login = async (credentials) => {
    setIsLoading(true);
    setError(null);
    try {
      await authApi.login(credentials);
      const profile = await authApi.getProfile();
      setUser(profile);
      return profile;
    } catch (err) {
      setError(err.message || 'Login failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData) => {
    setIsLoading(true);
    setError(null);
    try {
      const newUser = await authApi.register(userData);
      // Auto login after registration
      await authApi.login({
        email: userData.email,
        password: userData.password,
      });
      const profile = await authApi.getProfile();
      setUser(profile);
      return newUser;
    } catch (err) {
      setError(err.message || 'Registration failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await authApi.logout();
    } finally {
      setUser(null);
      setIsLoading(false);
    }
  };

  const refreshUser = async () => {
    try {
      const profile = await authApi.getProfile();
      setUser(profile);
    } catch {
      // Ignored
    }
  };

  const value = {
    user,
    isAuthenticated: Boolean(user),
    isLoading,
    error,
    login,
    register,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
