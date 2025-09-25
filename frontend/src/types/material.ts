import { Attachment, ListQuery, MaterialGroup, PaginatedResult, UnitOfMeasure } from './common';

export interface MaterialBase {
  code: string;
  name: string;
  nameEn?: string;
  group: MaterialGroup;
  subgroup?: string;
  materialType?: string;
  color?: string;
  isActive: boolean;
  isCritical?: boolean;
  description?: string;
}

export interface MaterialSpecs {
  texture?: string;
  thicknessMm?: number;
  density?: number;
  unitPrimary: UnitOfMeasure;
  unitSecondary?: UnitOfMeasure;
  conversionFactor?: number;
  notes?: string;
}

export interface MaterialSupplyInfo {
  price?: number;
  currency?: string;
  supplierName?: string;
  supplierCode?: string;
  leadTimeDays?: number;
  minOrderQty?: number;
  orderMultiplicity?: number;
  storageConditions?: string;
  warrantyMonths?: number;
}

export interface MaterialStockSettings {
  safetyStock?: number;
  reorderPoint?: number;
  maxStock?: number;
  warehouseCode?: string;
  lotTracked?: boolean;
}

export interface Material extends MaterialBase {
  id: string;
  uuid: string;
  specs: MaterialSpecs;
  supply: MaterialSupplyInfo;
  stock: MaterialStockSettings;
  attachments?: Attachment[];
  createdAt: string;
  updatedAt: string;
}

export interface MaterialDraft extends MaterialBase {
  specs: MaterialSpecs;
  supply: MaterialSupplyInfo;
  stock: MaterialStockSettings;
  attachments?: Attachment[];
}

export interface MaterialReference {
  id: string;
  code: string;
  name: string;
  group: MaterialGroup;
  unit: UnitOfMeasure;
  color?: string;
}

export interface MaterialsListItem {
  id: string;
  code: string;
  name: string;
  group: MaterialGroup;
  subgroup?: string;
  unit: UnitOfMeasure;
  price?: number;
  supplierName?: string;
  leadTimeDays?: number;
  isActive: boolean;
  isCritical?: boolean;
  updatedAt: string;
}

export interface MaterialsListQuery extends ListQuery {
  group?: MaterialGroup;
  subgroup?: string;
  isActive?: boolean;
  isCritical?: boolean;
  priceMin?: number;
  priceMax?: number;
}

export type MaterialsListResult = PaginatedResult<MaterialsListItem>;
