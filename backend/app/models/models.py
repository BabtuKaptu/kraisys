"""
Normalized Models for KRAI System v0.6
Footwear models and their specifications
"""

from decimal import Decimal
from typing import List, Optional

from sqlalchemy import Column, String, Integer, Numeric, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class Model(BaseModel):
    """Модель обуви - основная таблица"""
    __tablename__ = "models"

    # Основные поля
    article: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)

    # Классификация
    gender: Mapped[Optional[str]] = mapped_column(String(20))  # MALE, FEMALE, UNISEX
    model_type: Mapped[Optional[str]] = mapped_column(String(50))  # SPORT, CASUAL, FORMAL
    category: Mapped[Optional[str]] = mapped_column(String(50))  # BOOTS, SHOES, SNEAKERS

    # Технические характеристики
    last_code: Mapped[Optional[str]] = mapped_column(String(50))
    last_type: Mapped[Optional[str]] = mapped_column(String(50))  # Ботиночная, Туфельная
    pattern_size_range: Mapped[Optional[str]] = mapped_column(String(20))  # 37-48
    assembly_type: Mapped[Optional[str]] = mapped_column(String(50))  # ЗНК, Ручная, Клеевая
    closure_type: Mapped[Optional[str]] = mapped_column(String(50))
    sole_type: Mapped[Optional[str]] = mapped_column(String(50))
    default_upper_material: Mapped[Optional[str]] = mapped_column(String(100))

    # Размерный ряд
    size_min: Mapped[int] = mapped_column(Integer, default=36)
    size_max: Mapped[int] = mapped_column(Integer, default=46)

    # Себестоимость
    material_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    labor_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    overhead_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)

    # Цены
    retail_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    wholesale_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)

    # Статус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Связи
    specifications: Mapped[List["Specification"]] = relationship(
        "Specification", back_populates="model", cascade="all, delete-orphan"
    )
    model_photos: Mapped[List["ModelPhoto"]] = relationship(
        "ModelPhoto", back_populates="model", cascade="all, delete-orphan"
    )
    model_properties: Mapped[List["ModelProperty"]] = relationship(
        "ModelProperty", back_populates="model", cascade="all, delete-orphan"
    )


class ModelPhoto(BaseModel):
    """Фотографии модели - нормализованная таблица вместо JSON"""
    __tablename__ = "model_photos"

    model_id: Mapped[int] = mapped_column(ForeignKey("models.id"))
    photo_url: Mapped[str] = mapped_column(String(500))
    photo_type: Mapped[str] = mapped_column(String(50))  # main, gallery, technical
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Связи
    model: Mapped["Model"] = relationship("Model", back_populates="model_photos")


class ModelProperty(BaseModel):
    """Дополнительные свойства модели - нормализованная таблица вместо JSONB"""
    __tablename__ = "model_properties"

    model_id: Mapped[int] = mapped_column(ForeignKey("models.id"))
    property_name: Mapped[str] = mapped_column(String(100))  # color, season, style, etc.
    property_value: Mapped[str] = mapped_column(String(255))
    property_type: Mapped[str] = mapped_column(String(50))  # string, number, boolean

    # Связи
    model: Mapped["Model"] = relationship("Model", back_populates="model_properties")


class SizeRun(BaseModel):
    """Размерные ряды для производства - из таблицы Excel"""
    __tablename__ = "size_runs"

    model_id: Mapped[int] = mapped_column(ForeignKey("models.id"))
    color_code: Mapped[str] = mapped_column(String(50))
    color_name: Mapped[str] = mapped_column(String(100))

    # Размеры 35-49 как отдельные поля для удобства
    size_35: Mapped[int] = mapped_column(Integer, default=0)
    size_36: Mapped[int] = mapped_column(Integer, default=0)
    size_37: Mapped[int] = mapped_column(Integer, default=0)
    size_38: Mapped[int] = mapped_column(Integer, default=0)
    size_39: Mapped[int] = mapped_column(Integer, default=0)
    size_40: Mapped[int] = mapped_column(Integer, default=0)
    size_41: Mapped[int] = mapped_column(Integer, default=0)
    size_42: Mapped[int] = mapped_column(Integer, default=0)
    size_43: Mapped[int] = mapped_column(Integer, default=0)
    size_44: Mapped[int] = mapped_column(Integer, default=0)
    size_45: Mapped[int] = mapped_column(Integer, default=0)
    size_46: Mapped[int] = mapped_column(Integer, default=0)
    size_47: Mapped[int] = mapped_column(Integer, default=0)
    size_48: Mapped[int] = mapped_column(Integer, default=0)
    size_49: Mapped[int] = mapped_column(Integer, default=0)

    # Общее количество
    total_pairs: Mapped[int] = mapped_column(Integer, default=0)

    # Связи
    model: Mapped["Model"] = relationship("Model")


class Specification(BaseModel):
    """Спецификации модели - нормализованная структура"""
    __tablename__ = "specifications"

    model_id: Mapped[int] = mapped_column(ForeignKey("models.id"))

    # Версионирование
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Название варианта
    variant_name: Mapped[Optional[str]] = mapped_column(String(255))
    variant_code: Mapped[Optional[str]] = mapped_column(String(50))

    # Расчетные поля
    total_material_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    total_labor_hours: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=0)

    # Связи
    model: Mapped["Model"] = relationship("Model", back_populates="specifications")
    cutting_parts: Mapped[List["SpecificationCuttingPart"]] = relationship(
        "SpecificationCuttingPart", back_populates="specification", cascade="all, delete-orphan"
    )
    hardware_items: Mapped[List["SpecificationHardware"]] = relationship(
        "SpecificationHardware", back_populates="specification", cascade="all, delete-orphan"
    )
    variant_options: Mapped[List["SpecificationVariantOption"]] = relationship(
        "SpecificationVariantOption", back_populates="specification", cascade="all, delete-orphan"
    )