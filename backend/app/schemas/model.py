"""Pydantic schemas for footwear models aligned with the frontend structure."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .common import Attachment, KPIBlock, ListQuery, PaginatedResult
from .material import MaterialReference
from .reference import ReferenceItem


class PerforationOption(BaseModel):
    id: Optional[UUID] = None
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    previewImage: Optional[str] = None
    isDefault: bool = False
    isActive: bool = True


class InsoleOption(BaseModel):
    id: Optional[UUID] = None
    name: str
    material: Optional[str] = None
    seasonality: Optional[str] = None
    thicknessMm: Optional[float] = None
    isDefault: bool = False
    isActive: bool = True


class HardwareItemOption(BaseModel):
    id: Optional[UUID] = None
    name: str
    materialGroup: Optional[str] = None
    compatibleMaterials: List[MaterialReference] = Field(default_factory=list)
    requiresExactSelection: bool = False
    notes: Optional[str] = None


class HardwareSet(BaseModel):
    id: Optional[UUID] = None
    name: str
    description: Optional[str] = None
    items: List[HardwareItemOption] = Field(default_factory=list)
    isDefault: bool = False
    isActive: bool = True


class ModelSuperBOM(BaseModel):
    perforationOptions: List[PerforationOption] = Field(default_factory=list)
    insoleOptions: List[InsoleOption] = Field(default_factory=list)
    hardwareSets: List[HardwareSet] = Field(default_factory=list)


class CuttingPartUsage(BaseModel):
    id: Optional[UUID] = None
    part: Optional[ReferenceItem] = None
    material: Optional[MaterialReference] = None
    quantity: float = 0
    consumptionPerPair: Optional[float] = None
    laborCost: Optional[float] = None
    notes: Optional[str] = None


class SoleOption(BaseModel):
    id: Optional[UUID] = None
    name: str
    material: Optional[MaterialReference] = None
    sizeMin: Optional[int] = None
    sizeMax: Optional[int] = None
    isDefault: bool = False
    color: Optional[str] = None
    notes: Optional[str] = None


class ModelVariantSpecification(BaseModel):
    perforationOptionId: Optional[UUID] = None
    insoleOptionId: Optional[UUID] = None
    hardwareSetId: Optional[UUID] = None
    soleOptionId: Optional[UUID] = None
    customizedCuttingParts: List[CuttingPartUsage] = Field(default_factory=list)
    notes: Optional[str] = None


class ModelVariant(BaseModel):
    id: Optional[UUID] = None
    modelId: Optional[UUID] = None
    name: str
    code: Optional[str] = None
    isDefault: bool = False
    status: str = "ACTIVE"
    specification: ModelVariantSpecification
    totalMaterialCost: Optional[float] = None
    createdAt: datetime
    updatedAt: datetime


class ModelBase(BaseModel):
    name: str
    article: str
    gender: Optional[str] = None
    modelType: Optional[str] = None
    category: Optional[str] = None
    collection: Optional[str] = None
    season: Optional[str] = None
    lastCode: Optional[str] = None
    lastType: Optional[str] = None
    sizeMin: int = 36
    sizeMax: int = 46
    lacingType: Optional[str] = None
    defaultSoleOptionId: Optional[UUID] = None
    isActive: bool = True
    retailPrice: Optional[float] = None
    wholesalePrice: Optional[float] = None
    materialCost: Optional[float] = None
    laborCost: Optional[float] = None
    overheadCost: Optional[float] = None
    description: Optional[str] = None


class ModelDraft(ModelBase):
    superBom: ModelSuperBOM = Field(default_factory=ModelSuperBOM)
    cuttingParts: List[CuttingPartUsage] = Field(default_factory=list)
    soleOptions: List[SoleOption] = Field(default_factory=list)
    notes: Optional[str] = None
    attachments: List[Attachment] = Field(default_factory=list)


class Model(ModelDraft):
    class Config:
        protected_namespaces = ()
    id: UUID
    uuid: UUID
    variants: List[ModelVariant] = Field(default_factory=list)
    createdAt: datetime
    updatedAt: datetime
    kpis: List[KPIBlock] = Field(default_factory=list)


class ModelListItem(BaseModel):
    id: UUID
    article: str
    name: str
    gender: Optional[str] = None
    modelType: Optional[str] = None
    category: Optional[str] = None
    sizeRange: str
    defaultSole: Optional[str] = None
    status: str
    updatedAt: datetime


class ModelsListQuery(ListQuery):
    gender: Optional[str] = None
    modelType: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None


class ModelsListResult(PaginatedResult[ModelListItem]):
    pass


class ModelResponse(Model):
    pass


class ModelCreateRequest(ModelDraft):
    pass


class ModelUpdateRequest(ModelDraft):
    pass
