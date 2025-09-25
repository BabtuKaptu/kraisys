import { apiClient } from './httpClient';
import { ReferenceItem, ReferenceListQuery, ReferenceListResult } from '../types';

export const referenceApi = {
  async list(query: ReferenceListQuery = {}): Promise<ReferenceListResult> {
    const response = await apiClient.get('/references', { 
      params: {
        ...query,
        // Передаем поисковый запрос на бэкенд для server-side поиска
        search: query.search,
        type: query.type,
      },
    });
    return response.data;
  },

  async getById(id: string): Promise<ReferenceItem> {
    const response = await apiClient.get(`/references/${id}`);
    return response.data;
  },

  async create(draft: Partial<ReferenceItem>): Promise<ReferenceItem> {
    const response = await apiClient.post('/references', draft);
    return response.data;
  },

  async update(id: string, draft: Partial<ReferenceItem>): Promise<ReferenceItem> {
    const response = await apiClient.put(`/references/${id}`, draft);
    return response.data;
  },

  async remove(id: string): Promise<void> {
    await apiClient.delete(`/references/${id}`);
  },
};
