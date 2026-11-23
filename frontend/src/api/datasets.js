import { apiClient } from './client';

export const datasetsApi = {
  async list() {
    return await apiClient('/datasets/');
  },

  async upload(file) {
    const formData = new FormData();
    formData.append('file', file);

    return await apiClient('/datasets/upload', {
      method: 'POST',
      body: formData,
    });
  },

  async getAnalysis(datasetId) {
    return await apiClient(`/datasets/${datasetId}/analysis`);
  },

  async delete(datasetId) {
    return await apiClient(`/datasets/${datasetId}`, {
      method: 'DELETE',
    });
  },
};
