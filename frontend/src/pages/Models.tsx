import React from 'react';
import { Card, Typography, Button, Table, Space, Tag } from 'antd';
import { PlusOutlined, EditOutlined, EyeOutlined } from '@ant-design/icons';

const { Title } = Typography;

export const Models: React.FC = () => {
  // Mock data
  const models = [
    {
      key: '1',
      article: '250',
      name: 'SPORT',
      category: 'Спортивная',
      gender: 'Мужская',
      sizeRange: '40-46',
      price: 4500,
      status: 'active',
    },
    {
      key: '2',
      article: '450',
      name: 'BRUNO',
      category: 'Повседневная',
      gender: 'Мужская',
      sizeRange: '39-45',
      price: 5200,
      status: 'active',
    },
    {
      key: '3',
      article: '500',
      name: 'BETA',
      category: 'Ботинки',
      gender: 'Женская',
      sizeRange: '36-42',
      price: 6800,
      status: 'inactive',
    },
  ];

  const columns = [
    {
      title: 'Артикул',
      dataIndex: 'article',
      key: 'article',
      width: 100,
    },
    {
      title: 'Название',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Категория',
      dataIndex: 'category',
      key: 'category',
    },
    {
      title: 'Пол',
      dataIndex: 'gender',
      key: 'gender',
    },
    {
      title: 'Размерный ряд',
      dataIndex: 'sizeRange',
      key: 'sizeRange',
    },
    {
      title: 'Цена',
      dataIndex: 'price',
      key: 'price',
      render: (price: number) => `${price.toLocaleString()} ₽`,
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'active' ? 'green' : 'red'}>
          {status === 'active' ? 'Активная' : 'Неактивная'}
        </Tag>
      ),
    },
    {
      title: 'Действия',
      key: 'actions',
      render: () => (
        <Space>
          <Button type="text" icon={<EyeOutlined />} size="small" />
          <Button type="text" icon={<EditOutlined />} size="small" />
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div className="page-header">
        <Title level={2}>Модели обуви</Title>
        <p>Управление каталогом моделей</p>
      </div>

      <div className="toolbar">
        <div>
          <Button type="primary" icon={<PlusOutlined />}>
            Добавить модель
          </Button>
        </div>
      </div>

      <Card className="content-card">
        <Table
          dataSource={models}
          columns={columns}
          pagination={{
            total: models.length,
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `Всего моделей: ${total}`,
          }}
        />
      </Card>
    </div>
  );
};