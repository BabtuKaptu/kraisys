export type Gender = 'MALE' | 'FEMALE' | 'UNISEX' | 'KIDS';

export type ModelCategory =
  | 'SNEAKERS'
  | 'SHOES'
  | 'BOOTS'
  | 'SANDALS'
  | 'SLIPPERS'
  | 'LOAFERS'
  | 'OXFORDS'
  | 'DERBY'
  | 'OTHER';

export type ModelType = 'SPORT' | 'CASUAL' | 'FORMAL' | 'WORK' | 'OUTDOOR' | 'SPECIAL';

export type Season = 'SPRING_SUMMER' | 'FALL_WINTER' | 'ALL_SEASON' | 'DEMISEASON' | 'CUSTOM';

export type LacingType =
  | 'GLUED'
  | 'STITCHED'
  | 'HANDMADE'
  | 'COMBINED'
  | 'CEMENTED'
  | 'LASTING';

export type MaterialGroup =
  | 'LEATHER'
  | 'SOLE'
  | 'HARDWARE'
  | 'LINING'
  | 'CHEMICAL'
  | 'PACKAGING'
  | 'TEXTILE'
  | 'ADHESIVE'
  | 'OTHER';

export type UnitOfMeasure =
  | 'шт'
  | 'пар'
  | 'компл'
  | 'уп'
  | 'дм²'
  | 'м²'
  | 'м'
  | 'кг'
  | 'г'
  | 'л'
  | 'мл';

export interface Attachment {
  id: string;
  fileName: string;
  fileType: string;
  url: string;
  uploadedAt: string;
}

export interface KPIBlock {
  title: string;
  value: number | string;
  trend?: 'up' | 'down' | 'neutral';
  helperText?: string;
}

export interface PaginatedResult<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

export interface ListQuery {
  page?: number;
  pageSize?: number;
  search?: string;
  filters?: Record<string, unknown>;
}
