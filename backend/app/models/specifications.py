"""
Specification models for KRAI System v0.6
Normalized specification tables instead of JSONB
"""

from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, String, Integer, Numeric, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class SpecificationCuttingPart(BaseModel):
    """Детали кроя в спецификации - нормализованная таблица"""
    __tablename__ = "specification_cutting_parts"

    specification_id: Mapped[int] = mapped_column(ForeignKey("specifications.id"))
    cutting_part_id: Mapped[int] = mapped_column(ForeignKey("cutting_parts.id"))

    quantity: Mapped[int] = mapped_column(Integer)
    note: Mapped[Optional[str]] = mapped_column(Text)

    # Связи
    specification: Mapped["Specification"] = relationship(
        "Specification", back_populates="cutting_parts"
    )
    cutting_part: Mapped["CuttingPart"] = relationship("CuttingPart")


class SpecificationHardware(BaseModel):
    """Фурнитура в спецификации - нормализованная таблица"""
    __tablename__ = "specification_hardware"

    specification_id: Mapped[int] = mapped_column(ForeignKey("specifications.id"))
    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"))

    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 3))
    description: Mapped[Optional[str]] = mapped_column(String(255))  # было "file"
    unit: Mapped[str] = mapped_column(String(20), default="шт")

    # Связи
    specification: Mapped["Specification"] = relationship(
        "Specification", back_populates="hardware_items"
    )
    material: Mapped["Material"] = relationship("Material")


class SpecificationVariantOption(BaseModel):
    """Варианты исполнения спецификации - нормализованная таблица"""
    __tablename__ = "specification_variant_options"

    specification_id: Mapped[int] = mapped_column(ForeignKey("specifications.id"))

    option_type: Mapped[str] = mapped_column(String(50))  # perforation, lining, sole
    option_name: Mapped[str] = mapped_column(String(255))

    # Ссылки на справочники
    perforation_type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("perforation_types.id"))
    lining_type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("lining_types.id"))
    lasting_type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("lasting_types.id"))
    sole_option_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sole_options.id"))

    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    # Связи
    specification: Mapped["Specification"] = relationship(
        "Specification", back_populates="variant_options"
    )
    perforation_type: Mapped[Optional["PerforationType"]] = relationship("PerforationType")
    lining_type: Mapped[Optional["LiningType"]] = relationship("LiningType")
    lasting_type: Mapped[Optional["LastingType"]] = relationship("LastingType")
    sole_option: Mapped[Optional["SoleOption"]] = relationship("SoleOption")


# Импорты для связей
from .models import Specification
from .materials import CuttingPart, Material, PerforationType, LiningType, LastingType, SoleOption