import React, { useMemo, useState } from 'react';
import { Button, Card, Dropdown, List, message, Space, Table, Tag, MenuProps } from 'antd';
import { EditOutlined, DeleteOutlined, MoreOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { ReferenceDraft, ReferenceItem, ReferenceListResult } from '../types';
import { referenceApi } from '../services/referenceApi';
import ReferenceDrawer from '../components/references/ReferenceDrawer';

const referenceGroups: { id: string; title: string; description: string }[] = [
  { id: 'perforation_type', title: 'Типы перфорации', description: 'Варианты перфорации для SUPER-BOM' },
  { id: 'lining_type', title: 'Типы подкладки', description: 'Материалы и варианты подкладки' },
  { id: 'cutting_part', title: 'Детали кроя', description: 'Справочник деталей верха' },
  { id: 'lasting_type', title: 'Типы затяжки', description: 'Технологии затяжки' },
];

const References: React.FC = () => {
  const [activeType, setActiveType] = useState(referenceGroups[0].id);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<ReferenceItem | null>(null);

  const {
    data = { items: [], total: 0, page: 1, pageSize: 50 } as ReferenceListResult,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ['references', activeType],
    queryFn: () => referenceApi.list({ type: activeType }),
  });

  const columns = useMemo(() => {
    return [
      {
        title: 'Код',
        dataIndex: 'code',
        key: 'code',
        width: 120,
        render: (value: string | undefined) => value ?? '—',
      },
      {
        title: 'Название',
        dataIndex: 'name',
        key: 'name',
      },
      {
        title: 'Описание',
        dataIndex: 'description',
        key: 'description',
        render: (value: string | undefined) => value ?? '—',
      },
      {
        title: 'Статус',
        dataIndex: 'isActive',
        key: 'isActive',
        width: 120,
        render: (isActive: boolean) => <Tag color={isActive ? 'green' : 'red'}>{isActive ? 'Активен' : 'Скрыт'}</Tag>,
      },
      {
        title: 'Действия',
        key: 'actions',
        width: 80,
        fixed: 'right',
        render: (_: unknown, record: ReferenceItem) => {
          const menuItems: MenuProps['items'] = [
            {
              key: 'edit',
              label: 'Редактировать',
              icon: <EditOutlined />,
              onClick: () => handleEdit(record),
            },
            {
              type: 'divider',
            },
            {
              key: 'delete',
              label: 'Удалить',
              icon: <DeleteOutlined />,
              danger: true,
              onClick: () => handleDelete(record),
            },
          ];

          return (
            <Dropdown menu={{ items: menuItems }} trigger={['click']} placement="bottomRight">
              <Button type="text" icon={<MoreOutlined />} />
            </Dropdown>
          );
        },
      },
    ];
  }, []);  // Remove activeType dependency

  const handleEdit = (item: ReferenceItem) => {
    setEditingItem(item);
    setDrawerOpen(true);
  };

  const handleDelete = (item: ReferenceItem) => {
    message.info(`Удаление справочника пока не реализовано (id: ${item.id})`);
  };

  const handleDrawerSubmit = (_draft: ReferenceDraft) => {
    message.success('Изменения будут сохранены после интеграции с API');
    setDrawerOpen(false);
    setEditingItem(null);
    refetch();
  };

  return (
    <div style={{ display: 'flex', gap: 16 }}>
      <Card style={{ width: 260 }} bodyStyle={{ padding: 0 }} className="content-card">
        <List
          dataSource={referenceGroups}
          renderItem={(item) => (
            <List.Item
              key={item.id}
              style={{
                cursor: 'pointer',
                background: item.id === activeType ? '#f5f5f5' : undefined,
                padding: '16px 20px',
              }}
              onClick={() => setActiveType(item.id)}
            >
              <List.Item.Meta
                title={<strong>{item.title}</strong>}
                description={<span style={{ color: '#888' }}>{item.description}</span>}
              />
            </List.Item>
          )}
        />
      </Card>

      <div style={{ flex: 1 }}>
        <Space style={{ width: '100%', marginBottom: 16, justifyContent: 'space-between' }}>
          <div>
            <h2 style={{ marginBottom: 4 }}>{referenceGroups.find((ref) => ref.id === activeType)?.title}</h2>
            <p style={{ margin: 0, color: '#666' }}>Управление значениями для форм и SUPER-BOM</p>
          </div>
          <Button type="primary" onClick={() => setDrawerOpen(true)}>
            Добавить элемент
          </Button>
        </Space>

        <Card className="content-card">
          <Table<ReferenceItem>
            loading={isLoading}
            dataSource={data.items}
            columns={columns}
            rowKey="id"
            scroll={{ x: 800 }}
            pagination={false}
          />
        </Card>
      </div>

      <ReferenceDrawer
        open={drawerOpen}
        type={activeType}
        initialValues={editingItem ?? undefined}
        onClose={() => {
          setDrawerOpen(false);
          setEditingItem(null);
        }}
        onSubmit={handleDrawerSubmit}
      />
    </div>
  );
};

export default References;
export { References };
