# krai_system/models/mrp.py
from sqlmodel import Field, Column, JSON, Enum, SQLModel
from typing import Optional, Dict, Any, List
from decimal import Decimal
from datetime import date
from enum import Enum as PyEnum

class ScheduleStatus(PyEnum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"

class PurchaseStatus(PyEnum):
    PENDING = "pending"
    ORDERED = "ordered"
    RECEIVED = "received"
    CANCELLED = "cancelled"

class ProductionSchedule(SQLModel, table=True):
    """График производства"""
    __tablename__ = "production_schedule"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="production_orders.id", unique=True)
    scheduled_date: date = Field(index=True)
    capacity_used: int = Field(default=0)
    workshop: Optional[str] = Field(default=None)
    status: ScheduleStatus = Field(
        default=ScheduleStatus.PLANNED,
        sa_column=Column(Enum(ScheduleStatus))
    )

class PurchasePlan(SQLModel, table=True):
    """План закупок"""
    __tablename__ = "purchase_plan"

    id: Optional[int] = Field(default=None, primary_key=True)
    material_id: Optional[int] = Field(foreign_key="materials.id", default=None)
    material_name: Optional[str] = Field(default=None)
    required_qty: Decimal = Field(default=Decimal(0))
    available_qty: Decimal = Field(default=Decimal(0))
    deficit_qty: Decimal = Field(default=Decimal(0))
    order_refs: List[str] = Field(
        default=[],
        sa_column=Column(JSON),
        description="Ссылки на заказы"
    )
    supplier: Optional[str] = Field(default=None)
    planned_date: Optional[date] = Field(default=None)
    status: PurchaseStatus = Field(
        default=PurchaseStatus.PENDING,
        sa_column=Column(Enum(PurchaseStatus))
    )
    notes: Optional[str] = Field(default=None)