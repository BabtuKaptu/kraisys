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
  SettingOutlined,
  MoreOutlined,
} from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Gender,
  Model,
  ModelDraft,
  ModelListItem,
  ModelType,
  ModelsListQuery,
  ModelCategory,
} from '../types';
import { modelsApi } from '../services/modelsApi';
import { ModelKpiCards } from '../components/models/ModelKpiCards';
import { ModelDrawer } from '../components/models/ModelDrawer';
import { ModelVariantsManager } from '../components/models/ModelVariantsManager';

const { Search } = Input;

const genderFilterOptions: { label: string; value: Gender }[] = [
  { label: 'Мужской', value: 'MALE' },
  { label: 'Женский', value: 'FEMALE' },
  { label: 'Унисекс', value: 'UNISEX' },
  { label: 'Детский', value: 'KIDS' },
];

const statusOptions = [
  { label: 'Активные', value: 'ACTIVE' },
  { label: 'Архив', value: 'INACTIVE' },
];

const modelTypeOptions: { label: string; value: ModelType }[] = [
  { label: 'Sport', value: 'SPORT' },
  { label: 'Casual', value: 'CASUAL' },
  { label: 'Formal', value: 'FORMAL' },
  { label: 'Work', value: 'WORK' },
  { label: 'Outdoor', value: 'OUTDOOR' },
  { label: 'Special', value: 'SPECIAL' },
];

const categoryOptions: { label: string; value: ModelCategory }[] = [
  { label: 'Кроссовки', value: 'SNEAKERS' },
  { label: 'Туфли', value: 'SHOES' },
  { label: 'Ботинки', value: 'BOOTS' },
  { label: 'Сандалии', value: 'SANDALS' },
  { label: 'Тапочки', value: 'SLIPPERS' },
  { label: 'Лоферы', value: 'LOAFERS' },
  { label: 'Оксфорды', value: 'OXFORDS' },
  { label: 'Дерби', value: 'DERBY' },
  { label: 'Другое', value: 'OTHER' },
];

const Models: React.FC = () => {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState<ModelsListQuery>({ page: 1, pageSize: 10 });
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerLoading, setDrawerLoading] = useState(false);
  const [activeModel, setActiveModel] = useState<Model | null>(null);
  const [variantsOpen, setVariantsOpen] = useState(false);
  const [variantModel, setVariantModel] = useState<Model | null>(null);

  const { data = { items: [], total: 0, page: filters.page ?? 1, pageSize: filters.pageSize ?? 10 }, isPending } =
    useQuery({
      queryKey: ['models', 'list', filters],
      queryFn: () => modelsApi.list(filters),
      placeholderData: (previousData) =>
        previousData ?? {
          items: [],
          total: 0,
          page: filters.page ?? 1,
          pageSize: filters.pageSize ?? 10,
        },
    });

  const createMutation = useMutation({
    mutationFn: (draft: ModelDraft) => modelsApi.create(draft),
    onSuccess: async () => {
      message.success('Модель создана');
      await queryClient.invalidateQueries({ queryKey: ['models', 'list'] });
      setDrawerOpen(false);
      setActiveModel(null);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, draft }: { id: string; draft: ModelDraft }) =>
      modelsApi.update(id, draft),
    onSuccess: async (updated) => {
      if (updated) {
        message.success('Модель обновлена');
        setActiveModel(updated);
      }
      await queryClient.invalidateQueries({ queryKey: ['models', 'list'] });
      setDrawerOpen(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => modelsApi.remove(id),
    onSuccess: async () => {
      message.success('Модель удалена');
      await queryClient.invalidateQueries({ queryKey: ['models', 'list'] });
    },
  });

  const loadModel = async (id: string) => {
    setDrawerLoading(true);
    try {
      const model = await modelsApi.getById(id);
      if (model) {
        setActiveModel(model);
        return model;
      }
      message.error('Не удалось загрузить модель');
      return null;
    } finally {
      setDrawerLoading(false);
    }
  };

  const handleCreate = () => {
    setActiveModel(null);
    setDrawerOpen(true);
  };

  const handleEdit = async (id: string) => {
    const loaded = await loadModel(id);
    if (loaded) {
      setDrawerOpen(true);
    }
  };

  const handleManageVariants = async (id: string) => {
    const loaded = await loadModel(id);
    if (loaded) {
      setVariantModel(loaded);
      setVariantsOpen(true);
    }
  };

  const handleDrawerSubmit = async (draft: ModelDraft, context: { modelId?: string }) => {
    if (context.modelId) {
      await updateMutation.mutateAsync({ id: context.modelId, draft });
    } else {
      await createMutation.mutateAsync(draft);
    }
  };

  const columns: ColumnsType<ModelListItem> = useMemo(
    () => [
      {
        title: 'Артикул',
        dataIndex: 'article',
        key: 'article',
        width: 110,
      },
      {
        title: 'Название',
        dataIndex: 'name',
        key: 'name',
      },
      {
        title: 'Пол',
        dataIndex: 'gender',
        key: 'gender',
        width: 120,
        render: (gender: Gender) => {
          if (!gender) return null;
          const map: Record<Gender, { label: string; color: string }> = {
            MALE: { label: 'Муж.', color: 'blue' },
            FEMALE: { label: 'Жен.', color: 'magenta' },
            UNISEX: { label: 'Унисекс', color: 'geekblue' },
            KIDS: { label: 'Детская', color: 'cyan' },
          };
          const { label, color } = map[gender];
          return <Tag color={color}>{label}</Tag>;
        },
      },
      {
        title: 'Категория',
        dataIndex: 'category',
        key: 'category',
        width: 140,
      },
      {
        title: 'Размеры',
        dataIndex: 'sizeRange',
        key: 'sizeRange',
        width: 120,
      },
      {
        title: 'Подошва по умолчанию',
        dataIndex: 'defaultSole',
        key: 'defaultSole',
        render: (value: string | undefined) => value ?? '—',
      },
      {
        title: 'Статус',
        dataIndex: 'status',
        key: 'status',
        width: 120,
        render: (status: 'ACTIVE' | 'INACTIVE') => (
          <Tag color={status === 'ACTIVE' ? 'green' : 'red'}>{status === 'ACTIVE' ? 'Активна' : 'Архив'}</Tag>
        ),
      },
      {
        title: 'Действия',
        key: 'actions',
        width: 80,
        fixed: 'right',
        render: (_, record) => {
          const menuItems: MenuProps['items'] = [
            {
              key: 'edit',
              label: 'Редактировать',
              icon: <EditOutlined />,
              onClick: () => handleEdit(record.id),
            },
            {
              key: 'variants',
              label: 'Варианты',
              icon: <SettingOutlined />,
              onClick: () => handleManageVariants(record.id),
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
                // Показываем Popconfirm через message
                window.confirm('Удалить модель? Это действие нельзя отменить') &&
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

  const handleTableChange = (page: number, pageSize?: number) => {
    setFilters((prev) => ({
      ...prev,
      page,
      pageSize: pageSize ?? prev.pageSize,
    }));
  };

  const resetFilters = () => {
    setFilters({ page: 1, pageSize: filters.pageSize ?? 10 });
  };

  return (
    <div>
      <Space style={{ width: '100%', marginBottom: 16 }} direction="vertical" size="large">
        <Space style={{ justifyContent: 'space-between', width: '100%' }} align="center">
          <div>
            <h2 style={{ marginBottom: 4 }}>Модели обуви</h2>
            <p style={{ margin: 0, color: '#666' }}>Управление модельным рядом и вариантами (SUPER-BOM)</p>
          </div>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            Добавить модель
          </Button>
        </Space>

        <ModelKpiCards models={data.items} />

        <Card className="content-card" bodyStyle={{ paddingBottom: 0 }}>
          <Space wrap style={{ width: '100%' }} size={[16, 16]}>
            <Search
              allowClear
              placeholder="Поиск по названию или артикулу"
              onSearch={(value) => setFilters((prev) => ({ ...prev, search: value, page: 1 }))}
              style={{ width: 280 }}
            />
            <Select
              allowClear
              placeholder="Пол"
              options={genderFilterOptions}
              value={filters.gender}
              style={{ width: 160 }}
              onChange={(value) => setFilters((prev) => ({ ...prev, gender: value as Gender | undefined, page: 1 }))}
            />
            <Select
              allowClear
              placeholder="Тип модели"
              style={{ width: 180 }}
              options={modelTypeOptions}
              value={filters.modelType}
              onChange={(value) => setFilters((prev) => ({ ...prev, modelType: value as ModelType | undefined, page: 1 }))}
            />
            <Select
              allowClear
              placeholder="Категория"
              style={{ width: 200 }}
              options={categoryOptions}
              value={filters.category}
              onChange={(value) => setFilters((prev) => ({ ...prev, category: value as ModelCategory | undefined, page: 1 }))}
            />
            <Select
              allowClear
              placeholder="Статус"
              style={{ width: 160 }}
              options={statusOptions}
              value={filters.status}
              onChange={(value) => setFilters((prev) => ({ ...prev, status: value as 'ACTIVE' | 'INACTIVE' | undefined, page: 1 }))}
            />
            <Button onClick={resetFilters}>Сбросить</Button>
          </Space>
        </Card>

        <Card className="content-card">
          <Table<ModelListItem>
            loading={isPending || deleteMutation.isPending}
            dataSource={data.items}
            columns={columns}
            rowKey="id"
            scroll={{ x: 900 }}
            pagination={{
              current: filters.page,
              pageSize: filters.pageSize,
              total: data.total,
              showSizeChanger: true,
              onChange: handleTableChange,
              onShowSizeChange: handleTableChange,
              showTotal: (total, range) => `${range[0]}-${range[1]} из ${total}`,
            }}
          />
        </Card>
      </Space>

      <ModelDrawer
        open={drawerOpen}
        loading={drawerLoading || createMutation.isPending || updateMutation.isPending}
        model={activeModel ?? undefined}
        onClose={() => {
          setDrawerOpen(false);
          setActiveModel(null);
        }}
        onSubmit={handleDrawerSubmit}
        onManageVariants={(model) => {
          setVariantModel(model);
          setVariantsOpen(true);
        }}
      />

      <ModelVariantsManager
        open={variantsOpen}
        model={variantModel}
        onClose={() => {
          setVariantsOpen(false);
          setVariantModel(null);
        }}
        onUpdated={(updated) => {
          setVariantModel(updated);
          if (activeModel && updated.id === activeModel.id) {
            setActiveModel(updated);
          }
        }}
      />
    </div>
  );
};

export default Models;
export { Models };
