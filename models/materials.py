# krai_system/models/materials.py
from sqlmodel import Field, Column, JSON, Enum
from typing import Optional, Dict, Any
from decimal import Decimal
from enum import Enum as PyEnum
from .base import Base

class MaterialGroup(PyEnum):
    LEATHER = "LEATHER"
    SOLE = "SOLE"
    HARDWARE = "HARDWARE"
    LINING = "LINING"
    CHEMICAL = "CHEMICAL"
    PACKAGING = "PACKAGING"

class Material(Base, table=True):
    """Материалы"""
    __tablename__ = "materials"
    
    # Основные поля
    code: str = Field(unique=True, index=True)
    name: str = Field(index=True)
    
    # Классификация
    group_type: MaterialGroup = Field(sa_column=Column(Enum(MaterialGroup)))
    
    # Единицы измерения
    unit: str = Field(default="шт")
    
    # Цены
    price: Optional[Decimal] = Field(default=None)
    
    # Поставщик
    supplier_name: Optional[str] = Field(default=None)
    lead_time_days: Optional[int] = Field(default=None)
    
    # Складские параметры
    safety_stock: Optional[Decimal] = Field(default=None)
    reorder_point: Optional[Decimal] = Field(default=None)
    
    # JSONB свойства для дополнительных характеристик
    properties: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    
    # Статус
    is_active: bool = Field(default=True)