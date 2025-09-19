import React from 'react';
import { Card, Typography } from 'antd';

const { Title } = Typography;

export const References: React.FC = () => {
  return (
    <div>
      <div className="page-header">
        <Title level={2}>Справочники</Title>
        <p>Управление справочными данными</p>
      </div>
      <Card className="content-card">
        <p>Справочники в разработке...</p>
      </Card>
    </div>
  );
};