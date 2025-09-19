import React from 'react';
import { Card, Typography } from 'antd';

const { Title } = Typography;

export const Warehouse: React.FC = () => {
  return (
    <div>
      <div className="page-header">
        <Title level={2}>Склад</Title>
        <p>Управление складскими остатками</p>
      </div>
      <Card className="content-card">
        <p>Складской учёт в разработке...</p>
      </Card>
    </div>
  );
};