import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConfigProvider, theme } from 'antd';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Models } from './pages/Models';
import { Materials } from './pages/Materials';
import { Warehouse } from './pages/Warehouse';
import { Production } from './pages/Production';
import { References } from './pages/References';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
});

// Ant Design theme configuration
const antdTheme = {
  algorithm: theme.defaultAlgorithm,
  token: {
    colorPrimary: '#2196F3',
    colorSuccess: '#4CAF50',
    colorWarning: '#FF9800',
    colorError: '#F44336',
    colorInfo: '#2196F3',
    borderRadius: 8,
    fontSize: 14,
  },
};

function App() {
  return (
    <ConfigProvider theme={antdTheme}>
      <QueryClientProvider client={queryClient}>
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
      </QueryClientProvider>
    </ConfigProvider>
  );
}

export default App;
