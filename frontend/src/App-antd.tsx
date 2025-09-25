import { ConfigProvider } from 'antd';
import { SimpleLayout } from './components/SimpleLayout';
import { SimpleDashboard } from './pages/SimpleDashboard';

function App() {
  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#2196F3',
          colorSuccess: '#4CAF50',
          colorWarning: '#FF9800',
          colorError: '#F44336',
          borderRadius: 8,
          fontSize: 14,
        },
      }}
    >
      <SimpleLayout>
        <SimpleDashboard />
      </SimpleLayout>
    </ConfigProvider>
  );
}

export default App;
