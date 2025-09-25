"""Warehouse schemas aligned with frontend expectations."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .common import ListQuery, PaginatedResult
from .material import MaterialReference


class WarehouseStock(BaseModel):
    id: UUID
    material: MaterialReference
    batchNumber: Optional[str] = None
    warehouseCode: str
    location: Optional[str] = None
    quantity: float
    reservedQuantity: float = 0
    unit: str
    purchasePrice: Optional[float] = None
    receiptDate: Optional[datetime] = None
    expiryDate: Optional[datetime] = None
    lastReceiptDate: Optional[datetime] = None
    lastIssueDate: Optional[datetime] = None
    notes: Optional[str] = None
    availableQuantity: float
    status: str
    totalValue: Optional[float] = None
    updatedAt: datetime


class WarehouseStockListItem(WarehouseStock):
    pass


class WarehouseListQuery(ListQuery):
    warehouseCode: Optional[str] = None
    status: Optional[str] = None
    showArchived: bool = False


class WarehouseListResult(PaginatedResult[WarehouseStockListItem]):
    pass


class WarehouseReceiptLine(BaseModel):
    materialId: UUID
    quantity: float
    unit: str
    price: Optional[float] = None
    warehouseCode: str
    location: Optional[str] = None
    batchNumber: Optional[str] = None
    receiptDate: Optional[datetime] = None
    comments: Optional[str] = None


class WarehouseReceiptDraft(BaseModel):
    referenceNumber: Optional[str] = None
    supplier: Optional[str] = None
    lines: List[WarehouseReceiptLine] = Field(default_factory=list)


class WarehouseIssueLine(BaseModel):
    stockId: UUID
    quantity: float
    unit: str
    reason: str
    orderReference: Optional[str] = None
    comments: Optional[str] = None


class WarehouseIssueDraft(BaseModel):
    lines: List[WarehouseIssueLine] = Field(default_factory=list)


class WarehouseInventoryLine(BaseModel):
    stockId: UUID
    systemQuantity: float
    countedQuantity: float
    unit: str
    difference: float


class WarehouseInventoryDraft(BaseModel):
    lines: List[WarehouseInventoryLine] = Field(default_factory=list)
    performedAt: Optional[datetime] = None
    responsible: Optional[str] = None

