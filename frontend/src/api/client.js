/**
 * Centralized API Client for AI Data Analysis
 * Handles JWT access & refresh tokens, automatic token refreshing,
 * error parsing, and multipart file uploads.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

export const getTokens = () => {
  try {
    const access_token =
      localStorage.getItem('ai_analysis_access_token') ||
      localStorage.getItem('datapilot_access_token');
    const refresh_token =
      localStorage.getItem('ai_analysis_refresh_token') ||
      localStorage.getItem('datapilot_refresh_token');
    return { access_token, refresh_token };
  } catch {
    return { access_token: null, refresh_token: null };
  }
};

export const setTokens = (accessToken, refreshToken) => {
  if (accessToken) {
    localStorage.setItem('ai_analysis_access_token', accessToken);
    localStorage.setItem('datapilot_access_token', accessToken);
  }
  if (refreshToken) {
    localStorage.setItem('ai_analysis_refresh_token', refreshToken);
    localStorage.setItem('datapilot_refresh_token', refreshToken);
  }
};

export const clearTokens = () => {
  localStorage.removeItem('ai_analysis_access_token');
  localStorage.removeItem('datapilot_access_token');
  localStorage.removeItem('ai_analysis_refresh_token');
  localStorage.removeItem('datapilot_refresh_token');
  window.dispatchEvent(new CustomEvent('datapilot:auth_cleared'));
  window.dispatchEvent(new CustomEvent('ai_analysis:auth_cleared'));
};

/**
 * Core fetch wrapper
 */
export async function apiClient(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const { access_token, refresh_token } = getTokens();

  const headers = new Headers(options.headers || {});

  // Add Authorization header if available and not explicitly skipped
  if (access_token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${access_token}`);
  }

  // If body is NOT FormData, set Content-Type: application/json if not set
  if (options.body && !(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const config = {
    ...options,
    headers,
  };

  try {
    let response = await fetch(url, config);

    // If 401 Unauthorized and we have a refresh token, attempt token refresh
    if (response.status === 401 && refresh_token && !endpoint.includes('/auth/login') && !endpoint.includes('/auth/refresh')) {
      if (isRefreshing) {
        // Wait for token refresh to finish
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((newToken) => {
          config.headers.set('Authorization', `Bearer ${newToken}`);
          return fetch(url, config).then(handleResponse);
        });
      }

      isRefreshing = true;

      try {
        const refreshResponse = await fetch(`${BASE_URL}/auth/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token }),
        });

        if (!refreshResponse.ok) {
          throw new Error('Session expired');
        }

        const data = await refreshResponse.json();
        setTokens(data.access_token, data.refresh_token);
        processQueue(null, data.access_token);

        // Retry original request with new access token
        config.headers.set('Authorization', `Bearer ${data.access_token}`);
        response = await fetch(url, config);
      } catch (refreshErr) {
        processQueue(refreshErr, null);
        clearTokens();
        throw new Error('Your session has expired. Please log in again.');
      } finally {
        isRefreshing = false;
      }
    }

    return await handleResponse(response);
  } catch (error) {
    if (error.message.includes('Failed to fetch') || error.name === 'TypeError') {
      throw new Error(`Unable to reach the backend server at ${BASE_URL}. Ensure the backend is running.`);
    }
    throw error;
  }
}

async function handleResponse(response) {
  // Check if response has no content (204)
  if (response.status === 204) {
    return null;
  }

  const contentType = response.headers.get('content-type');
  const isJson = contentType && contentType.includes('application/json');

  let data;
  try {
    data = isJson ? await response.json() : await response.text();
  } catch {
    data = null;
  }

  if (!response.ok) {
    let errorMessage = 'An unexpected error occurred.';

    if (data) {
      if (typeof data.detail === 'string') {
        errorMessage = data.detail;
      } else if (Array.isArray(data.detail)) {
        // Pydantic validation error array
        errorMessage = data.detail.map((err) => `${err.loc?.slice(-1)[0] || 'Field'}: ${err.msg}`).join(', ');
      } else if (typeof data.message === 'string') {
        errorMessage = data.message;
      } else if (typeof data === 'string') {
        errorMessage = data;
      }
    }

    const error = new Error(errorMessage);
    error.status = response.status;
    error.data = data;
    throw error;
  }

  return data;
}

export default apiClient;
