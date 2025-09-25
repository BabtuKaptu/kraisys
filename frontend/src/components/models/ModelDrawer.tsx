import React, { useEffect, useMemo } from 'react';
import {
  Alert,
  Button,
  Card,
  Col,
  Collapse,
  Divider,
  Drawer,
  Form,
  FormInstance,
  Input,
  InputNumber,
  List,
  Row,
  Select,
  Space,
  Switch,
  Tabs,
  Tag,
  Typography,
} from 'antd';
import { PlusOutlined, MinusCircleOutlined, EditOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { Gender, LacingType, Model, ModelCategory, ModelDraft, ModelType, Season } from '../../types';
import { materialsApi } from '../../services/materialsApi';
import { referenceApi } from '../../services/referenceApi';
import { MaterialSelector } from '../shared/MaterialSelector';
import { ReferenceSelector } from '../shared/ReferenceSelector';

const { Title, Paragraph, Text } = Typography;
const { TabPane } = Tabs;
const { Panel } = Collapse;

const genderOptions: Gender[] = ['MALE', 'FEMALE', 'UNISEX', 'KIDS'];
const modelTypeOptions: ModelType[] = ['SPORT', 'CASUAL', 'FORMAL', 'WORK', 'OUTDOOR', 'SPECIAL'];
const categoryOptions: ModelCategory[] = [
  'SNEAKERS',
  'SHOES',
  'BOOTS',
  'SANDALS',
  'SLIPPERS',
  'LOAFERS',
  'OXFORDS',
  'DERBY',
  'OTHER',
];
const seasonOptions: Season[] = ['SPRING_SUMMER', 'FALL_WINTER', 'ALL_SEASON', 'DEMISEASON', 'CUSTOM'];
const lacingOptions: LacingType[] = ['GLUED', 'STITCHED', 'HANDMADE', 'COMBINED', 'CEMENTED', 'LASTING'];

interface HardwareItemFormValues {
  id?: string;
  name?: string;
  materialGroup?: string;
  compatibleMaterials?: string[];
  requiresExactSelection?: boolean;
  notes?: string;
}

interface HardwareSetFormValues {
  id?: string;
  name?: string;
  description?: string;
  isDefault?: boolean;
  isActive?: boolean;
  items?: HardwareItemFormValues[];
}

interface FormPerforationOption {
  id?: string;
  name?: string;
  code?: string;
  description?: string;
  isDefault?: boolean;
  isActive?: boolean;
}

interface FormInsoleOption {
  id?: string;
  name?: string;
  material?: string;
  seasonality?: Season;
  thicknessMm?: number;
  isDefault?: boolean;
  isActive?: boolean;
}

interface FormCuttingPart {
  id?: string;
  partId?: string;
  materialId?: string;
  quantity?: number;
  consumptionPerPair?: number;
  laborCost?: number;
  notes?: string;
}

interface FormSoleOption {
  id?: string;
  name?: string;
  materialId?: string;
  sizeMin?: number;
  sizeMax?: number;
  isDefault?: boolean;
  color?: string;
  notes?: string;
}

export interface ModelFormValues {
  name?: string;
  article?: string;
  gender?: Gender;
  modelType?: ModelType;
  category?: ModelCategory;
  collection?: string;
  season?: Season;
  lastCode?: string;
  lastType?: string;
  sizeMin?: number;
  sizeMax?: number;
  lacingType?: LacingType;
  isActive?: boolean;
  retailPrice?: number;
  wholesalePrice?: number;
  materialCost?: number;
  laborCost?: number;
  overheadCost?: number;
  description?: string;
  superBom?: {
    perforationOptions?: FormPerforationOption[];
    insoleOptions?: FormInsoleOption[];
    hardwareSets?: HardwareSetFormValues[];
  };
  cuttingParts?: FormCuttingPart[];
  soleOptions?: FormSoleOption[];
  notes?: string;
}

interface ModelDrawerProps {
  open: boolean;
  loading?: boolean;
  model?: Model;
  form?: FormInstance<ModelFormValues>;
  onClose: () => void;
  onSubmit: (draft: ModelDraft, context: { modelId?: string }) => Promise<void>;
  onManageVariants?: (model: Model) => void;
}

const toFormValues = (model?: Model): ModelFormValues => {
  if (!model) {
    return {
      isActive: true,
      sizeMin: 39,
      sizeMax: 45,
      retailPrice: 0,
      wholesalePrice: 0,
      superBom: {
        perforationOptions: [
          {
            id: `perf-${Date.now()}`,
            name: 'Без перфорации',
            isDefault: true,
            isActive: true,
          },
        ],
        insoleOptions: [
          {
            id: `insole-${Date.now()}`,
            name: 'Стелька стандарт',
            isDefault: true,
            isActive: true,
          },
        ],
        hardwareSets: [
          {
            id: `hardware-${Date.now()}`,
            name: 'Базовый комплект',
            isDefault: true,
            isActive: true,
            items: [],
          },
        ],
      },
      cuttingParts: [],
      soleOptions: [],
    };
  }

  return {
    name: model.name,
    article: model.article,
    gender: model.gender,
    modelType: model.modelType,
    category: model.category,
    collection: model.collection,
    season: model.season,
    lastCode: model.lastCode,
    lastType: model.lastType,
    sizeMin: model.sizeMin,
    sizeMax: model.sizeMax,
    lacingType: model.lacingType,
    isActive: model.isActive,
    retailPrice: model.retailPrice,
    wholesalePrice: model.wholesalePrice,
    materialCost: model.materialCost,
    laborCost: model.laborCost,
    overheadCost: model.overheadCost,
    description: model.description,
    superBom: {
      perforationOptions: model.superBom.perforationOptions.map((option) => ({
        ...option,
      })),
      insoleOptions: model.superBom.insoleOptions.map((option) => ({
        ...option,
      })),
      hardwareSets: model.superBom.hardwareSets.map((set) => ({
        ...set,
        items: set.items?.map((item) => ({
          ...item,
          compatibleMaterials: item.compatibleMaterials?.map((material) => material.id),
        })),
      })),
    },
    cuttingParts: model.cuttingParts?.map((usage) => ({
      id: usage.id,
      partId: usage.part.id,
      materialId: usage.material.id,
      quantity: usage.quantity,
      consumptionPerPair: usage.consumptionPerPair,
      laborCost: usage.laborCost,
      notes: usage.notes,
    })),
    soleOptions: model.soleOptions?.map((sole) => ({
      ...sole,
      materialId: sole.material.id,
    })),
    notes: model.notes,
  };
};

const fromFormValues = (values: ModelFormValues): ModelDraft => {
  return {
    name: values.name ?? '',
    article: values.article ?? '',
    gender: values.gender ?? 'UNISEX',
    modelType: values.modelType ?? 'CASUAL',
    category: values.category ?? 'OTHER',
    collection: values.collection,
    season: values.season,
    lastCode: values.lastCode,
    lastType: values.lastType,
    sizeMin: values.sizeMin ?? 39,
    sizeMax: values.sizeMax ?? 45,
    lacingType: values.lacingType,
    isActive: values.isActive ?? true,
    retailPrice: Number(values.retailPrice ?? 0),
    wholesalePrice: Number(values.wholesalePrice ?? 0),
    materialCost: values.materialCost,
    laborCost: values.laborCost,
    overheadCost: values.overheadCost,
    description: values.description,
    superBom: {
      perforationOptions: values.superBom?.perforationOptions?.map((option, index) => ({
        id: option.id ?? `perf-${index}-${Date.now()}`,
        name: option.name ?? '',
        code: option.code,
        description: option.description,
        isDefault: option.isDefault,
        isActive: option.isActive ?? true,
      })) ?? [],
      insoleOptions: values.superBom?.insoleOptions?.map((option, index) => ({
        id: option.id ?? `insole-${index}-${Date.now()}`,
        name: option.name ?? '',
        material: option.material,
        seasonality: option.seasonality,
        thicknessMm: option.thicknessMm,
        isDefault: option.isDefault,
        isActive: option.isActive ?? true,
      })) ?? [],
      hardwareSets: values.superBom?.hardwareSets?.map((set, index) => ({
        id: set.id ?? `hardware-${index}-${Date.now()}`,
        name: set.name ?? '',
        description: set.description,
        isDefault: set.isDefault,
        isActive: set.isActive ?? true,
        items:
          set.items?.map((item, itemIndex) => ({
            id: item.id ?? `hardware-item-${itemIndex}-${Date.now()}`,
            name: item.name ?? '',
            materialGroup: (item.materialGroup as any) ?? 'HARDWARE',
            compatibleMaterials:
              item.compatibleMaterials?.map((materialId) => ({
                id: materialId,
                code: '',
                name: '',
                group: 'OTHER',
                unit: 'шт',
              })) ?? [],
            requiresExactSelection: item.requiresExactSelection,
            notes: item.notes,
          })) ?? [],
      })) ?? [],
    },
    cuttingParts:
      values.cuttingParts?.map((entry, index) => ({
        id: entry.id ?? `cutting-${index}-${Date.now()}`,
        part: {
          id: entry.partId ?? '',
          name: '',
          type: 'cutting_part',
          isActive: true,
        },
        material: {
          id: entry.materialId ?? '',
          code: '',
          name: '',
          group: 'OTHER',
          unit: 'шт',
        },
        quantity: Number(entry.quantity ?? 0),
        consumptionPerPair: entry.consumptionPerPair,
        laborCost: entry.laborCost,
        notes: entry.notes,
      })) ?? [],
    soleOptions:
      values.soleOptions?.map((option, index) => ({
        id: option.id ?? `sole-${index}-${Date.now()}`,
        name: option.name ?? '',
        material: {
          id: option.materialId ?? '',
          code: '',
          name: '',
          group: 'SOLE',
          unit: 'пар',
        },
        sizeMin: option.sizeMin ?? 35,
        sizeMax: option.sizeMax ?? 46,
        isDefault: option.isDefault,
        color: option.color,
        notes: option.notes,
      })) ?? [],
    notes: values.notes,
    attachments: [],
  };
};

export const ModelDrawer: React.FC<ModelDrawerProps> = ({
  open,
  loading,
  model,
  form: externalForm,
  onClose,
  onSubmit,
  onManageVariants,
}) => {
  const [form] = Form.useForm<ModelFormValues>();
  const mergedForm = externalForm ?? form;

  useEffect(() => {
    if (open) {
      mergedForm.setFieldsValue(toFormValues(model));
    } else {
      mergedForm.resetFields();
    }
  }, [open, model, mergedForm]);

  // Удаляем старый запрос cutting parts - теперь это делает ReferenceSelector

  const submitHandler = async () => {
    try {
      const values = await mergedForm.validateFields();
      const draft = fromFormValues(values);
      await onSubmit(draft, { modelId: model?.id });
    } catch (error) {
      if (typeof error === 'object' && error !== null && 'errorFields' in error) {
        return;
      }
      throw error;
    }
  };

  return (
    <Drawer
      title={model ? `Редактирование модели «${model.name}»` : 'Создание новой модели'}
      open={open}
      onClose={onClose}
      width={960}
      destroyOnClose
      extra={
        <Space>
          <Button onClick={onClose}>Отмена</Button>
          <Button type="primary" onClick={submitHandler} loading={loading}>
            Сохранить
          </Button>
        </Space>
      }
    >
      <Form
        form={mergedForm}
        layout="vertical"
        initialValues={toFormValues(model)}
        disabled={loading}
        scrollToFirstError
      >
        <Tabs defaultActiveKey="general" type="card">
          <TabPane tab="Основное" key="general">
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="name"
                  label="Название модели"
                  rules={[{ required: true, message: 'Укажите название' }]}
                >
                  <Input placeholder="Например: SPORT 250" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="article"
                  label="Артикул"
                  rules={[{ required: true, message: 'Укажите артикул' }]}
                >
                  <Input placeholder="Например: SPT-250" />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="gender" label="Пол" rules={[{ required: true, message: 'Выберите пол' }]}>
                  <Select options={genderOptions.map((value) => ({ value, label: value }))} placeholder="Пол" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="modelType"
                  label="Тип модели"
                  rules={[{ required: true, message: 'Выберите тип' }]}
                >
                  <Select options={modelTypeOptions.map((value) => ({ value, label: value }))} />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="category"
                  label="Категория"
                  rules={[{ required: true, message: 'Выберите категорию' }]}
                >
                  <Select options={categoryOptions.map((value) => ({ value, label: value }))} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="collection" label="Коллекция">
                  <Input placeholder="Например: Осень-Зима 2024" />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="season" label="Сезон">
                  <Select
                    allowClear
                    options={seasonOptions.map((value) => ({ value, label: value }))}
                    placeholder="Выберите сезон"
                  />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="lacingType" label="Тип затяжки">
                  <Select allowClear options={lacingOptions.map((value) => ({ value, label: value }))} />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="lastCode" label="Колодка">
                  <Input placeholder="Например: 75" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="lastType" label="Тип колодки">
                  <Input placeholder="Например: Ботиночная" />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="sizeMin"
                  label="Размер от"
                  rules={[{ required: true, message: 'Укажите минимальный размер' }]}
                >
                  <InputNumber style={{ width: '100%' }} min={20} max={50} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="sizeMax"
                  label="Размер до"
                  rules={[{ required: true, message: 'Укажите максимальный размер' }]}
                >
                  <InputNumber style={{ width: '100%' }} min={20} max={55} />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={24}>
                <Form.Item name="isActive" label="Статус" valuePropName="checked">
                  <Switch checkedChildren="Активна" unCheckedChildren="Архив" />
                </Form.Item>
              </Col>
            </Row>
            <Divider orientation="left">Ценообразование</Divider>
            <Row gutter={16}>
              <Col span={8}>
                <Form.Item name="retailPrice" label="Розничная цена" rules={[{ required: true }]}> 
                  <InputNumber style={{ width: '100%' }} min={0} />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item name="wholesalePrice" label="Оптовая цена" rules={[{ required: true }]}>
                  <InputNumber style={{ width: '100%' }} min={0} />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item name="materialCost" label="Себестоимость материалов">
                  <InputNumber style={{ width: '100%' }} min={0} />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item name="laborCost" label="Трудозатраты">
                  <InputNumber style={{ width: '100%' }} min={0} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="overheadCost" label="Накладные">
                  <InputNumber style={{ width: '100%' }} min={0} />
                </Form.Item>
              </Col>
            </Row>
            <Form.Item name="description" label="Описание">
              <Input.TextArea rows={4} placeholder="Краткое описание модели" />
            </Form.Item>
          </TabPane>

          <TabPane tab="Конфигурация (SUPER-BOM)" key="superBom">
            <Collapse defaultActiveKey={["perforation", "insoles", "hardware"]}>
              <Panel header="Перфорация" key="perforation">
                <Form.List name={['superBom', 'perforationOptions']}>
                  {(fields, { add, remove }) => (
                    <Space direction="vertical" style={{ width: '100%' }}>
                      {fields.map((field) => (
                        <Card
                          key={field.key}
                          size="small"
                          title={mergedForm.getFieldValue(['superBom', 'perforationOptions', field.name, 'name']) || 'Вариант'}
                          extra={
                            fields.length > 1 ? (
                              <MinusCircleOutlined onClick={() => remove(field.name)} style={{ color: '#ff4d4f' }} />
                            ) : null
                          }
                        >
                          <Row gutter={12}>
                            <Col span={8}>
                              <Form.Item
                                {...field}
                                name={[field.name, 'name']}
                                label="Название"
                                rules={[{ required: true, message: 'Введите название' }]}
                              >
                                <Input placeholder="Например: Без перфорации" />
                              </Form.Item>
                            </Col>
                            <Col span={8}>
                              <Form.Item {...field} name={[field.name, 'code']} label="Код">
                                <Input placeholder="Код варианта" />
                              </Form.Item>
                            </Col>
                            <Col span={4}>
                              <Form.Item
                                {...field}
                                name={[field.name, 'isDefault']}
                                label="По умолчанию"
                                valuePropName="checked"
                              >
                                <Switch />
                              </Form.Item>
                            </Col>
                            <Col span={4}>
                              <Form.Item
                                {...field}
                                name={[field.name, 'isActive']}
                                label="Активен"
                                valuePropName="checked"
                                initialValue
                              >
                                <Switch defaultChecked />
                              </Form.Item>
                            </Col>
                          </Row>
                          <Form.Item {...field} name={[field.name, 'description']} label="Описание">
                            <Input.TextArea rows={2} placeholder="Комментарий" />
                          </Form.Item>
                        </Card>
                      ))}
                      <Button icon={<PlusOutlined />} type="dashed" onClick={() => add()} block>
                        Добавить вариант перфорации
                      </Button>
                    </Space>
                  )}
                </Form.List>
              </Panel>

              <Panel header="Стельки" key="insoles">
                <Form.List name={['superBom', 'insoleOptions']}>
                  {(fields, { add, remove }) => (
                    <Space direction="vertical" style={{ width: '100%' }}>
                      {fields.map((field) => (
                        <Card
                          key={field.key}
                          size="small"
                          title={mergedForm.getFieldValue(['superBom', 'insoleOptions', field.name, 'name']) || 'Стелька'}
                          extra={
                            fields.length > 1 ? (
                              <MinusCircleOutlined onClick={() => remove(field.name)} style={{ color: '#ff4d4f' }} />
                            ) : null
                          }
                        >
                          <Row gutter={12}>
                            <Col span={10}>
                              <Form.Item
                                {...field}
                                name={[field.name, 'name']}
                                label="Название"
                                rules={[{ required: true, message: 'Введите название стельки' }]}
                              >
                                <Input placeholder="Стелька EVA" />
                              </Form.Item>
                            </Col>
                            <Col span={6}>
                              <Form.Item {...field} name={[field.name, 'material']} label="Материал">
                                <Input placeholder="Материал" />
                              </Form.Item>
                            </Col>
                            <Col span={4}>
                              <Form.Item {...field} name={[field.name, 'seasonality']} label="Сезон">
                                <Select allowClear options={seasonOptions.map((value) => ({ value, label: value }))} />
                              </Form.Item>
                            </Col>
                            <Col span={4}>
                              <Form.Item {...field} name={[field.name, 'isDefault']} label="По умолчанию" valuePropName="checked">
                                <Switch />
                              </Form.Item>
                            </Col>
                          </Row>
                          <Row gutter={12}>
                            <Col span={8}>
                              <Form.Item {...field} name={[field.name, 'thicknessMm']} label="Толщина, мм">
                                <InputNumber style={{ width: '100%' }} min={0} max={20} />
                              </Form.Item>
                            </Col>
                            <Col span={8}>
                              <Form.Item {...field} name={[field.name, 'isActive']} label="Активна" valuePropName="checked">
                                <Switch defaultChecked />
                              </Form.Item>
                            </Col>
                          </Row>
                        </Card>
                      ))}
                      <Button icon={<PlusOutlined />} type="dashed" onClick={() => add()} block>
                        Добавить стельку
                      </Button>
                    </Space>
                  )}
                </Form.List>
              </Panel>

              <Panel header="Фурнитурные наборы" key="hardware">
                <Form.List name={['superBom', 'hardwareSets']}>
                  {(fields, { add, remove }) => (
                    <Space direction="vertical" style={{ width: '100%' }}>
                      {fields.map((field) => (
                        <Card
                          key={field.key}
                          size="small"
                          title={mergedForm.getFieldValue(['superBom', 'hardwareSets', field.name, 'name']) || 'Комплект фурнитуры'}
                          extra={
                            fields.length > 1 ? (
                              <MinusCircleOutlined onClick={() => remove(field.name)} style={{ color: '#ff4d4f' }} />
                            ) : null
                          }
                        >
                          <Row gutter={12}>
                            <Col span={10}>
                              <Form.Item
                                {...field}
                                name={[field.name, 'name']}
                                label="Название"
                                rules={[{ required: true, message: 'Укажите название набора' }]}
                              >
                                <Input placeholder="Крючки + шнурки" />
                              </Form.Item>
                            </Col>
                            <Col span={10}>
                              <Form.Item {...field} name={[field.name, 'description']} label="Описание">
                                <Input placeholder="Описание комплекта" />
                              </Form.Item>
                            </Col>
                            <Col span={2}>
                              <Form.Item {...field} name={[field.name, 'isDefault']} label="Default" valuePropName="checked">
                                <Switch />
                              </Form.Item>
                            </Col>
                            <Col span={2}>
                              <Form.Item {...field} name={[field.name, 'isActive']} label="Активен" valuePropName="checked">
                                <Switch defaultChecked />
                              </Form.Item>
                            </Col>
                          </Row>
                          <Form.List name={[field.name, 'items']}>
                            {(itemFields, itemOperations) => (
                              <>
                                <div style={{ marginLeft: 32 }}>
                                  {itemFields.map((item) => (
                                    <Card
                                      key={item.key}
                                      size="small"
                                      style={{ marginBottom: 16 }}
                                      title="Элемент комплекта"
                                      extra={
                                        <MinusCircleOutlined
                                          onClick={() => itemOperations.remove(item.name)}
                                          style={{ color: '#ff4d4f' }}
                                        />
                                      }
                                    >
                                      <Row gutter={12}>
                                        <Col span={12}>
                                          <Form.Item
                                            {...item}
                                            name={[item.name, 'name']}
                                            label="Название"
                                            rules={[{ required: true, message: 'Укажите название элемента' }]}
                                          >
                                            <Input placeholder="Например: Крючки" />
                                          </Form.Item>
                                        </Col>
                                        <Col span={12}>
                                          <Form.Item {...item} name={[item.name, 'materialGroup']} label="Группа материала">
                                            <Select
                                              placeholder="Группа"
                                              options={[
                                                { label: 'Фурнитура', value: 'HARDWARE' },
                                                { label: 'Подошвы', value: 'SOLE' },
                                                { label: 'Текстиль', value: 'TEXTILE' },
                                                { label: 'Прочее', value: 'OTHER' },
                                              ]}
                                              allowClear
                                            />
                                          </Form.Item>
                                        </Col>
                                      </Row>
                                      <Row gutter={12}>
                                        <Col span={16}>
                                          <Form.Item {...item} name={[item.name, 'compatibleMaterials']} label="Варианты номенклатуры">
                                            <Select
                                              mode="multiple"
                                              placeholder="Выберите материалы"
                                              options={materialSelectOptions}
                                              showSearch
                                            />
                                          </Form.Item>
                                        </Col>
                                        <Col span={8}>
                                          <Form.Item
                                            {...item}
                                            name={[item.name, 'requiresExactSelection']}
                                            label="Уточнять при заказе"
                                            valuePropName="checked"
                                          >
                                            <Switch checkedChildren="Да" unCheckedChildren="Нет" />
                                          </Form.Item>
                                        </Col>
                                      </Row>
                                      <Form.Item {...item} name={[item.name, 'notes']} label="Комментарий">
                                        <Input.TextArea rows={2} placeholder="Особые требования" />
                                      </Form.Item>
                                    </Card>
                                  ))}
                                </div>
                                <Button
                                  icon={<PlusOutlined />}
                                  type="dashed"
                                  onClick={() => itemOperations.add({ requiresExactSelection: false })}
                                  block
                                >
                                  Добавить элемент
                                </Button>
                              </>
                            )}
                          </Form.List>
                        </Card>
                      ))}
                      <Button icon={<PlusOutlined />} type="dashed" onClick={() => add({ items: [] })} block>
                        Добавить набор
                      </Button>
                    </Space>
                  )}
                </Form.List>
              </Panel>
            </Collapse>
          </TabPane>

          <TabPane tab="Детали и подошвы" key="cutting">
            <Title level={5}>Детали кроя</Title>
            <Form.List name="cuttingParts">
              {(fields, { add, remove }) => (
                <Space direction="vertical" style={{ width: '100%' }}>
                  {fields.map((field) => (
                    <Card
                      key={field.key}
                      size="small"
                      title={`Деталь #${field.name + 1}`}
                      extra={<MinusCircleOutlined onClick={() => remove(field.name)} style={{ color: '#ff4d4f' }} />}
                    >
                      <Row gutter={12}>
                        <Col span={8}>
                          <Form.Item
                            {...field}
                            name={[field.name, 'partId']}
                            label="Деталь"
                            rules={[{ required: true, message: 'Выберите деталь' }]}
                          >
                            <ReferenceSelector
                              referenceType="cutting_part"
                              placeholder="Выберите деталь кроя"
                              showCode={false}
                            />
                          </Form.Item>
                        </Col>
                        <Col span={8}>
                          <Form.Item
                            {...field}
                            name={[field.name, 'materialId']}
                            label="Материал"
                            rules={[{ required: true, message: 'Выберите материал' }]}
                          >
                            <MaterialSelector 
                              placeholder="Выберите материал"
                              showDetails={true}
                              groupBy="group"
                            />
                          </Form.Item>
                        </Col>
                        <Col span={4}>
                          <Form.Item {...field} name={[field.name, 'quantity']} label="Количество" initialValue={1}>
                            <InputNumber style={{ width: '100%' }} min={0} max={10} />
                          </Form.Item>
                        </Col>
                        <Col span={4}>
                          <Form.Item {...field} name={[field.name, 'consumptionPerPair']} label="Расход, дм²">
                            <InputNumber style={{ width: '100%' }} min={0} step={0.1} />
                          </Form.Item>
                        </Col>
                      </Row>
                      <Row gutter={12}>
                        <Col span={6}>
                          <Form.Item {...field} name={[field.name, 'laborCost']} label="Трудозатраты, мин">
                            <InputNumber style={{ width: '100%' }} min={0} step={0.1} />
                          </Form.Item>
                        </Col>
                        <Col span={18}>
                          <Form.Item {...field} name={[field.name, 'notes']} label="Комментарий">
                            <Input.TextArea rows={2} />
                          </Form.Item>
                        </Col>
                      </Row>
                    </Card>
                  ))}
                  <Button icon={<PlusOutlined />} type="dashed" onClick={() => add()} block>
                    Добавить деталь
                  </Button>
                </Space>
              )}
            </Form.List>

            <Divider orientation="left">Подошвы</Divider>
            <Form.List name="soleOptions">
              {(fields, { add, remove }) => (
                <Space direction="vertical" style={{ width: '100%' }}>
                  {fields.map((field) => (
                    <Card
                      key={field.key}
                      size="small"
                      title={mergedForm.getFieldValue(['soleOptions', field.name, 'name']) || 'Вариант подошвы'}
                      extra={<MinusCircleOutlined onClick={() => remove(field.name)} style={{ color: '#ff4d4f' }} />}
                    >
                      <Row gutter={12}>
                        <Col span={8}>
                          <Form.Item
                            {...field}
                            name={[field.name, 'name']}
                            label="Название"
                            rules={[{ required: true, message: 'Укажите название подошвы' }]}
                          >
                            <Input placeholder="Подошва 888" />
                          </Form.Item>
                        </Col>
                        <Col span={8}>
                          <Form.Item
                            {...field}
                            name={[field.name, 'materialId']}
                            label="Материал"
                            rules={[{ required: true, message: 'Выберите материал подошвы' }]}
                          >
                            <Select placeholder="Материал" options={materialSelectOptions} showSearch />
                          </Form.Item>
                        </Col>
                        <Col span={4}>
                          <Form.Item {...field} name={[field.name, 'sizeMin']} label="Размер от">
                            <InputNumber style={{ width: '100%' }} min={30} max={55} />
                          </Form.Item>
                        </Col>
                        <Col span={4}>
                          <Form.Item {...field} name={[field.name, 'sizeMax']} label="Размер до">
                            <InputNumber style={{ width: '100%' }} min={30} max={55} />
                          </Form.Item>
                        </Col>
                      </Row>
                      <Row gutter={12}>
                        <Col span={4}>
                          <Form.Item {...field} name={[field.name, 'isDefault']} label="По умолчанию" valuePropName="checked">
                            <Switch />
                          </Form.Item>
                        </Col>
                        <Col span={8}>
                          <Form.Item {...field} name={[field.name, 'color']} label="Цвет">
                            <Input placeholder="Цвет" />
                          </Form.Item>
                        </Col>
                        <Col span={12}>
                          <Form.Item {...field} name={[field.name, 'notes']} label="Комментарий">
                            <Input placeholder="Например: Для outdoor" />
                          </Form.Item>
                        </Col>
                      </Row>
                    </Card>
                  ))}
                  <Button icon={<PlusOutlined />} type="dashed" onClick={() => add()} block>
                    Добавить вариант подошвы
                  </Button>
                </Space>
              )}
            </Form.List>
          </TabPane>

          <TabPane tab="Варианты" key="variants" forceRender>
            {model ? (
              <>
                <Paragraph>
                  Управляйте коллекционными вариантами модели. Можно открыть менеджер вариантов для добавления новых конфигураций или правки существующих.
                </Paragraph>
                <List
                  itemLayout="vertical"
                  dataSource={model.variants}
                  locale={{ emptyText: 'Пока нет сохранённых вариантов' }}
                  renderItem={(variant) => (
                    <List.Item
                      key={variant.id}
                      actions={[
                        <Button
                          key="manage"
                          icon={<EditOutlined />}
                          onClick={() => onManageVariants?.(model)}
                          type="link"
                        >
                          Открыть менеджер вариантов
                        </Button>,
                      ]}
                    >
                      <List.Item.Meta
                        title={
                          <Space>
                            <Text strong>{variant.name}</Text>
                            {variant.isDefault && <Tag color="green">По умолчанию</Tag>}
                            <Tag color={variant.status === 'ACTIVE' ? 'blue' : 'red'}>{variant.status === 'ACTIVE' ? 'Активен' : 'Отключен'}</Tag>
                          </Space>
                        }
                        description={variant.code}
                      />
                      <Paragraph type="secondary">
                        Стоимость материалов: {variant.totalMaterialCost ? `₽ ${variant.totalMaterialCost}` : '—'}
                      </Paragraph>
                    </List.Item>
                  )}
                />
                <Button type="primary" onClick={() => onManageVariants?.(model)}>
                  Открыть менеджер вариантов
                </Button>
              </>
            ) : (
              <Alert type="info" message="Варианты станут доступны после сохранения модели" showIcon />
            )}
          </TabPane>

          <TabPane tab="Заметки" key="notes">
            <Form.Item name="notes" label="Комментарии">
              <Input.TextArea rows={6} placeholder="Внутренние заметки по модели" />
            </Form.Item>
            <Alert
              type="info"
              message="Загрузка файлов пока не реализована"
              description="После интеграции с backend появится возможность прикладывать техлист, фотографии и прочие документы."
              showIcon
            />
          </TabPane>
        </Tabs>
      </Form>
    </Drawer>
  );
};

export default ModelDrawer;
