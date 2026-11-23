import { apiClient, setTokens, clearTokens, getTokens } from './client';

export const authApi = {
  async register({ name, email, password }) {
    return await apiClient('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    });
  },

  async login({ email, password }) {
    // Backend expects OAuth2PasswordRequestForm (form-urlencoded with username and password)
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const tokens = await apiClient('/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });

    setTokens(tokens.access_token, tokens.refresh_token);
    return tokens;
  },

  async getProfile() {
    return await apiClient('/auth/me');
  },

  async logout() {
    const { refresh_token } = getTokens();
    if (refresh_token) {
      try {
        await apiClient('/auth/logout', {
          method: 'POST',
          body: JSON.stringify({ refresh_token }),
        });
      } catch {
        // Fallback to local token clearance if server fails
      }
    }
    clearTokens();
  },
};
