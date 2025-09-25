import React, { useCallback, useMemo, useState } from 'react';
import { Button, Form, Input, Modal, Select, Space, Switch, Table, Tag } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Model, ModelVariant, ModelVariantSpecification } from '../../types';
import { modelsApi } from '../../services/modelsApi';

interface ModelVariantsManagerProps {
  open: boolean;
  model: Model | null;
  onClose: () => void;
  onUpdated: (model: Model) => void;
}

interface VariantFormValues {
  id?: string;
  name: string;
  code?: string;
  isDefault?: boolean;
  status?: 'ACTIVE' | 'INACTIVE';
  perforationOptionId?: string;
  insoleOptionId?: string;
  hardwareSetId?: string;
  soleOptionId?: string;
  notes?: string;
}

const defaultValues = (model: Model | null): VariantFormValues => ({
  name: '',
  status: 'ACTIVE',
  isDefault: model ? model.variants.length === 0 : false,
  perforationOptionId: model?.superBom.perforationOptions.find((option) => option.isDefault)?.id,
  insoleOptionId: model?.superBom.insoleOptions.find((option) => option.isDefault)?.id,
  hardwareSetId: model?.superBom.hardwareSets.find((set) => set.isDefault)?.id,
  soleOptionId: model?.soleOptions.find((option) => option.isDefault)?.id,
});

export const ModelVariantsManager: React.FC<ModelVariantsManagerProps> = ({ open, model, onClose, onUpdated }) => {
  const [variantModalOpen, setVariantModalOpen] = useState(false);
  const [editingVariant, setEditingVariant] = useState<ModelVariant | null>(null);
  const [form] = Form.useForm<VariantFormValues>();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async (values: VariantFormValues) => {
      if (!model) {
        throw new Error('Модель не выбрана');
      }
      const specification: ModelVariantSpecification = {
        perforationOptionId: values.perforationOptionId,
        insoleOptionId: values.insoleOptionId,
        hardwareSetId: values.hardwareSetId,
        soleOptionId: values.soleOptionId,
        notes: values.notes,
      };

      const variant: ModelVariant = {
        id: values.id ?? `variant-${Date.now()}`,
        modelId: model.id,
        name: values.name,
        code: values.code,
        isDefault: values.isDefault,
        status: values.status ?? 'ACTIVE',
        specification,
        totalMaterialCost: editingVariant?.totalMaterialCost,
        createdAt: editingVariant?.createdAt ?? new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      const updatedModel = await modelsApi.upsertVariant(model.id, variant);
      if (!updatedModel) {
        throw new Error('Не удалось обновить вариант');
      }
      return updatedModel;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['models', 'list'] });
      onUpdated(data);
      setVariantModalOpen(false);
      setEditingVariant(null);
      form.resetFields();
    },
  });

  const handleAdd = useCallback(() => {
    if (!model) return;
    setEditingVariant(null);
    form.resetFields();
    form.setFieldsValue(defaultValues(model));
    setVariantModalOpen(true);
  }, [form, model]);

  const handleEdit = useCallback(
    (variant: ModelVariant) => {
      if (!model) return;
      setEditingVariant(variant);
      form.setFieldsValue({
        id: variant.id,
        name: variant.name,
        code: variant.code,
        status: variant.status,
        isDefault: variant.isDefault,
        perforationOptionId: variant.specification.perforationOptionId,
        insoleOptionId: variant.specification.insoleOptionId,
        hardwareSetId: variant.specification.hardwareSetId,
        soleOptionId: variant.specification.soleOptionId,
        notes: variant.specification.notes,
      });
      setVariantModalOpen(true);
    },
    [form, model],
  );

  const handleDelete = useCallback(
    async (variant: ModelVariant) => {
      if (!model) return;
      const updated = await modelsApi.deleteVariant(model.id, variant.id);
      if (updated) {
        onUpdated(updated);
        queryClient.invalidateQueries({ queryKey: ['models', 'list'] });
      }
    },
    [model, onUpdated, queryClient],
  );

  const submitVariant = useCallback(async () => {
    const values = await form.validateFields();
    await mutation.mutateAsync(values);
  }, [form, mutation]);

  const columns = useMemo<ColumnsType<ModelVariant>>(
    () => [
      {
        title: 'Название',
        dataIndex: 'name',
        key: 'name',
      },
      {
        title: 'Код',
        dataIndex: 'code',
        key: 'code',
        render: (value: string | undefined) => value ?? '—',
      },
      {
        title: 'Статус',
        dataIndex: 'status',
        key: 'status',
        render: (status: ModelVariant['status']) => (
          <Tag color={status === 'ACTIVE' ? 'blue' : 'red'}>{status === 'ACTIVE' ? 'Активен' : 'Отключен'}</Tag>
        ),
      },
      {
        title: 'По умолчанию',
        dataIndex: 'isDefault',
        key: 'isDefault',
        render: (isDefault: boolean | undefined) => (isDefault ? <Tag color="green">Да</Tag> : '—'),
      },
      {
        title: 'Стоимость материалов',
        dataIndex: 'totalMaterialCost',
        key: 'cost',
        render: (value: number | undefined) => (value ? `₽ ${value}` : '—'),
      },
      {
        title: 'Действия',
        key: 'actions',
        render: (_, record) => (
          <Space>
            <Button type="link" onClick={() => handleEdit(record)}>
              Редактировать
            </Button>
            <Button type="link" danger onClick={() => handleDelete(record)}>
              Удалить
            </Button>
          </Space>
        ),
      },
    ],
    [handleDelete, handleEdit, model],
  );

  return (
    <>
      <Modal
        open={open}
        onCancel={onClose}
        width={900}
        title={model ? `Варианты модели «${model.name}»` : 'Варианты модели'}
        footer={null}
        destroyOnClose
      >
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Button type="primary" onClick={handleAdd} disabled={!model}>
            Добавить вариант
          </Button>
          <Table<ModelVariant>
            dataSource={model?.variants ?? []}
            columns={columns}
            pagination={false}
            rowKey="id"
            locale={{ emptyText: 'Варианты отсутствуют' }}
          />
        </Space>
      </Modal>

      <Modal
        open={variantModalOpen}
        onCancel={() => {
          setVariantModalOpen(false);
          setEditingVariant(null);
          form.resetFields();
        }}
        onOk={submitVariant}
        confirmLoading={mutation.isPending}
        title={editingVariant ? 'Редактирование варианта' : 'Новый вариант'}
        width={640}
        destroyOnClose
      >
        <Form form={form} layout="vertical" initialValues={defaultValues(model)}>
          <Form.Item
            name="name"
            label="Название варианта"
            rules={[{ required: true, message: 'Введите название варианта' }]}
          >
            <Input placeholder="Например: Winter Edition" />
          </Form.Item>
          <Form.Item name="code" label="Код варианта">
            <Input placeholder="Код для учёта" />
          </Form.Item>
          <Form.Item name="status" label="Статус">
            <Select
              options={[
                { value: 'ACTIVE', label: 'Активен' },
                { value: 'INACTIVE', label: 'Отключен' },
              ]}
            />
          </Form.Item>
          <Form.Item name="isDefault" label="Использовать по умолчанию" valuePropName="checked">
            <Switch />
          </Form.Item>

          <Form.Item name="perforationOptionId" label="Перфорация">
            <Select
              allowClear
              options={model?.superBom.perforationOptions.map((option) => ({
                value: option.id,
                label: option.name,
              }))}
              placeholder="Выберите вариант"
            />
          </Form.Item>
          <Form.Item name="insoleOptionId" label="Стелька">
            <Select
              allowClear
              options={model?.superBom.insoleOptions.map((option) => ({
                value: option.id,
                label: option.name,
              }))}
            />
          </Form.Item>
          <Form.Item name="hardwareSetId" label="Фурнитурный набор">
            <Select
              allowClear
              options={model?.superBom.hardwareSets.map((set) => ({
                value: set.id,
                label: set.name,
              }))}
            />
          </Form.Item>
          <Form.Item name="soleOptionId" label="Подошва">
            <Select
              allowClear
              options={model?.soleOptions.map((option) => ({
                value: option.id,
                label: option.name,
              }))}
            />
          </Form.Item>
          <Form.Item name="notes" label="Комментарий">
            <Input.TextArea rows={3} placeholder="Особенности варианта" />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};

export default ModelVariantsManager;
