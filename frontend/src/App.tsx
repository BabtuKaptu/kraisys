import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConfigProvider } from 'antd';
import ruRU from 'antd/locale/ru_RU';
import 'antd/dist/reset.css';

import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Models } from './pages/Models';
import { Materials } from './pages/Materials';
import { Warehouse } from './pages/Warehouse';
import { Production } from './pages/Production';
import { References } from './pages/References';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 минут для обычных данных
      refetchOnWindowFocus: false,
      retry: (failureCount, error: any) => {
        // Не повторяем запросы для 4xx ошибок
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        return failureCount < 3;
      },
    },
    mutations: {
      retry: false, // Не повторяем мутации автоматически
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider locale={ruRU}>
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/models" element={<Models />} />
              <Route path="/materials" element={<Materials />} />
              <Route path="/warehouse" element={<Warehouse />} />
              <Route path="/production" element={<Production />} />
              <Route path="/references" element={<References />} />
            </Routes>
          </Layout>
        </Router>
      </ConfigProvider>
    </QueryClientProvider>
  );
}

export default App;
