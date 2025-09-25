import { apiClient } from './httpClient';
import { Model, ModelDraft, ModelsListQuery, ModelsListResult, ModelVariant } from '../types';

export const modelsApi = {
  async list(query: ModelsListQuery = {}): Promise<ModelsListResult> {
    const response = await apiClient.get('/models', { params: query });
    return response.data;
  },

  async getById(id: string): Promise<Model> {
    const response = await apiClient.get(`/models/${id}`);
    return response.data;
  },

  async create(draft: ModelDraft): Promise<Model> {
    const response = await apiClient.post('/models', draft);
    return response.data;
  },

  async update(id: string, draft: Partial<ModelDraft>): Promise<Model> {
    const response = await apiClient.put(`/models/${id}`, draft);
    return response.data;
  },

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/models/${id}`);
  },

  async upsertVariant(modelId: string, variant: ModelVariant): Promise<Model> {
    const response = await apiClient.post(`/models/${modelId}/variants`, variant);
    return response.data;
  },

  async deleteVariant(modelId: string, variantId: string): Promise<Model> {
    const response = await apiClient.delete(`/models/${modelId}/variants/${variantId}`);
    return response.data;
  },

  async getStats(): Promise<any> {
    const response = await apiClient.get('/models/stats/summary');
    return response.data;
  },
};
