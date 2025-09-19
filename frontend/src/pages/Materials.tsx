import React from 'react';
import { Card, Typography, Button, Table, Space, Tag } from 'antd';
import { PlusOutlined, EditOutlined, EyeOutlined } from '@ant-design/icons';

const { Title } = Typography;

export const Materials: React.FC = () => {
  return (
    <div>
      <div className="page-header">
        <Title level={2}>Материалы</Title>
        <p>Справочник материалов и комплектующих</p>
      </div>
      <Card className="content-card">
        <p>Раздел материалов в разработке...</p>
      </Card>
    </div>
  );
};