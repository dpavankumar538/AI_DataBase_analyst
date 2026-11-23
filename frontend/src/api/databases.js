import { apiClient } from './client';

export const databasesApi = {
  async list() {
    return await apiClient('/data-sources/');
  },

  async testConnection({ database_type, source_name, host, port, database, username, password, ssl_enabled }) {
    return await apiClient('/data-sources/test-connection', {
      method: 'POST',
      body: JSON.stringify({
        database_type,
        source_name,
        host,
        port: port ? parseInt(port, 10) : null,
        database,
        username,
        password,
        ssl_enabled: Boolean(ssl_enabled),
      }),
    });
  },

  async connect({ database_type, source_name, host, port, database, username, password, ssl_enabled }) {
    return await apiClient('/data-sources/connect', {
      method: 'POST',
      body: JSON.stringify({
        database_type,
        source_name,
        host,
        port: port ? parseInt(port, 10) : null,
        database,
        username,
        password,
        ssl_enabled: Boolean(ssl_enabled),
      }),
    });
  },

  async getSchema(dataSourceId) {
    return await apiClient(`/data-sources/${dataSourceId}/schema`);
  },

  async disconnect(dataSourceId) {
    return await apiClient(`/data-sources/${dataSourceId}/disconnect`, {
      method: 'POST',
    });
  },

  async reconnect(dataSourceId) {
    return await apiClient(`/data-sources/${dataSourceId}/reconnect`, {
      method: 'POST',
    });
  },

  async delete(dataSourceId) {
    return await apiClient(`/data-sources/${dataSourceId}`, {
      method: 'DELETE',
    });
  },
};
