import React from 'react';
import { Card, Typography } from 'antd';

const { Title } = Typography;

export const Production: React.FC = () => {
  return (
    <div>
      <div className="page-header">
        <Title level={2}>Производство</Title>
        <p>Планирование и управление производством</p>
      </div>
      <Card className="content-card">
        <p>Производственное планирование в разработке...</p>
      </Card>
    </div>
  );
};