import React, { useMemo, useState } from 'react';
import {
  Button,
  Card,
  Dropdown,
  Input,
  message,
  Popconfirm,
  Select,
  Space,
  Table,
  Tag,
  MenuProps,
} from 'antd';
import { ColumnsType } from 'antd/es/table';
import {
  DeleteOutlined,
  EditOutlined,
  PlusOutlined,
  EyeOutlined,
  MoreOutlined,
} from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Material,
  MaterialDraft,
  MaterialGroup,
  MaterialsListItem,
  MaterialsListQuery,
  UnitOfMeasure,
} from '../types';
import { materialsApi } from '../services/materialsApi';
import { MaterialKpiCards } from '../components/materials/MaterialKpiCards';
import { MaterialDrawer } from '../components/materials/MaterialDrawer';

const { Search } = Input;

const materialGroupOptions: { label: string; value: MaterialGroup }[] = [
  { label: 'Кожа', value: 'LEATHER' },
  { label: 'Подошва', value: 'SOLE' },
  { label: 'Фурнитура', value: 'HARDWARE' },
  { label: 'Подкладка', value: 'LINING' },
  { label: 'Химия', value: 'CHEMICAL' },
  { label: 'Упаковка', value: 'PACKAGING' },
  { label: 'Текстиль', value: 'TEXTILE' },
  { label: 'Прочее', value: 'OTHER' },
];

const Materials: React.FC = () => {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState<MaterialsListQuery>({ page: 1, pageSize: 10 });
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerLoading, setDrawerLoading] = useState(false);
  const [activeMaterial, setActiveMaterial] = useState<Material | null>(null);

  const { data = { items: [], total: 0, page: filters.page ?? 1, pageSize: filters.pageSize ?? 10 }, isPending } =
    useQuery({
      queryKey: ['materials', 'list', filters],
      queryFn: () => materialsApi.list(filters),
      placeholderData: (previousData) => previousData ?? {
        items: [],
        total: 0,
        page: filters.page ?? 1,
        pageSize: filters.pageSize ?? 10,
      },
    });

  const createMutation = useMutation({
    mutationFn: (draft: MaterialDraft) => materialsApi.create(draft),
    onSuccess: async () => {
      message.success('Материал создан');
      await queryClient.invalidateQueries({ queryKey: ['materials', 'list'] });
      setDrawerOpen(false);
      setActiveMaterial(null);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, draft }: { id: string; draft: MaterialDraft }) =>
      materialsApi.update(id, draft),
    onSuccess: async (updated) => {
      if (updated) {
        setActiveMaterial(updated);
        message.success('Материал обновлён');
      }
      await queryClient.invalidateQueries({ queryKey: ['materials', 'list'] });
      setDrawerOpen(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => materialsApi.remove(id),
    onSuccess: async () => {
      message.success('Материал удалён');
      await queryClient.invalidateQueries({ queryKey: ['materials', 'list'] });
    },
  });

  const loadMaterial = async (id: string) => {
    setDrawerLoading(true);
    try {
      const material = await materialsApi.getById(id);
      if (!material) {
        message.error('Не удалось загрузить материал');
        return null;
      }
      setActiveMaterial(material);
      return material;
    } finally {
      setDrawerLoading(false);
    }
  };

  const handleCreate = () => {
    setActiveMaterial(null);
    setDrawerOpen(true);
  };

  const handleEdit = async (id: string) => {
    const loaded = await loadMaterial(id);
    if (loaded) {
      setDrawerOpen(true);
    }
  };

  const handleDrawerSubmit = async (draft: MaterialDraft, context: { materialId?: string }) => {
    if (context.materialId) {
      await updateMutation.mutateAsync({ id: context.materialId, draft });
    } else {
      await createMutation.mutateAsync(draft);
    }
  };

  const columns: ColumnsType<MaterialsListItem> = useMemo(
    () => [
      {
        title: 'Код',
        dataIndex: 'code',
        key: 'code',
        width: 140,
      },
      {
        title: 'Название',
        dataIndex: 'name',
        key: 'name',
      },
      {
        title: 'Группа',
        dataIndex: 'group',
        key: 'group',
        width: 150,
      },
      {
        title: 'Ед. изм.',
        dataIndex: 'unit',
        key: 'unit',
        width: 110,
        render: (unit: UnitOfMeasure) => <Tag>{unit}</Tag>,
      },
      {
        title: 'Поставщик',
        dataIndex: 'supplierName',
        key: 'supplier',
        width: 200,
        render: (value: string | undefined) => value ?? '—',
      },
      {
        title: 'Статус',
        dataIndex: 'isActive',
        key: 'status',
        width: 120,
        render: (isActive: boolean) => (
          <Tag color={isActive ? 'green' : 'red'}>{isActive ? 'Активен' : 'Архив'}</Tag>
        ),
      },
      {
        title: 'Критичность',
        dataIndex: 'isCritical',
        key: 'critical',
        width: 140,
        render: (isCritical: boolean | undefined) =>
          isCritical ? <Tag color="volcano">Критичный</Tag> : '—',
      },
      {
        title: 'Действия',
        key: 'actions',
        width: 80,
        fixed: 'right',
        render: (_, record) => {
          const menuItems: MenuProps['items'] = [
            {
              key: 'view',
              label: 'Просмотр',
              icon: <EyeOutlined />,
              onClick: () => handleEdit(record.id),
            },
            {
              key: 'edit',
              label: 'Редактировать',
              icon: <EditOutlined />,
              onClick: () => handleEdit(record.id),
            },
            {
              type: 'divider',
            },
            {
              key: 'delete',
              label: 'Удалить',
              icon: <DeleteOutlined />,
              danger: true,
              onClick: () => {
                window.confirm('Удалить материал? Это действие нельзя отменить') &&
                  deleteMutation.mutateAsync(record.id);
              },
            },
          ];

          return (
            <Dropdown menu={{ items: menuItems }} trigger={['click']} placement="bottomRight">
              <Button type="text" icon={<MoreOutlined />} />
            </Dropdown>
          );
        },
      },
    ],
    [deleteMutation],
  );

  const resetFilters = () => {
    setFilters({ page: 1, pageSize: filters.pageSize ?? 10 });
  };

  return (
    <div>
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <Space style={{ width: '100%', justifyContent: 'space-between' }} align="center">
          <div>
            <h2 style={{ marginBottom: 4 }}>Материалы</h2>
            <p style={{ margin: 0, color: '#666' }}>Справочник материалов и комплектующих</p>
          </div>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            Добавить материал
          </Button>
        </Space>

        <MaterialKpiCards materials={data.items} />

        <Card className="content-card" bodyStyle={{ paddingBottom: 0 }}>
          <Space wrap style={{ width: '100%' }} size={[16, 16]}>
            <Search
              allowClear
              placeholder="Поиск по коду или названию"
              onSearch={(value) => setFilters((prev) => ({ ...prev, search: value, page: 1 }))}
              style={{ width: 280 }}
            />
            <Select
              allowClear
              placeholder="Группа"
              style={{ width: 200 }}
              options={materialGroupOptions}
              value={filters.group}
              onChange={(value) => setFilters((prev) => ({ ...prev, group: value as MaterialGroup | undefined, page: 1 }))}
            />
            <Search
              allowClear
              placeholder="Подгруппа"
              onSearch={(value) => setFilters((prev) => ({ ...prev, subgroup: value || undefined, page: 1 }))}
              style={{ width: 200 }}
            />
            <Select
              allowClear
              placeholder="Статус"
              style={{ width: 160 }}
              options={[
                { label: 'Активные', value: true },
                { label: 'Архив', value: false },
              ]}
              value={filters.isActive}
              onChange={(value) => setFilters((prev) => ({ ...prev, isActive: value as boolean | undefined, page: 1 }))}
            />
            <Select
              allowClear
              placeholder="Критичные"
              style={{ width: 160 }}
              options={[
                { label: 'Критичные', value: true },
                { label: 'Обычные', value: false },
              ]}
              value={filters.isCritical}
              onChange={(value) => setFilters((prev) => ({ ...prev, isCritical: value as boolean | undefined, page: 1 }))}
            />
            <Button onClick={resetFilters}>Сбросить</Button>
          </Space>
        </Card>

        <Card className="content-card">
          <Table<MaterialsListItem>
            loading={isPending || deleteMutation.isPending}
            dataSource={data.items}
            columns={columns}
            rowKey="id"
            scroll={{ x: 1000 }}
            pagination={{
              current: filters.page,
              pageSize: filters.pageSize,
              total: data.total,
              showSizeChanger: true,
              onChange: (page, pageSize) =>
                setFilters((prev) => ({ ...prev, page, pageSize: pageSize ?? prev.pageSize })),
              showTotal: (total, range) => `${range[0]}-${range[1]} из ${total}`,
            }}
          />
        </Card>
      </Space>

      <MaterialDrawer
        open={drawerOpen}
        loading={drawerLoading || createMutation.isPending || updateMutation.isPending}
        material={activeMaterial}
        onClose={() => {
          setDrawerOpen(false);
          setActiveMaterial(null);
        }}
        onSubmit={handleDrawerSubmit}
      />
    </div>
  );
};

export default Materials;
export { Materials };
