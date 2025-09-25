import React, { useMemo, useState } from 'react';
import { Button, Card, Input, message, Select, Space, Statistic, Table, Tag } from 'antd';
import { ColumnsType } from 'antd/es/table';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { WarehouseListQuery, WarehouseStockListItem, WarehouseReceiptDraft, WarehouseIssueDraft } from '../types';
import { warehouseApi } from '../services/warehouseApi';
import { ReceiptDialog, IssueDialog, InventoryDialog } from '../components/warehouse/WarehouseDialogs';

const { Search } = Input;

const statusOptions = [
  { label: 'Все статусы', value: undefined },
  { label: 'OK', value: 'OK' },
  { label: 'Низкий остаток', value: 'LOW' },
  { label: 'Критичный', value: 'CRITICAL' },
];

const warehouseFilterOptions = [
  { label: 'Все склады', value: undefined },
  { label: 'WH_MAIN', value: 'WH_MAIN' },
  { label: 'WH_PRODUCTION', value: 'WH_PRODUCTION' },
  { label: 'WH_FINISHED', value: 'WH_FINISHED' },
];

const Warehouse: React.FC = () => {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState<WarehouseListQuery>({ page: 1, pageSize: 15 });
  const [receiptOpen, setReceiptOpen] = useState(false);
  const [issueOpen, setIssueOpen] = useState(false);
  const [inventoryOpen, setInventoryOpen] = useState(false);

  const { data = { items: [], total: 0, page: filters.page ?? 1, pageSize: filters.pageSize ?? 15 }, isPending } =
    useQuery({
      queryKey: ['warehouse', 'list', filters],
      queryFn: () => warehouseApi.list(filters),
      placeholderData: (prev) =>
        prev ?? { items: [], total: 0, page: filters.page ?? 1, pageSize: filters.pageSize ?? 15 },
    });

  const receiptMutation = useMutation({
    mutationFn: async (draft: WarehouseReceiptDraft) => {
      await warehouseApi.receipt(draft);
    },
    onSuccess: async () => {
      message.success('Приход зарегистрирован');
      await queryClient.invalidateQueries({ queryKey: ['warehouse', 'list'] });
      setReceiptOpen(false);
    },
    onError: (error: unknown) => {
      console.error('Receipt error:', error);
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as any;
        console.error('Response data:', axiosError.response?.data);
        if (axiosError.response?.data?.detail) {
          console.error('Validation errors:', JSON.stringify(axiosError.response.data.detail, null, 2));
        }
      }
      message.error((error as Error).message ?? 'Ошибка при создании прихода');
    },
  });

  const issueMutation = useMutation({
    mutationFn: async (draft: WarehouseIssueDraft) => {
      await warehouseApi.issue(draft);
    },
    onSuccess: async () => {
      message.success('Списание выполнено');
      await queryClient.invalidateQueries({ queryKey: ['warehouse', 'list'] });
      setIssueOpen(false);
    },
    onError: (error: unknown) => {
      message.warning((error as Error).message ?? 'API для списания пока недоступно');
    },
  });

  const stats = useMemo(() => {
    const items = data.items;
    const totalPositions = items.length;
    const totalValue = items.reduce((acc, stock) => acc + (stock.totalValue ?? 0), 0);
    const critical = items.filter((stock) => stock.status === 'CRITICAL').length;
    return { totalPositions, totalValue, critical };
  }, [data]);

  const columns: ColumnsType<WarehouseStockListItem> = [
    {
      title: 'Материал',
      dataIndex: ['material', 'name'],
      key: 'materialName',
      render: (_, record) => (
        <div>
          <div style={{ fontWeight: 500 }}>{record.material.name}</div>
          <div style={{ color: '#888' }}>{record.material.code}</div>
        </div>
      ),
    },
    {
      title: 'Партия',
      dataIndex: 'batchNumber',
      key: 'batchNumber',
      width: 140,
      render: (value: string | undefined) => value ?? '—',
    },
    {
      title: 'Количество',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 140,
      render: (_, record) => (
        <div>
          <div>{record.quantity} {record.unit}</div>
          <div style={{ color: '#888' }}>Доступно: {record.availableQuantity}</div>
        </div>
      ),
    },
    {
      title: 'Резерв',
      dataIndex: 'reservedQuantity',
      key: 'reservedQuantity',
      width: 120,
    },
    {
      title: 'Цена закупки',
      dataIndex: 'purchasePrice',
      key: 'purchasePrice',
      width: 140,
      render: (value: number | undefined) => (value ? `₽ ${value}` : '—'),
    },
    {
      title: 'Стоимость партии',
      dataIndex: 'totalValue',
      key: 'totalValue',
      width: 160,
      render: (value: number | undefined) => (value ? `₽ ${value.toLocaleString()}` : '—'),
    },
    {
      title: 'Склад / место',
      dataIndex: 'warehouseCode',
      key: 'warehouseCode',
      width: 180,
      render: (_, record) => (
        <div>
          <div>{record.warehouseCode}</div>
          <div style={{ color: '#888' }}>{record.location ?? '—'}</div>
        </div>
      ),
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: WarehouseStockListItem['status']) => {
        const colors: Record<WarehouseStockListItem['status'], string> = {
          OK: 'green',
          LOW: 'orange',
          CRITICAL: 'red',
        };
        const labels: Record<WarehouseStockListItem['status'], string> = {
          OK: 'OK',
          LOW: 'Низкий',
          CRITICAL: 'Критичный',
        };
        return <Tag color={colors[status]}>{labels[status]}</Tag>;
      },
    },
    {
      title: 'Даты',
      key: 'dates',
      width: 200,
      render: (_, record) => (
        <div style={{ color: '#888' }}>
          <div>Приход: {record.receiptDate ?? '—'}</div>
          <div>Выдача: {record.lastIssueDate ?? '—'}</div>
        </div>
      ),
    },
  ];

  return (
    <div>
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <div>
          <h2 style={{ marginBottom: 4 }}>Склад</h2>
          <p style={{ margin: 0, color: '#666' }}>Учёт движения материалов и партий</p>
        </div>

        <Space style={{ width: '100%' }} wrap>
          <Card className="content-card" style={{ flex: 1 }}>
            <Statistic title="Позиции" value={stats.totalPositions} />
          </Card>
          <Card className="content-card" style={{ flex: 1 }}>
            <Statistic title="Общая стоимость" value={`₽ ${stats.totalValue.toLocaleString()}`} />
          </Card>
          <Card className="content-card" style={{ flex: 1 }}>
            <Statistic title="Критичные" value={stats.critical} valueStyle={{ color: '#ff4d4f' }} />
          </Card>
        </Space>

        <Card className="content-card" bodyStyle={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          <Button type="primary" onClick={() => setReceiptOpen(true)}>
            Приход материалов
          </Button>
          <Button onClick={() => setIssueOpen(true)}>Списание / расход</Button>
          <Button onClick={() => setInventoryOpen(true)}>Инвентаризация</Button>
        </Card>

        <Card className="content-card" bodyStyle={{ paddingBottom: 0 }}>
          <Space wrap style={{ width: '100%' }} size={[16, 16]}>
            <Search
              allowClear
              placeholder="Поиск по коду или названию"
              style={{ width: 280 }}
              onSearch={(value) => setFilters((prev) => ({ ...prev, search: value, page: 1 }))}
            />
            <Select
              allowClear
              placeholder="Склад"
              options={warehouseFilterOptions}
              style={{ width: 200 }}
              value={filters.warehouseCode}
              onChange={(value) =>
                setFilters((prev) => ({
                  ...prev,
                  warehouseCode: value as string | undefined,
                  page: 1,
                }))
              }
            />
            <Select
              allowClear
              placeholder="Статус"
              options={statusOptions}
              style={{ width: 200 }}
              value={filters.status}
              onChange={(value) =>
                setFilters((prev) => ({
                  ...prev,
                  status: value as WarehouseStockListItem['status'] | undefined,
                  page: 1,
                }))
              }
            />
          </Space>
        </Card>

        <Card className="content-card">
          <Table<WarehouseStockListItem>
            loading={isPending}
            dataSource={data.items}
            columns={columns}
            rowKey="id"
            pagination={{
              current: filters.page,
              pageSize: filters.pageSize,
              total: data.total,
              onChange: (page, pageSize) =>
                setFilters((prev) => ({ ...prev, page, pageSize: pageSize ?? prev.pageSize })),
            }}
          />
        </Card>
      </Space>

      <ReceiptDialog
        open={receiptOpen}
        submitting={receiptMutation.isPending}
        onClose={() => setReceiptOpen(false)}
        onSubmit={(draft) => receiptMutation.mutateAsync(draft)}
      />

      <IssueDialog
        open={issueOpen}
        submitting={issueMutation.isPending}
        onClose={() => setIssueOpen(false)}
        stockOptions={(data?.items ?? []).map((stock) => ({
          value: stock.id,
          label: `${stock.material.code} · ${stock.material.name} (${stock.availableQuantity} ${stock.unit})`,
        }))}
        onSubmit={(draft) => issueMutation.mutateAsync(draft)}
      />

      <InventoryDialog open={inventoryOpen} onClose={() => setInventoryOpen(false)} />
    </div>
  );
};

export default Warehouse;
export { Warehouse };
