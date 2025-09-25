import { Attachment, Gender, KPIBlock, LacingType, ListQuery, MaterialGroup, ModelCategory, ModelType, PaginatedResult, Season } from './common';
import { MaterialReference } from './material';
import { ReferenceItem } from './reference';

export interface PerforationOption {
  id?: string;
  name: string;
  code?: string;
  description?: string;
  previewImage?: string;
  isDefault?: boolean;
  isActive: boolean;
}

export interface InsoleOption {
  id?: string;
  name: string;
  material?: string;
  seasonality?: Season;
  thicknessMm?: number;
  isDefault?: boolean;
  isActive: boolean;
}

export interface HardwareItemOption {
  id?: string;
  name: string;
  materialGroup: MaterialGroup;
  compatibleMaterials: MaterialReference[];
  requiresExactSelection?: boolean; // уточняется в заказе
  notes?: string;
}

export interface HardwareSet {
  id?: string;
  name: string;
  description?: string;
  items: HardwareItemOption[];
  isDefault?: boolean;
  isActive: boolean;
}

export interface ModelSuperBOM {
  perforationOptions: PerforationOption[];
  insoleOptions: InsoleOption[];
  hardwareSets: HardwareSet[];
}

export interface CuttingPartUsage {
  id?: string;
  part: ReferenceItem<'cutting_part'>;
  material: MaterialReference;
  quantity: number;
  consumptionPerPair?: number;
  laborCost?: number;
  notes?: string;
}

export interface SoleOption {
  id?: string;
  name: string;
  material: MaterialReference;
  sizeMin: number;
  sizeMax: number;
  isDefault?: boolean;
  color?: string;
  notes?: string;
}

export interface ModelVariantSpecification {
  perforationOptionId?: string;
  insoleOptionId?: string;
  hardwareSetId?: string;
  soleOptionId?: string;
  customizedCuttingParts?: CuttingPartUsage[];
  customizedHardware?: HardwareItemOption[];
  notes?: string;
}

export interface ModelVariant {
  id: string;
  modelId: string;
  name: string;
  code?: string;
  isDefault?: boolean;
  status: 'ACTIVE' | 'INACTIVE';
  specification: ModelVariantSpecification;
  totalMaterialCost?: number;
  createdAt: string;
  updatedAt: string;
}

export interface ModelBase {
  name: string;
  article: string;
  gender: Gender;
  modelType: ModelType;
  category: ModelCategory;
  collection?: string;
  season?: Season;
  lastCode?: string;
  lastType?: string;
  sizeMin: number;
  sizeMax: number;
  lacingType?: LacingType;
  defaultSoleOptionId?: string;
  isActive: boolean;
  retailPrice: number;
  wholesalePrice: number;
  materialCost?: number;
  laborCost?: number;
  overheadCost?: number;
  description?: string;
}

export interface ModelDraft extends ModelBase {
  superBom: ModelSuperBOM;
  cuttingParts: CuttingPartUsage[];
  soleOptions: SoleOption[];
  notes?: string;
  attachments?: Attachment[];
}

export interface Model extends ModelDraft {
  id: string;
  uuid: string;
  variants: ModelVariant[];
  createdAt: string;
  updatedAt: string;
  kpis?: KPIBlock[];
}

export interface ModelListItem {
  id: string;
  article: string;
  name: string;
  gender: Gender;
  modelType: ModelType;
  category: ModelCategory;
  sizeRange: string;
  defaultSole?: string;
  status: 'ACTIVE' | 'INACTIVE';
  updatedAt: string;
}

export interface ModelsListQuery extends ListQuery {
  gender?: Gender;
  modelType?: ModelType;
  category?: ModelCategory;
  status?: 'ACTIVE' | 'INACTIVE';
}

export type ModelsListResult = PaginatedResult<ModelListItem>;

export interface ModelVariantDraft extends Omit<ModelVariant, 'id' | 'modelId' | 'createdAt' | 'updatedAt'> {
  id?: string;
}
