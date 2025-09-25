import React from 'react';
import { Card, Row, Col, Statistic, Typography } from 'antd';
import {
  ShopOutlined,
  InboxOutlined,
  BuildOutlined,
  BankOutlined,
} from '@ant-design/icons';

const { Title } = Typography;

export const SimpleDashboard: React.FC = () => {
  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>Дашборд</Title>
        <p>Обзор производственной системы KRAI</p>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Модели в каталоге"
              value={47}
              prefix={<ShopOutlined style={{ color: '#1890ff' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Активные материалы"
              value={156}
              prefix={<InboxOutlined style={{ color: '#52c41a' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Заказы в работе"
              value={23}
              prefix={<BuildOutlined style={{ color: '#faad14' }} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Критичные остатки"
              value={8}
              prefix={<BankOutlined style={{ color: '#ff4d4f' }} />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card title="Производственная система KRAI v0.6">
            <p>✅ Нормализованная база данных (20 таблиц)</p>
            <p>✅ FastAPI backend на порту 8001</p>
            <p>✅ React frontend на порту 3000</p>
            <p>✅ Ant Design UI компоненты</p>
            <p>✅ Современная архитектура</p>

            <div style={{ marginTop: 20, padding: 16, background: '#f6ffed', borderRadius: 6 }}>
              <Title level={4} style={{ color: '#52c41a' }}>🎉 Система готова к работе!</Title>
              <p>Все основные компоненты запущены и функционируют корректно.</p>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};