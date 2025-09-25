import { ListQuery, PaginatedResult, UnitOfMeasure } from './common';
import { MaterialReference } from './material';

export type WarehouseCode = 'WH_MAIN' | 'WH_PRODUCTION' | 'WH_FINISHED' | 'WH_RESERVED' | string;

export interface WarehouseStock {
  id: string;
  material: MaterialReference;
  batchNumber?: string;
  warehouseCode: WarehouseCode;
  location?: string;
  quantity: number;
  reservedQuantity: number;
  unit: UnitOfMeasure;
  purchasePrice?: number;
  receiptDate?: string;
  expiryDate?: string;
  lastReceiptDate?: string;
  lastIssueDate?: string;
  notes?: string;
  updatedAt: string;
}

export type WarehouseStatus = 'OK' | 'LOW' | 'CRITICAL';

export interface WarehouseStockListItem extends WarehouseStock {
  availableQuantity: number;
  status: WarehouseStatus;
  totalValue?: number;
}

export interface WarehouseTransaction {
  id: string;
  stockId: string;
  material: MaterialReference;
  type: 'RECEIPT' | 'ISSUE' | 'TRANSFER' | 'ADJUSTMENT';
  quantity: number;
  unit: UnitOfMeasure;
  warehouseFrom?: WarehouseCode;
  warehouseTo?: WarehouseCode;
  referenceNumber?: string;
  referenceType?: string;
  reason?: string;
  notes?: string;
  performedBy?: string;
  performedAt: string;
}

export interface WarehouseReceiptLine {
  materialId: string;
  quantity: number;
  unit: UnitOfMeasure;
  price?: number;
  warehouseCode: WarehouseCode;
  location?: string;
  batchNumber?: string;
  receiptDate?: string;
  comments?: string;
}

export interface WarehouseReceiptDraft {
  referenceNumber?: string;
  supplier?: string;
  lines: WarehouseReceiptLine[];
}

export interface WarehouseIssueLine {
  stockId: string;
  quantity: number;
  unit: UnitOfMeasure;
  reason: string;
  orderReference?: string;
  comments?: string;
}

export interface WarehouseIssueDraft {
  lines: WarehouseIssueLine[];
}

export interface WarehouseInventoryLine {
  stockId: string;
  systemQuantity: number;
  countedQuantity: number;
  unit: UnitOfMeasure;
  difference: number;
}

export interface WarehouseInventoryDraft {
  lines: WarehouseInventoryLine[];
  performedAt?: string;
  responsible?: string;
}

export interface WarehouseListQuery extends ListQuery {
  warehouseCode?: WarehouseCode;
  status?: WarehouseStatus;
  showArchived?: boolean;
}

export type WarehouseListResult = PaginatedResult<WarehouseStockListItem>;
