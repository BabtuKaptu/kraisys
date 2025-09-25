import React, { useState } from 'react';
import { Layout, Menu, Typography, Button } from 'antd';
import {
  DashboardOutlined,
  ShopOutlined,
  InboxOutlined,
  BankOutlined,
  BuildOutlined,
  BookOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

interface SimpleLayoutProps {
  children: React.ReactNode;
}

export const SimpleLayout: React.FC<SimpleLayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);

  const menuItems = [
    {
      key: '1',
      icon: <DashboardOutlined />,
      label: 'Дашборд',
    },
    {
      key: '2',
      icon: <ShopOutlined />,
      label: 'Модели',
    },
    {
      key: '3',
      icon: <InboxOutlined />,
      label: 'Материалы',
    },
    {
      key: '4',
      icon: <BankOutlined />,
      label: 'Склад',
    },
    {
      key: '5',
      icon: <BuildOutlined />,
      label: 'Производство',
    },
    {
      key: '6',
      icon: <BookOutlined />,
      label: 'Справочники',
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        style={{
          background: '#fff',
        }}
      >
        <div style={{
          padding: '16px',
          textAlign: 'center',
          borderBottom: '1px solid #f0f0f0'
        }}>
          {!collapsed ? (
            <Title level={4} style={{ margin: 0, color: '#2196F3' }}>
              👟 KRAI v0.6
            </Title>
          ) : (
            <Title level={4} style={{ margin: 0, color: '#2196F3' }}>
              👟
            </Title>
          )}
        </div>
        <Menu
          mode="inline"
          defaultSelectedKeys={['1']}
          items={menuItems}
          style={{ border: 'none' }}
        />
      </Sider>
      <Layout>
        <Header style={{
          padding: '0 24px',
          background: '#fff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          boxShadow: '0 2px 8px rgba(0,0,0,0.06)'
        }}>
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{
              fontSize: '16px',
              width: 64,
              height: 64,
            }}
          />
          <div>
            <span style={{ color: '#666' }}>Производственная система KRAI</span>
          </div>
        </Header>
        <Content style={{
          padding: '24px',
          background: '#fafafa',
          overflow: 'auto'
        }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  );
};