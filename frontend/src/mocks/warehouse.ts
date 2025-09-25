import {
  WarehouseInventoryDraft,
  WarehouseListResult,
  WarehouseStockListItem,
  WarehouseTransaction,
} from '../types';
import { mockMaterials } from './materials';

const now = new Date('2024-09-21T08:45:00Z').toISOString();

const stocks: WarehouseStockListItem[] = [
  {
    id: 'stock-leather-001',
    material: {
      id: mockMaterials[0].id,
      code: mockMaterials[0].code,
      name: mockMaterials[0].name,
      group: mockMaterials[0].group,
      unit: mockMaterials[0].specs.unitPrimary,
      color: mockMaterials[0].color,
    },
    batchNumber: 'BATCH-LEA-2409',
    warehouseCode: 'WH_MAIN',
    location: 'A1-15',
    quantity: 780,
    reservedQuantity: 80,
    unit: mockMaterials[0].specs.unitPrimary,
    purchasePrice: 430,
    receiptDate: '2024-09-12',
    lastReceiptDate: '2024-09-12',
    lastIssueDate: '2024-09-19',
    notes: 'Закупка партиями по 200 дм²',
    updatedAt: now,
    availableQuantity: 700,
    status: 'OK',
    totalValue: 335400,
  },
  {
    id: 'stock-sole-001',
    material: {
      id: mockMaterials[1].id,
      code: mockMaterials[1].code,
      name: mockMaterials[1].name,
      group: mockMaterials[1].group,
      unit: mockMaterials[1].specs.unitPrimary ?? 'пар',
      color: mockMaterials[1].color,
    },
    batchNumber: 'SOLES-888-2408',
    warehouseCode: 'WH_MAIN',
    location: 'B2-08',
    quantity: 420,
    reservedQuantity: 60,
    unit: mockMaterials[1].specs.unitPrimary ?? 'пар',
    purchasePrice: 265,
    receiptDate: '2024-09-10',
    lastReceiptDate: '2024-09-10',
    lastIssueDate: '2024-09-18',
    updatedAt: now,
    availableQuantity: 360,
    status: 'OK',
    totalValue: 111300,
  },
  {
    id: 'stock-hooks-001',
    material: {
      id: mockMaterials[2].id,
      code: mockMaterials[2].code,
      name: mockMaterials[2].name,
      group: mockMaterials[2].group,
      unit: mockMaterials[2].specs.unitPrimary ?? 'компл',
      color: mockMaterials[2].color,
    },
    batchNumber: 'HOOKS-2409-01',
    warehouseCode: 'WH_PRODUCTION',
    location: 'C1-03',
    quantity: 95,
    reservedQuantity: 30,
    unit: mockMaterials[2].specs.unitPrimary ?? 'компл',
    purchasePrice: 40,
    receiptDate: '2024-09-11',
    lastReceiptDate: '2024-09-11',
    lastIssueDate: '2024-09-20',
    updatedAt: now,
    availableQuantity: 65,
    status: 'LOW',
    totalValue: 3800,
  },
];

export const mockWarehouseStocks = stocks;

export const mockWarehouseTransactions: WarehouseTransaction[] = [
  {
    id: 'trx-001',
    stockId: 'stock-leather-001',
    material: stocks[0].material,
    type: 'RECEIPT',
    quantity: 200,
    unit: stocks[0].unit,
    warehouseTo: 'WH_MAIN',
    referenceNumber: 'RCP-2024-0912',
    referenceType: 'PURCHASE',
    notes: 'Поставка от ООО "Кожторг"',
    performedBy: 'Логистика',
    performedAt: '2024-09-12T09:00:00Z',
  },
  {
    id: 'trx-002',
    stockId: 'stock-hooks-001',
    material: stocks[2].material,
    type: 'ISSUE',
    quantity: 20,
    unit: stocks[2].unit,
    warehouseFrom: 'WH_PRODUCTION',
    referenceNumber: 'PROD-2024-001',
    referenceType: 'PRODUCTION',
    reason: 'Производственный заказ SPORT 250',
    performedBy: 'Кладовщик',
    performedAt: '2024-09-20T08:30:00Z',
  },
];

export const mockWarehouseListResult: WarehouseListResult = {
  items: stocks,
  total: stocks.length,
  page: 1,
  pageSize: 50,
};

export const mockInventoryDraft: WarehouseInventoryDraft = {
  lines: stocks.map((stock) => ({
    stockId: stock.id,
    systemQuantity: stock.quantity,
    countedQuantity: stock.quantity,
    unit: stock.unit,
    difference: 0,
  })),
  performedAt: now,
};
