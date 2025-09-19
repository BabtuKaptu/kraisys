"""
Production models for KRAI System v0.6
Orders, scheduling and MRP
"""

from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional
from enum import Enum as PyEnum

from sqlalchemy import Column, String, Integer, Numeric, Boolean, ForeignKey, Date, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class OrderStatus(PyEnum):
    """Статусы заказов"""
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    IN_PRODUCTION = "in_production"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ScheduleStatus(PyEnum):
    """Статусы планирования"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"


class PurchaseStatus(PyEnum):
    """Статусы закупок"""
    PENDING = "pending"
    ORDERED = "ordered"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class ProductionOrder(BaseModel):
    """Производственные заказы"""
    __tablename__ = "production_orders"

    # Номер и даты
    order_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    order_date: Mapped[date] = mapped_column(Date, default=date.today)
    due_date: Mapped[date] = mapped_column(Date)
    completion_date: Mapped[Optional[date]] = mapped_column(Date)

    # Связи
    model_id: Mapped[int] = mapped_column(ForeignKey("models.id"))
    specification_id: Mapped[Optional[int]] = mapped_column(ForeignKey("specifications.id"))

    # Клиент
    customer_name: Mapped[Optional[str]] = mapped_column(String(255))
    customer_phone: Mapped[Optional[str]] = mapped_column(String(50))
    customer_email: Mapped[Optional[str]] = mapped_column(String(255))
    delivery_address: Mapped[Optional[str]] = mapped_column(Text)

    # Статус и приоритет
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.DRAFT)
    priority: Mapped[int] = mapped_column(Integer, default=50)

    # Финансы
    price_per_pair: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    discount_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)

    # Производство
    workshop: Mapped[Optional[str]] = mapped_column(String(100))
    master_name: Mapped[Optional[str]] = mapped_column(String(100))

    # Примечания
    notes: Mapped[Optional[str]] = mapped_column(Text)
    special_requirements: Mapped[Optional[str]] = mapped_column(Text)

    # Источник
    source: Mapped[Optional[str]] = mapped_column(String(50))  # website, phone, showroom, b2b

    # MRP поля
    leather_material_id: Mapped[Optional[int]] = mapped_column(ForeignKey("materials.id"))
    sole_material_id: Mapped[Optional[int]] = mapped_column(ForeignKey("materials.id"))
    sole_color: Mapped[Optional[str]] = mapped_column(String(50))
    planned_start_date: Mapped[Optional[date]] = mapped_column(Date)
    production_capacity_used: Mapped[int] = mapped_column(Integer, default=0)

    # Связи
    model: Mapped["Model"] = relationship("Model")
    specification: Mapped[Optional["Specification"]] = relationship("Specification")
    leather_material: Mapped[Optional["Material"]] = relationship(
        "Material", foreign_keys=[leather_material_id]
    )
    sole_material: Mapped[Optional["Material"]] = relationship(
        "Material", foreign_keys=[sole_material_id]
    )
    order_sizes: Mapped[List["OrderSize"]] = relationship(
        "OrderSize", back_populates="order", cascade="all, delete-orphan"
    )
    material_requirements: Mapped[List["OrderMaterialRequirement"]] = relationship(
        "OrderMaterialRequirement", back_populates="order", cascade="all, delete-orphan"
    )
    production_schedule: Mapped[Optional["ProductionSchedule"]] = relationship(
        "ProductionSchedule", back_populates="order", uselist=False
    )

    @property
    def total_pairs(self) -> int:
        """Общее количество пар"""
        return sum(order_size.quantity for order_size in self.order_sizes)

    @property
    def total_amount(self) -> Decimal:
        """Общая сумма заказа"""
        base_amount = self.price_per_pair * self.total_pairs
        discount = base_amount * (self.discount_percent / 100)
        return base_amount - discount


class OrderSize(BaseModel):
    """Размеры в заказе - нормализованная таблица вместо JSON"""
    __tablename__ = "order_sizes"

    order_id: Mapped[int] = mapped_column(ForeignKey("production_orders.id"))
    size: Mapped[int] = mapped_column(Integer)  # 36, 37, 38, etc.
    quantity: Mapped[int] = mapped_column(Integer)

    # Связи
    order: Mapped["ProductionOrder"] = relationship("ProductionOrder", back_populates="order_sizes")


class OrderMaterialRequirement(BaseModel):
    """Потребности в материалах для заказа - нормализованная таблица"""
    __tablename__ = "order_material_requirements"

    order_id: Mapped[int] = mapped_column(ForeignKey("production_orders.id"))
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"))

    required_quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))
    unit: Mapped[str] = mapped_column(String(20))
    notes: Mapped[Optional[str]] = mapped_column(String(255))

    # Связи
    order: Mapped["ProductionOrder"] = relationship("ProductionOrder", back_populates="material_requirements")
    material: Mapped["Material"] = relationship("Material")


class ProductionSchedule(BaseModel):
    """График производства"""
    __tablename__ = "production_schedule"

    order_id: Mapped[int] = mapped_column(ForeignKey("production_orders.id"), unique=True)
    scheduled_date: Mapped[date] = mapped_column(Date, index=True)
    capacity_used: Mapped[int] = mapped_column(Integer, default=0)
    workshop: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[ScheduleStatus] = mapped_column(Enum(ScheduleStatus), default=ScheduleStatus.PLANNED)

    # Связи
    order: Mapped["ProductionOrder"] = relationship("ProductionOrder", back_populates="production_schedule")


class PurchasePlan(BaseModel):
    """План закупок"""
    __tablename__ = "purchase_plan"

    material_id: Mapped[Optional[int]] = mapped_column(ForeignKey("materials.id"))
    material_name: Mapped[Optional[str]] = mapped_column(String(255))

    required_qty: Mapped[Decimal] = mapped_column(Numeric(15, 3), default=0)
    available_qty: Mapped[Decimal] = mapped_column(Numeric(15, 3), default=0)
    deficit_qty: Mapped[Decimal] = mapped_column(Numeric(15, 3), default=0)

    supplier: Mapped[Optional[str]] = mapped_column(String(255))
    planned_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[PurchaseStatus] = mapped_column(Enum(PurchaseStatus), default=PurchaseStatus.PENDING)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Связи
    material: Mapped[Optional["Material"]] = relationship("Material")
    order_references: Mapped[List["PurchasePlanOrderRef"]] = relationship(
        "PurchasePlanOrderRef", back_populates="purchase_plan", cascade="all, delete-orphan"
    )


class PurchasePlanOrderRef(BaseModel):
    """Ссылки на заказы в плане закупок - нормализованная таблица вместо JSON"""
    __tablename__ = "purchase_plan_order_refs"

    purchase_plan_id: Mapped[int] = mapped_column(ForeignKey("purchase_plan.id"))
    order_number: Mapped[str] = mapped_column(String(50))

    # Связи
    purchase_plan: Mapped["PurchasePlan"] = relationship("PurchasePlan", back_populates="order_references")


# Импорты для связей
from .models import Model, Specification
from .materials import Material