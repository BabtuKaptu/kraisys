import React from 'react';
import { Button, Drawer, Form, Input, Space, Switch } from 'antd';
import { ReferenceDraft } from '../../types';

interface ReferenceDrawerProps {
  open: boolean;
  loading?: boolean;
  type: string;
  initialValues?: ReferenceDraft;
  onClose: () => void;
  onSubmit: (draft: ReferenceDraft) => void;
}

const typeLabels: Record<string, string> = {
  perforation_type: 'Тип перфорации',
  lining_type: 'Тип подкладки',
  cutting_part: 'Деталь кроя',
  lasting_type: 'Тип затяжки',
};

export const ReferenceDrawer: React.FC<ReferenceDrawerProps> = ({
  open,
  loading,
  type,
  initialValues,
  onClose,
  onSubmit,
}) => {
  const [form] = Form.useForm<ReferenceDraft>();

  return (
    <Drawer
      open={open}
      width={480}
      title={initialValues ? `Редактирование: ${typeLabels[type] ?? type}` : `Новый элемент: ${typeLabels[type] ?? type}`}
      onClose={() => {
        form.resetFields();
        onClose();
      }}
      destroyOnClose
      extra={
        <Space>
          <Button onClick={onClose}>Отмена</Button>
          <Button
            type="primary"
            loading={loading}
            onClick={async () => {
              const values = await form.validateFields();
              onSubmit({ ...values, type });
            }}
          >
            Сохранить
          </Button>
        </Space>
      }
    >
      <Form form={form} layout="vertical" initialValues={initialValues ?? { isActive: true }}>
        <Form.Item name="code" label="Код">
          <Input placeholder="Код элемента" />
        </Form.Item>
        <Form.Item
          name="name"
          label="Название"
          rules={[{ required: true, message: 'Введите название' }]}
        >
          <Input placeholder="Название" />
        </Form.Item>
        <Form.Item name="description" label="Описание">
          <Input.TextArea rows={3} placeholder="Описание или примечание" />
        </Form.Item>
        <Form.Item name="isActive" label="Активен" valuePropName="checked">
          <Switch />
        </Form.Item>
        <Form.Item name={['attributes', 'notes']} label="Дополнительно">
          <Input.TextArea rows={3} placeholder="Дополнительные атрибуты" />
        </Form.Item>
      </Form>
    </Drawer>
  );
};

export default ReferenceDrawer;
