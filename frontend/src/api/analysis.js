import { apiClient } from './client';

export const analysisApi = {
  async run({ question, dataset_ids = [], document_ids = [], data_source_ids = [] }) {
    return await apiClient('/analysis/run', {
      method: 'POST',
      body: JSON.stringify({
        question,
        dataset_ids,
        document_ids,
        data_source_ids,
      }),
    });
  },

  async list(limit = 50, offset = 0) {
    return await apiClient(`/analysis/?limit=${limit}&offset=${offset}`);
  },

  async getDetail(analysisId) {
    return await apiClient(`/analysis/${analysisId}`);
  },
};
