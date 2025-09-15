# krai_system/models/production_orders.py
from sqlmodel import Field, Column, JSON, Enum
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import date
from enum import Enum as PyEnum
from .base import Base

class OrderStatus(PyEnum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    IN_PRODUCTION = "in_production"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ProductionOrder(Base, table=True):
    """Производственные заказы"""
    __tablename__ = "production_orders"
    
    # Номер и даты
    order_number: str = Field(unique=True, index=True)
    order_date: date = Field(default_factory=date.today)
    due_date: date
    completion_date: Optional[date] = Field(default=None)
    
    # Связи
    model_id: int = Field(foreign_key="models.id")
    specification_id: Optional[int] = Field(foreign_key="specifications.id", default=None)
    
    # Клиент
    customer_name: Optional[str] = Field(default=None)
    customer_phone: Optional[str] = Field(default=None)
    customer_email: Optional[str] = Field(default=None)
    delivery_address: Optional[str] = Field(default=None)
    
    # Размеры и количества - JSONB
    sizes: Dict[str, int] = Field(
        default={},
        sa_column=Column(JSON),
        description="Размеры и количества: {'40': 2, '41': 3, '42': 1}"
    )
    
    # Статус и приоритет
    status: OrderStatus = Field(
        default=OrderStatus.DRAFT,
        sa_column=Column(Enum(OrderStatus))
    )
    priority: int = Field(default=50)
    
    # Финансы
    price_per_pair: Decimal = Field(default=Decimal(0))
    discount_percent: Decimal = Field(default=Decimal(0))
    
    # Производство
    workshop: Optional[str] = Field(default=None)
    master_name: Optional[str] = Field(default=None)
    
    # Примечания
    notes: Optional[str] = Field(default=None)
    special_requirements: Optional[str] = Field(default=None)
    
    # Источник
    source: Optional[str] = Field(default=None)  # 'website', 'phone', 'showroom', 'b2b'

    # MRP поля
    leather_material_id: Optional[int] = Field(foreign_key="materials.id", default=None)
    sole_material_id: Optional[int] = Field(foreign_key="materials.id", default=None)
    sole_color: Optional[str] = Field(default=None)
    material_requirements: Dict[str, Any] = Field(
        default={},
        sa_column=Column(JSON),
        description="Потребности в материалах"
    )
    planned_start_date: Optional[date] = Field(default=None)
    production_capacity_used: int = Field(default=0)

    @property
    def total_pairs(self) -> int:
        """Общее количество пар"""
        return sum(self.sizes.values())
    
    @property
    def total_amount(self) -> Decimal:
        """Общая сумма заказа"""
        base_amount = self.price_per_pair * self.total_pairs
        discount = base_amount * (self.discount_percent / 100)
        return base_amount - discount