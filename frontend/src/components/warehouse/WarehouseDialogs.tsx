import React from 'react';
import {
  Button,
  DatePicker,
  Form,
  Input,
  InputNumber,
  Modal,
  Select,
  Space,
  Switch,
  Typography,
  message,
} from 'antd';
import { InfoCircleOutlined } from '@ant-design/icons';
import { WarehouseIssueDraft, WarehouseReceiptDraft, WarehouseReceiptLine, WarehouseIssueLine, MaterialsListItem } from '../../types';
import { MaterialSelector } from '../shared/MaterialSelector';

interface ReceiptDialogProps {
  open: boolean;
  submitting?: boolean;
  onClose: () => void;
  onSubmit: (draft: WarehouseReceiptDraft) => Promise<void>;
}

interface IssueDialogProps {
  open: boolean;
  submitting?: boolean;
  onClose: () => void;
  onSubmit: (draft: WarehouseIssueDraft) => Promise<void>;
  stockOptions: { label: string; value: string }[];
}

interface InventoryDialogProps {
  open: boolean;
  onClose: () => void;
}

const { Paragraph } = Typography;

const warehouseOptions = [
  { label: 'Основной склад', value: 'WH_MAIN' },
  { label: 'Производство', value: 'WH_PRODUCTION' },
  { label: 'Готовая продукция', value: 'WH_FINISHED' },
];

export const ReceiptDialog: React.FC<ReceiptDialogProps> = ({ open, submitting, onClose, onSubmit }) => {
  const [form] = Form.useForm<WarehouseReceiptDraft>();

  const handleMaterialSelect = (material: MaterialsListItem | undefined, fieldIndex: number) => {
    if (material) {
      // Автозаполнение полей при выборе материала
      form.setFieldValue(['lines', fieldIndex, 'unit'], material.unit);
      if (material.price) {
        form.setFieldValue(['lines', fieldIndex, 'price'], material.price);
      }
      
      // Показать уведомление об автозаполнении
      message.success({
        content: `Автозаполнение: ${material.unit}${material.price ? `, цена ${material.price}` : ''}`,
        duration: 2,
      });
    }
  };

  const handleOk = async () => {
    const values = await form.validateFields();
    console.log('Form values:', values); // Debug log
    console.log('First line:', values.lines?.[0]); // Debug first line
    
    const draft: WarehouseReceiptDraft = {
      referenceNumber: values.referenceNumber,
      supplier: values.supplier,
      lines: (values.lines ?? []).map((line: WarehouseReceiptLine, index: number) => {
        console.log(`Processing line ${index}:`, line); // Debug each line
        
            // Правильная обработка даты (Day.js объект) - конвертируем в ISO datetime
            let receiptDate: string | undefined = undefined;
            if (line.receiptDate && typeof line.receiptDate === 'object') {
              // Day.js объект
              const dateObj = line.receiptDate as any;
              if (dateObj.format && typeof dateObj.format === 'function') {
                receiptDate = dateObj.format('YYYY-MM-DDTHH:mm:ss');
              } else if (dateObj.$d instanceof Date) {
                // Fallback для Day.js
                receiptDate = dateObj.$d.toISOString();
              }
            } else if (typeof line.receiptDate === 'string') {
              // Если строка без времени, добавляем полночь
              receiptDate = line.receiptDate.includes('T') ? line.receiptDate : `${line.receiptDate}T00:00:00`;
            }
        
        const processedLine = {
          materialId: line.materialId,
          quantity: Number(line.quantity),
          unit: line.unit,
          price: line.price ? Number(line.price) : undefined,
          warehouseCode: line.warehouseCode,
          location: line.location,
          batchNumber: line.batchNumber,
          receiptDate: receiptDate,
          comments: line.comments,
        };
        console.log(`Processed line ${index}:`, processedLine); // Debug processed line
        return processedLine;
      }),
    };
    
    console.log('Draft to send:', draft); // Debug log
    await onSubmit(draft);
    form.resetFields();
  };

  return (
    <Modal
      open={open}
      title="Приход материалов"
      onCancel={() => {
        form.resetFields();
        onClose();
      }}
      onOk={handleOk}
      confirmLoading={submitting}
      width={720}
      destroyOnClose
    >
      <Form form={form} layout="vertical">
        <Form.Item name="referenceNumber" label="Номер документа">
          <Input placeholder="Например: RCP-2024-001" />
        </Form.Item>
        <Form.Item name="supplier" label="Поставщик">
          <Input placeholder="Название поставщика" />
        </Form.Item>

        <Form.List name="lines" initialValue={[{}]}>
          {(fields, { add, remove }) => (
            <Space direction="vertical" style={{ width: '100%' }}>
              {fields.map((field) => (
                <Space
                  key={field.key}
                  direction="vertical"
                  style={{ width: '100%', padding: 16, border: '1px solid #f0f0f0', borderRadius: 8 }}
                >
                  <Space align="start" style={{ width: '100%', justifyContent: 'space-between' }}>
                    <Form.Item
                      {...field}
                      name={[field.name, 'materialId']}
                      label="Материал"
                      rules={[{ required: true, message: 'Выберите материал' }]}
                      style={{ flex: 1 }}
                    >
                      <MaterialSelector 
                        placeholder="Выберите материал"
                        showDetails={true}
                        groupBy="group"
                        onMaterialSelect={(material) => handleMaterialSelect(material, field.name)}
                      />
                    </Form.Item>
                    {fields.length > 1 && (
                      <Button type="link" danger onClick={() => remove(field.name)}>
                        Удалить
                      </Button>
                    )}
                  </Space>
                  <Space wrap style={{ width: '100%' }}>
                    <Form.Item
                      {...field}
                      name={[field.name, 'quantity']}
                      label="Количество"
                      rules={[{ required: true, message: 'Укажите количество' }]}
                    >
                      <InputNumber min={0} style={{ width: 140 }} />
                    </Form.Item>
                    <Form.Item {...field} name={[field.name, 'unit']} label="Ед. изм." initialValue="шт">
                      <Input 
                        style={{ width: 120 }} 
                        placeholder="автозаполнение"
                        suffix={<InfoCircleOutlined style={{ color: '#1890ff' }} />}
                      />
                    </Form.Item>
                    <Form.Item {...field} name={[field.name, 'price']} label="Цена">
                      <InputNumber 
                        style={{ width: 150 }} 
                        min={0} 
                        placeholder="автозаполнение"
                        formatter={(value) => value ? `₽ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',') : ''}
                        parser={(value) => value ? value.replace(/₽\s?|(,*)/g, '') : ''}
                      />
                    </Form.Item>
                    <Form.Item {...field} name={[field.name, 'warehouseCode']} label="Склад" initialValue="WH_MAIN">
                      <Select options={warehouseOptions} style={{ width: 200 }} />
                    </Form.Item>
                    <Form.Item {...field} name={[field.name, 'location']} label="Место хранения">
                      <Input style={{ width: 180 }} placeholder="Например: A1-15" />
                    </Form.Item>
                    <Form.Item {...field} name={[field.name, 'receiptDate']} label="Дата прихода">
                      <DatePicker format="YYYY-MM-DD" />
                    </Form.Item>
                  </Space>
                </Space>
              ))}
              <Button type="dashed" onClick={() => add()} block>
                Добавить строку
              </Button>
            </Space>
          )}
        </Form.List>
      </Form>
    </Modal>
  );
};

export const IssueDialog: React.FC<IssueDialogProps> = ({
  open,
  submitting,
  onClose,
  onSubmit,
  stockOptions,
}) => {
  const [form] = Form.useForm<WarehouseIssueDraft>();

  const handleOk = async () => {
    const values = await form.validateFields();
    const draft: WarehouseIssueDraft = {
      lines: (values.lines ?? []).map((line: WarehouseIssueLine) => ({
        ...line,
      })),
    };
    await onSubmit(draft);
    form.resetFields();
  };

  return (
    <Modal
      open={open}
      title="Списание / расход материалов"
      onCancel={() => {
        form.resetFields();
        onClose();
      }}
      onOk={handleOk}
      confirmLoading={submitting}
      width={680}
      destroyOnClose
    >
      <Form form={form} layout="vertical" initialValues={{ lines: [{}] }}>
        <Form.List name="lines">
          {(fields, { add, remove }) => (
            <Space direction="vertical" style={{ width: '100%' }}>
              {fields.map((field) => (
                <Space
                  key={field.key}
                  direction="vertical"
                  style={{ width: '100%', padding: 16, border: '1px solid #f0f0f0', borderRadius: 8 }}
                >
                  <Space align="start" style={{ width: '100%', justifyContent: 'space-between' }}>
                    <Form.Item
                      {...field}
                      name={[field.name, 'stockId']}
                      label="Партия"
                      rules={[{ required: true, message: 'Выберите партию' }]}
                      style={{ flex: 1 }}
                    >
                      <Select showSearch options={stockOptions} placeholder="Выберите партию" />
                    </Form.Item>
                    {fields.length > 1 && (
                      <Button type="link" danger onClick={() => remove(field.name)}>
                        Удалить
                      </Button>
                    )}
                  </Space>
                  <Space wrap style={{ width: '100%' }}>
                    <Form.Item
                      {...field}
                      name={[field.name, 'quantity']}
                      label="Количество"
                      rules={[{ required: true, message: 'Укажите количество' }]}
                    >
                      <InputNumber min={0} style={{ width: 140 }} />
                    </Form.Item>
                    <Form.Item {...field} name={[field.name, 'unit']} label="Ед. изм." initialValue="шт">
                      <Input style={{ width: 120 }} />
                    </Form.Item>
                    <Form.Item {...field} name={[field.name, 'reason']} label="Причина" initialValue="Производство">
                      <Select
                        style={{ width: 200 }}
                        options={[
                          { label: 'Производство', value: 'Производство' },
                          { label: 'Брак', value: 'Брак' },
                          { label: 'Корректировка', value: 'Корректировка' },
                        ]}
                      />
                    </Form.Item>
                    <Form.Item {...field} name={[field.name, 'orderReference']} label="Заказ/процесс">
                      <Input style={{ width: 200 }} placeholder="ORD-2024-001" />
                    </Form.Item>
                  </Space>
                  <Form.Item {...field} name={[field.name, 'comments']} label="Комментарий">
                    <Input.TextArea rows={2} placeholder="Причина списания" />
                  </Form.Item>
                </Space>
              ))}
              <Button type="dashed" onClick={() => add()} block>
                Добавить строку
              </Button>
            </Space>
          )}
        </Form.List>
      </Form>
    </Modal>
  );
};

export const InventoryDialog: React.FC<InventoryDialogProps> = ({ open, onClose }) => (
  <Modal
    open={open}
    title="Инвентаризация"
    onCancel={onClose}
    onOk={onClose}
    okText="Готово"
    width={640}
  >
    <Space direction="vertical" style={{ width: '100%' }}>
      <Paragraph>
        Инвентаризация в демо-режиме показывает текущие остатки. Для фиксации результатов будет добавлена интеграция со складским модулем.
      </Paragraph>
      <Switch checked disabled />{' '}
      <span>Система ведёт контроль за расхождениями автоматически.</span>
    </Space>
  </Modal>
);

export default { ReceiptDialog, IssueDialog, InventoryDialog };
