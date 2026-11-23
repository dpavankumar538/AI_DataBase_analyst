import { apiClient } from './client';

export const documentsApi = {
  async list() {
    return await apiClient('/documents/');
  },

  async upload(file) {
    const formData = new FormData();
    formData.append('file', file);

    return await apiClient('/documents/upload', {
      method: 'POST',
      body: formData,
    });
  },

  async getDetails(documentId) {
    return await apiClient(`/documents/${documentId}`);
  },

  async delete(documentId) {
    return await apiClient(`/documents/${documentId}`, {
      method: 'DELETE',
    });
  },
};
