# krai_system/models/models.py
from sqlmodel import Field, Column, JSON
from typing import Optional, Dict, Any, List
from decimal import Decimal
from .base import Base

class Model(Base, table=True):
    """Модель обуви"""
    __tablename__ = "models"
    
    # Основные поля
    article: str = Field(unique=True, index=True)
    name: str = Field(index=True)
    
    # Классификация
    gender: Optional[str] = Field(default=None)
    model_type: Optional[str] = Field(default=None)
    category: Optional[str] = Field(default=None)
    
    # Технические характеристики
    last_code: Optional[str] = Field(default=None)
    last_type: Optional[str] = Field(default=None)  # Ботиночная, Туфельная
    pattern_size_range: Optional[str] = Field(default=None)  # Размерный ряд лекал: 37-48
    assembly_type: Optional[str] = Field(default=None)  # ЗНК, Ручная, Клеевая
    closure_type: Optional[str] = Field(default=None)
    sole_type: Optional[str] = Field(default=None)
    default_upper_material: Optional[str] = Field(default=None)  # Материал верха по умолчанию
    
    # Размерный ряд
    size_min: int = Field(default=36)
    size_max: int = Field(default=46)
    
    # Себестоимость (вычисляемые поля в БД)
    material_cost: Decimal = Field(default=Decimal(0))
    labor_cost: Decimal = Field(default=Decimal(0))
    overhead_cost: Decimal = Field(default=Decimal(0))
    
    # Цены
    retail_price: Decimal = Field(default=Decimal(0))
    wholesale_price: Decimal = Field(default=Decimal(0))
    
    # JSONB поля
    properties: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    photos: List[str] = Field(default=[], sa_column=Column(JSON))
    
    # Статус
    is_active: bool = Field(default=True)