import { apiClient } from './httpClient';
import { Material, MaterialDraft, MaterialsListQuery, MaterialsListResult } from '../types';

export const materialsApi = {
  async list(query: MaterialsListQuery = {}): Promise<MaterialsListResult> {
    const response = await apiClient.get('/materials', { 
      params: {
        ...query,
        // Передаем поисковый запрос на бэкенд для server-side поиска
        search: query.search,
        group: query.group,
      },
    });
    return response.data;
  },

  async getById(id: string): Promise<Material> {
    const response = await apiClient.get(`/materials/${id}`);
    return response.data;
  },

  async create(draft: MaterialDraft): Promise<Material> {
    const response = await apiClient.post('/materials', draft);
    return response.data;
  },

  async update(id: string, draft: Partial<MaterialDraft>): Promise<Material> {
    const response = await apiClient.put(`/materials/${id}`, draft);
    return response.data;
  },

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/materials/${id}`);
  },

  async getStats(): Promise<any> {
    const response = await apiClient.get('/materials/stats/summary');
    return response.data;
  },
};
