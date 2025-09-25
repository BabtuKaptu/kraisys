"""SQLAlchemy models for footwear domain entities (v0.6)."""

from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, generate_uuid


class Model(Base, TimestampMixin):
    __tablename__ = "models"

    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    article: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)

    gender: Mapped[Optional[str]] = mapped_column(String(20))
    model_type: Mapped[Optional[str]] = mapped_column(String(50))
    category: Mapped[Optional[str]] = mapped_column(String(50))
    collection: Mapped[Optional[str]] = mapped_column(String(100))
    season: Mapped[Optional[str]] = mapped_column(String(50))

    last_code: Mapped[Optional[str]] = mapped_column(String(50))
    last_type: Mapped[Optional[str]] = mapped_column(String(50))
    lacing_type: Mapped[Optional[str]] = mapped_column(String(50))

    size_min: Mapped[int] = mapped_column(Integer, default=36)
    size_max: Mapped[int] = mapped_column(Integer, default=46)

    retail_price: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    wholesale_price: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))

    material_cost: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    labor_cost: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    overhead_cost: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))

    description: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    default_sole_option_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("model_sole_options.sole_option_id", ondelete="SET NULL"),
        nullable=True,
    )

    perforation_options: Mapped[List["ModelPerforation"]] = relationship(
        back_populates="model", cascade="all, delete-orphan"
    )
    insole_options: Mapped[List["ModelInsoleOption"]] = relationship(
        back_populates="model", cascade="all, delete-orphan"
    )
    hardware_sets: Mapped[List["ModelHardwareSet"]] = relationship(
        back_populates="model", cascade="all, delete-orphan"
    )
    cutting_parts: Mapped[List["ModelCuttingPart"]] = relationship(
        back_populates="model", cascade="all, delete-orphan"
    )
    sole_options: Mapped[List["ModelSoleOption"]] = relationship(
        back_populates="model",
        cascade="all, delete-orphan",
        foreign_keys="ModelSoleOption.model_id",
    )
    variants: Mapped[List["ModelVariant"]] = relationship(
        back_populates="model", cascade="all, delete-orphan"
    )


class ModelPerforation(Base, TimestampMixin):
    __tablename__ = "model_perforations"

    perforation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("models.model_id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(120))
    code: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    preview_image: Mapped[Optional[str]] = mapped_column(String(400))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    model: Mapped[Model] = relationship(back_populates="perforation_options")


class ModelInsoleOption(Base, TimestampMixin):
    __tablename__ = "model_insole_options"

    insole_option_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("models.model_id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(120))
    material: Mapped[Optional[str]] = mapped_column(String(120))
    seasonality: Mapped[Optional[str]] = mapped_column(String(30))
    thickness_mm: Mapped[Optional[float]] = mapped_column(Float)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    model: Mapped[Model] = relationship(back_populates="insole_options")


class ModelHardwareSet(Base, TimestampMixin):
    __tablename__ = "model_hardware_sets"

    hardware_set_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("models.model_id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    model: Mapped[Model] = relationship(back_populates="hardware_sets")
    items: Mapped[List["ModelHardwareItem"]] = relationship(
        back_populates="hardware_set", cascade="all, delete-orphan"
    )


class ModelHardwareItem(Base, TimestampMixin):
    __tablename__ = "model_hardware_items"

    hardware_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    hardware_set_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("model_hardware_sets.hardware_set_id", ondelete="CASCADE"),
        index=True,
    )
    name: Mapped[str] = mapped_column(String(120))
    material_group: Mapped[Optional[str]] = mapped_column(String(50))
    requires_exact_selection: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    hardware_set: Mapped[ModelHardwareSet] = relationship(back_populates="items")
    compatible_materials: Mapped[List["ModelHardwareCompatibleMaterial"]] = relationship(
        back_populates="hardware_item", cascade="all, delete-orphan"
    )


class ModelHardwareCompatibleMaterial(Base):
    __tablename__ = "model_hardware_item_materials"

    link_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    hardware_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("model_hardware_items.hardware_item_id", ondelete="CASCADE"),
        index=True,
    )
    material_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("materials.material_id", ondelete="CASCADE"), index=True
    )

    hardware_item: Mapped[ModelHardwareItem] = relationship(back_populates="compatible_materials")
    material: Mapped["Material"] = relationship("Material", foreign_keys=[material_id])


class ModelCuttingPart(Base, TimestampMixin):
    __tablename__ = "model_cutting_parts"

    cutting_part_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("models.model_id", ondelete="CASCADE"), index=True
    )
    reference_part_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cutting_parts.part_id", ondelete="SET NULL"), nullable=True
    )
    material_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("materials.material_id", ondelete="SET NULL"), nullable=True
    )
    quantity: Mapped[float] = mapped_column(Float, default=0)
    consumption_per_pair: Mapped[Optional[float]] = mapped_column(Float)
    labor_cost: Mapped[Optional[float]] = mapped_column(Float)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    model: Mapped[Model] = relationship(back_populates="cutting_parts")
    reference_part: Mapped[Optional["CuttingPart"]] = relationship("CuttingPart")
    material: Mapped[Optional["Material"]] = relationship("Material", foreign_keys=[material_id])


class ModelSoleOption(Base, TimestampMixin):
    __tablename__ = "model_sole_options"

    sole_option_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("models.model_id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(120))
    material_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("materials.material_id", ondelete="SET NULL"), nullable=True
    )
    size_min: Mapped[Optional[int]] = mapped_column(Integer)
    size_max: Mapped[Optional[int]] = mapped_column(Integer)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    color: Mapped[Optional[str]] = mapped_column(String(50))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    model: Mapped[Model] = relationship(
        "Model",
        back_populates="sole_options",
        foreign_keys=[model_id],
    )
    material: Mapped[Optional["Material"]] = relationship("Material", foreign_keys=[material_id])


class ModelVariant(Base, TimestampMixin):
    __tablename__ = "model_variants"

    variant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("models.model_id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(120))
    code: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    total_material_cost: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))

    perforation_option_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("model_perforations.perforation_id", ondelete="SET NULL"), nullable=True
    )
    insole_option_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("model_insole_options.insole_option_id", ondelete="SET NULL"), nullable=True
    )
    hardware_set_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("model_hardware_sets.hardware_set_id", ondelete="SET NULL"), nullable=True
    )
    sole_option_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("model_sole_options.sole_option_id", ondelete="SET NULL"), nullable=True
    )

    model: Mapped[Model] = relationship(back_populates="variants")
    customized_cutting_parts: Mapped[List["ModelVariantCuttingPart"]] = relationship(
        back_populates="variant", cascade="all, delete-orphan"
    )


class ModelVariantCuttingPart(Base):
    __tablename__ = "model_variant_cutting_parts"

    variant_cutting_part_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    variant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("model_variants.variant_id", ondelete="CASCADE"), index=True
    )
    cutting_part_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("model_cutting_parts.cutting_part_id", ondelete="SET NULL"), nullable=True
    )
    material_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("materials.material_id", ondelete="SET NULL"), nullable=True
    )
    quantity: Mapped[float] = mapped_column(Float, default=0)

    variant: Mapped[ModelVariant] = relationship(back_populates="customized_cutting_parts")
    base_cutting_part: Mapped[Optional[ModelCuttingPart]] = relationship(
        "ModelCuttingPart", foreign_keys=[cutting_part_id]
    )
    material: Mapped[Optional["Material"]] = relationship("Material", foreign_keys=[material_id])


# Late imports at bottom to avoid circular dependencies
from .material import Material
from .reference import CuttingPart
