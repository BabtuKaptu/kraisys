import axios from 'axios';

// Fix API URL to match backend port
const API_BASE_URL = 'http://localhost:8002/api/v1';

// Frontend logging utility
const logToConsole = (level: 'info' | 'warn' | 'error', message: string, data?: any) => {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}`;

  console[level](logMessage, data || '');

  // Also log to localStorage for debugging
  try {
    const logs = JSON.parse(localStorage.getItem('krai_frontend_logs') || '[]');
    logs.push({
      timestamp,
      level,
      message,
      data: data ? JSON.stringify(data) : null
    });

    // Keep only last 100 logs
    if (logs.length > 100) {
      logs.splice(0, logs.length - 100);
    }

    localStorage.setItem('krai_frontend_logs', JSON.stringify(logs));
  } catch (e) {
    console.error('Failed to store log to localStorage:', e);
  }
};

;(window as any).KRAI_LOGS = () => {
  const logs = JSON.parse(localStorage.getItem('krai_frontend_logs') || '[]');
  console.table(logs);
  return logs;
};

logToConsole('info', `Frontend API configured for: ${API_BASE_URL}`);

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    logToConsole('info', `API Request: ${config.method?.toUpperCase()} ${config.url}`, {
      params: config.params,
      data: config.data
    });
    return config;
  },
  (error) => {
    logToConsole('error', 'API Request Error', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for logging
api.interceptors.response.use(
  (response) => {
    logToConsole('info', `API Response: ${response.status} ${response.config.url}`, {
      status: response.status,
      data: response.data
    });
    return response;
  },
  (error) => {
    const message = error.response
      ? `API Error: ${error.response.status} ${error.config?.url}`
      : `API Network Error: ${error.message}`;

    logToConsole('error', message, {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      url: error.config?.url
    });
    return Promise.reject(error);
  }
);

// Models API
export const modelsApi = {
  getAll: (params?: { page?: number; size?: number; search?: string; is_active?: boolean }) =>
    api.get('/models', { params }),
  getById: (id: number) => api.get(`/models/${id}`),
  create: (data: any) => api.post('/models', data),
  update: (id: number, data: any) => api.put(`/models/${id}`, data),
  delete: (id: number) => api.delete(`/models/${id}`),
  getStats: () => api.get('/models/stats/summary'),
};

// Materials API
export const materialsApi = {
  getAll: (params?: { page?: number; size?: number; search?: string; group_type?: string; is_active?: boolean }) =>
    api.get('/materials', { params }),
  getById: (id: number) => api.get(`/materials/${id}`),
  create: (data: any) => api.post('/materials', data),
  update: (id: number, data: any) => api.put(`/materials/${id}`, data),
  delete: (id: number) => api.delete(`/materials/${id}`),
  getStats: () => api.get('/materials/stats/summary'),
};

// Warehouse API
export const warehouseApi = {
  getStock: (params?: { page?: number; size?: number; search?: string; status?: string; location?: string }) =>
    api.get('/warehouse/stock', { params }),
  getStockItem: (id: number) => api.get(`/warehouse/stock/${id}`),
  adjustStock: (id: number, data: { quantity: number; reason: string }) =>
    api.post(`/warehouse/stock/${id}/adjust`, data),
  getStats: () => api.get('/warehouse/stats/summary'),
  getLowStockAlerts: () => api.get('/warehouse/alerts/low-stock'),
};

// Production API
export const productionApi = {
  getOrders: (params?: { page?: number; size?: number; search?: string; status?: string; priority?: string }) =>
    api.get('/production/orders', { params }),
  getOrder: (id: number) => api.get(`/production/orders/${id}`),
  createOrder: (data: any) => api.post('/production/orders', data),
  updateOrderStatus: (id: number, status: string) =>
    api.put(`/production/orders/${id}/status`, { status }),
  getDashboard: () => api.get('/production/stats/dashboard'),
};

// References API
export const referencesApi = {
  getSizeRuns: (params?: { gender?: string; is_active?: boolean }) =>
    api.get('/references/size-runs', { params }),
  getSizeRun: (id: number) => api.get(`/references/size-runs/${id}`),
  createSizeRun: (data: any) => api.post('/references/size-runs', data),

  getSpecifications: (params?: { model_id?: number; size?: string }) =>
    api.get('/references/specifications', { params }),
  getSpecification: (id: number) => api.get(`/references/specifications/${id}`),
  createSpecification: (data: any) => api.post('/references/specifications', data),

  getWorkOperations: (params?: { category?: string; is_active?: boolean }) =>
    api.get('/references/work-operations', { params }),
  getWorkOperation: (id: number) => api.get(`/references/work-operations/${id}`),
  createWorkOperation: (data: any) => api.post('/references/work-operations', data),

  getEnums: () => api.get('/references/enums'),
};

export default api;
