import { ListQuery, PaginatedResult } from './common';

export interface ReferenceItem<TType extends string = string> {
  id: string;
  code?: string;
  name: string;
  description?: string;
  type: TType;
  isActive: boolean;
  attributes?: Record<string, unknown>;
}

export interface ReferenceDraft<TType extends string = string> {
  code?: string;
  name: string;
  description?: string;
  type: TType;
  isActive: boolean;
  attributes?: Record<string, unknown>;
}

export interface ReferenceListQuery extends ListQuery {
  type?: string;
  isActive?: boolean;
}

export type ReferenceListResult = PaginatedResult<ReferenceItem>;
