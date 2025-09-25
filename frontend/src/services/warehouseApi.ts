import { apiClient } from './httpClient';
import {
  WarehouseStock,
  WarehouseListQuery,
  WarehouseListResult,
  WarehouseReceiptDraft,
  WarehouseIssueDraft,
} from '../types';

const notImplemented = (operation: string): never => {
  throw new Error(`Warehouse API for "${operation}" не реализован на бэкенде`);
};

export const warehouseApi = {
  async list(query: WarehouseListQuery = {}): Promise<WarehouseListResult> {
    const response = await apiClient.get('/warehouse/stock', { params: query });
    return response.data;
  },

  async getById(id: string): Promise<WarehouseStock> {
    const response = await apiClient.get(`/warehouse/stock/${id}`);
    return response.data;
  },

  async transactions(): Promise<never> {
    return notImplemented('transactions');
  },

  async receipt(draft: WarehouseReceiptDraft): Promise<void> {
    await apiClient.post('/warehouse/receipt', draft);
  },

  async issue(draft: WarehouseIssueDraft): Promise<void> {
    await apiClient.post('/warehouse/issue', draft);
  },

  async inventory(): Promise<never> {
    return notImplemented('inventory');
  },

  async adjustStock(): Promise<never> {
    return notImplemented('adjust stock');
  },

  async getStats(): Promise<never> {
    return notImplemented('stats summary');
  },

  async getLowStockAlerts(): Promise<never> {
    return notImplemented('low stock alerts');
  },
};
