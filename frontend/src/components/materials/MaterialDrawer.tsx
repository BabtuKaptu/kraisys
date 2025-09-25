import React, { useEffect } from 'react';
import { Alert, Button, Col, Drawer, Form, FormInstance, Input, InputNumber, Row, Select, Space, Switch, Tabs } from 'antd';
import { Material, MaterialDraft, MaterialGroup, UnitOfMeasure } from '../../types';

const { TextArea } = Input;
const { TabPane } = Tabs;

const materialGroups: { label: string; value: MaterialGroup }[] = [
  { label: 'Кожа', value: 'LEATHER' },
  { label: 'Подошва', value: 'SOLE' },
  { label: 'Фурнитура', value: 'HARDWARE' },
  { label: 'Подкладка', value: 'LINING' },
  { label: 'Химия', value: 'CHEMICAL' },
  { label: 'Упаковка', value: 'PACKAGING' },
  { label: 'Текстиль', value: 'TEXTILE' },
  { label: 'Прочее', value: 'OTHER' },
];

const unitOptions: { label: string; value: UnitOfMeasure }[] = [
  'шт',
  'пар',
  'компл',
  'уп',
  'дм²',
  'м²',
  'м',
  'кг',
  'г',
  'л',
  'мл',
].map((unit) => ({ label: unit, value: unit as UnitOfMeasure }));

interface MaterialFormValues {
  code?: string;
  name?: string;
  nameEn?: string;
  group?: MaterialGroup;
  subgroup?: string;
  materialType?: string;
  color?: string;
  isActive?: boolean;
  isCritical?: boolean;
  description?: string;
  texture?: string;
  thicknessMm?: number;
  density?: number;
  unitPrimary?: UnitOfMeasure;
  unitSecondary?: UnitOfMeasure;
  conversionFactor?: number;
  characteristicsNotes?: string;
  price?: number;
  currency?: string;
  supplierName?: string;
  supplierCode?: string;
  leadTimeDays?: number;
  minOrderQty?: number;
  orderMultiplicity?: number;
  storageConditions?: string;
  warrantyMonths?: number;
  safetyStock?: number;
  reorderPoint?: number;
  maxStock?: number;
  warehouseCode?: string;
  lotTracked?: boolean;
  stockNotes?: string;
}

interface MaterialDrawerProps {
  open: boolean;
  material?: Material | null;
  loading?: boolean;
  form?: FormInstance<MaterialFormValues>;
  onClose: () => void;
  onSubmit: (draft: MaterialDraft, context: { materialId?: string }) => Promise<void>;
}

const toFormValues = (material?: Material | null): MaterialFormValues => {
  if (!material) {
    return {
      isActive: true,
      unitPrimary: 'шт',
      lotTracked: false,
    };
  }
  return {
    code: material.code,
    name: material.name,
    nameEn: material.nameEn,
    group: material.group,
    subgroup: material.subgroup,
    materialType: material.materialType,
    color: material.color,
    isActive: material.isActive,
    isCritical: material.isCritical,
    description: material.description,
    texture: material.specs.texture,
    thicknessMm: material.specs.thicknessMm,
    density: material.specs.density,
    unitPrimary: material.specs.unitPrimary,
    unitSecondary: material.specs.unitSecondary,
    conversionFactor: material.specs.conversionFactor,
    characteristicsNotes: material.specs.notes,
    price: material.supply.price,
    currency: material.supply.currency ?? 'RUB',
    supplierName: material.supply.supplierName,
    supplierCode: material.supply.supplierCode,
    leadTimeDays: material.supply.leadTimeDays,
    minOrderQty: material.supply.minOrderQty,
    orderMultiplicity: material.supply.orderMultiplicity,
    storageConditions: material.supply.storageConditions,
    warrantyMonths: material.supply.warrantyMonths,
    safetyStock: material.stock.safetyStock,
    reorderPoint: material.stock.reorderPoint,
    maxStock: material.stock.maxStock,
    warehouseCode: material.stock.warehouseCode,
    lotTracked: material.stock.lotTracked,
  };
};

const fromFormValues = (values: MaterialFormValues): MaterialDraft => ({
  code: values.code ?? '',
  name: values.name ?? '',
  nameEn: values.nameEn,
  group: values.group ?? 'OTHER',
  subgroup: values.subgroup,
  materialType: values.materialType,
  color: values.color,
  isActive: values.isActive ?? true,
  isCritical: values.isCritical,
  description: values.description,
  specs: {
    texture: values.texture,
    thicknessMm: values.thicknessMm,
    density: values.density,
    unitPrimary: values.unitPrimary ?? 'шт',
    unitSecondary: values.unitSecondary,
    conversionFactor: values.conversionFactor,
    notes: values.characteristicsNotes,
  },
  supply: {
    price: values.price,
    currency: values.currency ?? 'RUB',
    supplierName: values.supplierName,
    supplierCode: values.supplierCode,
    leadTimeDays: values.leadTimeDays,
    minOrderQty: values.minOrderQty,
    orderMultiplicity: values.orderMultiplicity,
    storageConditions: values.storageConditions,
    warrantyMonths: values.warrantyMonths,
  },
  stock: {
    safetyStock: values.safetyStock,
    reorderPoint: values.reorderPoint,
    maxStock: values.maxStock,
    warehouseCode: values.warehouseCode,
    lotTracked: values.lotTracked,
  },
});

export const MaterialDrawer: React.FC<MaterialDrawerProps> = ({
  open,
  material,
  loading,
  form: externalForm,
  onClose,
  onSubmit,
}) => {
  const [form] = Form.useForm<MaterialFormValues>();
  const mergedForm = externalForm ?? form;

  useEffect(() => {
    if (open) {
      mergedForm.setFieldsValue(toFormValues(material));
    } else {
      mergedForm.resetFields();
    }
  }, [open, material, mergedForm]);

  const handleSubmit = async () => {
    const values = await mergedForm.validateFields();
    const draft = fromFormValues(values);
    await onSubmit(draft, { materialId: material?.id });
  };

  return (
    <Drawer
      title={material ? `Редактирование материала «${material.name}»` : 'Новый материал'}
      width={800}
      open={open}
      onClose={onClose}
      destroyOnClose
      extra={
        <Space>
          <Button onClick={onClose}>Отмена</Button>
          <Button type="primary" onClick={handleSubmit} loading={loading}>
            Сохранить
          </Button>
        </Space>
      }
    >
      <Form form={mergedForm} layout="vertical" initialValues={toFormValues(material)} disabled={loading}>
        <Tabs defaultActiveKey="main" type="card">
          <TabPane tab="Основные данные" key="main">
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="code" label="Код" rules={[{ required: true, message: 'Укажите код' }]}
                >
                  <Input placeholder="Например: LEATHER001" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="name"
                  label="Название"
                  rules={[{ required: true, message: 'Укажите название' }]}
                >
                  <Input placeholder="Кожа натуральная чёрная" />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="nameEn" label="Название (EN)">
                  <Input placeholder="English name" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="group" label="Группа" rules={[{ required: true, message: 'Выберите группу' }]}>
                  <Select options={materialGroups} placeholder="Выберите группу" />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="subgroup" label="Подгруппа">
                  <Input placeholder="Подгруппа" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="materialType" label="Тип материала">
                  <Input placeholder="Например: Натуральная" />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="color" label="Цвет">
                  <Input placeholder="Например: Чёрный" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="isActive" label="Статус" valuePropName="checked">
                  <Switch checkedChildren="Активен" unCheckedChildren="Архив" defaultChecked />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="isCritical" label="Критичный" valuePropName="checked">
                  <Switch checkedChildren="Да" unCheckedChildren="Нет" />
                </Form.Item>
              </Col>
            </Row>
            <Form.Item name="description" label="Описание">
              <TextArea rows={4} placeholder="Описание материала" />
            </Form.Item>
          </TabPane>

          <TabPane tab="Характеристики" key="specs">
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="texture" label="Текстура">
                  <Input placeholder="Гладкая" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="thicknessMm" label="Толщина, мм">
                  <InputNumber style={{ width: '100%' }} min={0} max={10} step={0.1} />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="density" label="Плотность">
                  <InputNumber style={{ width: '100%' }} min={0} step={0.01} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="unitPrimary" label="Основная ед. изм." rules={[{ required: true, message: 'Выберите единицу' }]}
                >
                  <Select options={unitOptions} />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="unitSecondary" label="Дополнительная ед. изм.">
                  <Select allowClear options={unitOptions} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="conversionFactor" label="Коэффициент перевода">
                  <InputNumber style={{ width: '100%' }} min={0} step={0.001} />
                </Form.Item>
              </Col>
            </Row>
            <Form.Item name="characteristicsNotes" label="Примечания">
              <TextArea rows={3} placeholder="Особенности обработки" />
            </Form.Item>
          </TabPane>

          <TabPane tab="Поставки" key="supply">
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="price" label="Цена">
                  <InputNumber style={{ width: '100%' }} min={0} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="currency" label="Валюта" initialValue="RUB">
                  <Select
                    options={['RUB', 'USD', 'EUR', 'CNY'].map((currency) => ({ label: currency, value: currency }))}
                  />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="supplierName" label="Поставщик">
                  <Input placeholder="Название поставщика" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="supplierCode" label="Код поставщика">
                  <Input placeholder="Внутренний код" />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={8}>
                <Form.Item name="leadTimeDays" label="Срок поставки, дн.">
                  <InputNumber style={{ width: '100%' }} min={0} />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item name="minOrderQty" label="Минимальный заказ">
                  <InputNumber style={{ width: '100%' }} min={0} />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item name="orderMultiplicity" label="Кратность заказа">
                  <InputNumber style={{ width: '100%' }} min={0} />
                </Form.Item>
              </Col>
            </Row>
            <Form.Item name="storageConditions" label="Условия хранения">
              <TextArea rows={3} placeholder="Температура, влажность" />
            </Form.Item>
            <Form.Item name="warrantyMonths" label="Гарантия, мес.">
              <InputNumber style={{ width: 200 }} min={0} />
            </Form.Item>
          </TabPane>

          <TabPane tab="Склад" key="stock">
            <Row gutter={16}>
              <Col span={8}>
                <Form.Item name="safetyStock" label="Страховой запас">
                  <InputNumber style={{ width: '100%' }} min={0} />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item name="reorderPoint" label="Точка заказа">
                  <InputNumber style={{ width: '100%' }} min={0} />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item name="maxStock" label="Макс. запас">
                  <InputNumber style={{ width: '100%' }} min={0} />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="warehouseCode" label="Основной склад">
                  <Input placeholder="Например: WH_MAIN" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="lotTracked" label="Учёт по партиям" valuePropName="checked">
                  <Switch />
                </Form.Item>
              </Col>
            </Row>
            <Alert
              type="info"
              showIcon
              message="История движения"
              description="Детальная история будет доступна после интеграции со складским модулем."
            />
          </TabPane>
        </Tabs>
      </Form>
    </Drawer>
  );
};

export default MaterialDrawer;
