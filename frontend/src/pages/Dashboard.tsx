import React from 'react';
import { Card, Row, Col, Statistic, Typography, Progress, Table } from 'antd';
import {
  ShopOutlined,
  InboxOutlined,
  FactoryOutlined,
  WarehouseOutlined,
  TrendingUpOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';

const { Title } = Typography;

export const Dashboard: React.FC = () => {
  // Mock data - в реальном приложении будет загружаться из API
  const stats = {
    totalModels: 47,
    activeMaterials: 156,
    productionOrders: 23,
    lowStockItems: 8,
    dailyCapacity: 150,
    usedCapacity: 120,
  };

  const recentOrders = [
    {
      key: '1',
      orderNumber: 'ORD-2024-001',
      model: 'SPORT 250',
      customer: 'ИП Иванов',
      quantity: 10,
      status: 'В производстве',
      dueDate: '2024-09-25',
    },
    {
      key: '2',
      orderNumber: 'ORD-2024-002',
      model: 'BRUNO 450',
      customer: 'ООО Обувь-Сити',
      quantity: 25,
      status: 'Планирование',
      dueDate: '2024-09-30',
    },
    {
      key: '3',
      orderNumber: 'ORD-2024-003',
      model: 'BETA 500',
      customer: 'Магазин Стиль',
      quantity: 15,
      status: 'Готов',
      dueDate: '2024-09-22',
    },
  ];

  const orderColumns = [
    {
      title: 'Номер заказа',
      dataIndex: 'orderNumber',
      key: 'orderNumber',
    },
    {
      title: 'Модель',
      dataIndex: 'model',
      key: 'model',
    },
    {
      title: 'Заказчик',
      dataIndex: 'customer',
      key: 'customer',
    },
    {
      title: 'Количество',
      dataIndex: 'quantity',
      key: 'quantity',
      render: (qty: number) => `${qty} пар`,
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colors = {
          'В производстве': '#1890ff',
          'Планирование': '#faad14',
          'Готов': '#52c41a',
        };
        return (
          <span style={{ color: colors[status as keyof typeof colors] }}>
            {status}
          </span>
        );
      },
    },
    {
      title: 'Срок',
      dataIndex: 'dueDate',
      key: 'dueDate',
    },
  ];

  return (
    <div>
      <div className="page-header">
        <Title level={2}>Дашборд</Title>
        <p>Обзор производственной системы KRAI</p>
      </div>

      {/* Статистические карточки */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card className="content-card">
            <Statistic
              title="Модели в каталоге"
              value={stats.totalModels}
              prefix={<ShopOutlined style={{ color: '#1890ff' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="content-card">
            <Statistic
              title="Активные материалы"
              value={stats.activeMaterials}
              prefix={<InboxOutlined style={{ color: '#52c41a' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="content-card">
            <Statistic
              title="Заказы в работе"
              value={stats.productionOrders}
              prefix={<FactoryOutlined style={{ color: '#faad14' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card className="content-card">
            <Statistic
              title="Критичные остатки"
              value={stats.lowStockItems}
              prefix={<WarehouseOutlined style={{ color: '#ff4d4f' }} />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* Загрузка производства */}
        <Col xs={24} lg={8}>
          <Card
            className="content-card"
            title={
              <span>
                <TrendingUpOutlined style={{ marginRight: 8 }} />
                Загрузка производства
              </span>
            }
          >
            <div style={{ textAlign: 'center' }}>
              <Progress
                type="circle"
                percent={Math.round((stats.usedCapacity / stats.dailyCapacity) * 100)}
                strokeColor={{
                  '0%': '#108ee9',
                  '100%': '#87d068',
                }}
              />
              <p style={{ marginTop: 16 }}>
                {stats.usedCapacity} из {stats.dailyCapacity} пар/день
              </p>
            </div>
          </Card>
        </Col>

        {/* Последние заказы */}
        <Col xs={24} lg={16}>
          <Card
            className="content-card"
            title={
              <span>
                <ClockCircleOutlined style={{ marginRight: 8 }} />
                Последние заказы
              </span>
            }
          >
            <Table
              dataSource={recentOrders}
              columns={orderColumns}
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};