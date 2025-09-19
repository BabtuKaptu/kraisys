"""
Materials models for KRAI System v0.6
Normalized materials and related tables
"""

from decimal import Decimal
from typing import List, Optional
from enum import Enum as PyEnum

from sqlalchemy import Column, String, Integer, Numeric, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class MaterialGroup(PyEnum):
    """Группы материалов"""
    LEATHER = "LEATHER"
    SOLE = "SOLE"
    HARDWARE = "HARDWARE"
    LINING = "LINING"
    CHEMICAL = "CHEMICAL"
    PACKAGING = "PACKAGING"


class Material(BaseModel):
    """Материалы - основная таблица"""
    __tablename__ = "materials"

    # Основные поля
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)

    # Классификация
    group_type: Mapped[MaterialGroup] = mapped_column(Enum(MaterialGroup))

    # Единицы измерения
    unit: Mapped[str] = mapped_column(String(20), default="шт")

    # Цены
    price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))

    # Поставщик
    supplier_name: Mapped[Optional[str]] = mapped_column(String(255))
    lead_time_days: Mapped[Optional[int]] = mapped_column(Integer)

    # Складские параметры
    safety_stock: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 3))
    reorder_point: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 3))

    # Статус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Связи
    properties: Mapped[List["MaterialProperty"]] = relationship(
        "MaterialProperty", back_populates="material", cascade="all, delete-orphan"
    )
    warehouse_stocks: Mapped[List["WarehouseStock"]] = relationship(
        "WarehouseStock", back_populates="material"
    )


class MaterialProperty(BaseModel):
    """Дополнительные свойства материала - нормализованная таблица"""
    __tablename__ = "material_properties"

    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"))
    property_name: Mapped[str] = mapped_column(String(100))  # color, thickness, quality
    property_value: Mapped[str] = mapped_column(String(255))
    property_type: Mapped[str] = mapped_column(String(50))  # string, number, boolean

    # Связи
    material: Mapped["Material"] = relationship("Material", back_populates="properties")


class CuttingPart(BaseModel):
    """Справочник деталей кроя обуви"""
    __tablename__ = "cutting_parts"

    # Уникальный код детали
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    # Название детали
    name: Mapped[str] = mapped_column(String(255), index=True)

    # Категория детали
    category: Mapped[Optional[str]] = mapped_column(String(50))
    # SOYUZKA, BEREC, ZADNIK, YAZYK, KANT, VSTAVKA, NADBLOCHNIK, REMESHOK, GOLENISCHE

    # Является ли деталью кроя (true) или покупным материалом (false)
    is_cutting: Mapped[bool] = mapped_column(Boolean, default=True)

    # Количество по умолчанию
    default_qty: Mapped[Optional[int]] = mapped_column(Integer)

    # Единица измерения
    unit: Mapped[str] = mapped_column(String(20), default="шт")

    # Примечания
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Статус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Связи
    properties: Mapped[List["CuttingPartProperty"]] = relationship(
        "CuttingPartProperty", back_populates="cutting_part", cascade="all, delete-orphan"
    )


class CuttingPartProperty(BaseModel):
    """Дополнительные свойства деталей кроя"""
    __tablename__ = "cutting_part_properties"

    cutting_part_id: Mapped[int] = mapped_column(ForeignKey("cutting_parts.id"))
    property_name: Mapped[str] = mapped_column(String(100))
    property_value: Mapped[str] = mapped_column(String(255))
    property_type: Mapped[str] = mapped_column(String(50))

    # Связи
    cutting_part: Mapped["CuttingPart"] = relationship("CuttingPart", back_populates="properties")


# Справочники для вариантов исполнения (вместо JSONB)

class PerforationType(BaseModel):
    """Типы перфорации"""
    __tablename__ = "perforation_types"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class LiningType(BaseModel):
    """Типы подкладки"""
    __tablename__ = "lining_types"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    material_id: Mapped[Optional[int]] = mapped_column(ForeignKey("materials.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Связи
    material: Mapped[Optional["Material"]] = relationship("Material")


class LastingType(BaseModel):
    """Типы затяжки"""
    __tablename__ = "lasting_types"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class SoleOption(BaseModel):
    """Варианты подошв"""
    __tablename__ = "sole_options"

    name: Mapped[str] = mapped_column(String(100))
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"))
    size_range_min: Mapped[int] = mapped_column(Integer, default=36)
    size_range_max: Mapped[int] = mapped_column(Integer, default=46)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Связи
    material: Mapped["Material"] = relationship("Material")