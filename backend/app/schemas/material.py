"""Pydantic schemas for materials."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .common import Attachment, ListQuery, PaginatedResult


class MaterialSpecs(BaseModel):
    texture: Optional[str] = None
    thicknessMm: Optional[float] = None
    density: Optional[float] = None
    unitPrimary: str
    unitSecondary: Optional[str] = None
    conversionFactor: Optional[float] = None
    notes: Optional[str] = None


class MaterialSupplyInfo(BaseModel):
    price: Optional[float] = None
    currency: Optional[str] = None
    supplierName: Optional[str] = None
    supplierCode: Optional[str] = None
    leadTimeDays: Optional[int] = None
    minOrderQty: Optional[float] = None
    orderMultiplicity: Optional[float] = None
    storageConditions: Optional[str] = None
    warrantyMonths: Optional[int] = None


class MaterialStockSettings(BaseModel):
    safetyStock: Optional[float] = None
    reorderPoint: Optional[float] = None
    maxStock: Optional[float] = None
    warehouseCode: Optional[str] = None
    lotTracked: bool = False


class MaterialBase(BaseModel):
    code: str
    name: str
    nameEn: Optional[str] = None
    group: str
    subgroup: Optional[str] = None
    materialType: Optional[str] = None
    color: Optional[str] = None
    isActive: bool = True
    isCritical: bool = False
    description: Optional[str] = None
    specs: MaterialSpecs = Field(default_factory=lambda: MaterialSpecs(unitPrimary="шт"))
    supply: MaterialSupplyInfo = Field(default_factory=MaterialSupplyInfo)
    stock: MaterialStockSettings = Field(default_factory=MaterialStockSettings)


class MaterialDraft(MaterialBase):
    attachments: List[Attachment] = Field(default_factory=list)


class Material(MaterialDraft):
    id: UUID
    uuid: UUID
    createdAt: datetime
    updatedAt: datetime


class MaterialReference(BaseModel):
    id: UUID
    code: str
    name: str
    group: str
    unit: str
    color: Optional[str] = None


class MaterialsListItem(BaseModel):
    id: UUID
    code: str
    name: str
    group: str
    subgroup: Optional[str] = None
    unit: str
    price: Optional[float] = None
    supplierName: Optional[str] = None
    leadTimeDays: Optional[int] = None
    isActive: bool
    isCritical: bool = False
    updatedAt: datetime


class MaterialsListQuery(ListQuery):
    group: Optional[str] = None
    subgroup: Optional[str] = None
    isActive: Optional[bool] = None
    isCritical: Optional[bool] = None
    priceMin: Optional[float] = None
    priceMax: Optional[float] = None


class MaterialsListResult(PaginatedResult[MaterialsListItem]):
    pass


class MaterialResponse(Material):
    pass


class MaterialCreateRequest(MaterialDraft):
    pass


class MaterialUpdateRequest(MaterialDraft):
    pass
