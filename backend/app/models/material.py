"""SQLAlchemy models for materials and related entities."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Boolean, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin, generate_uuid


class Material(Base, TimestampMixin):
    __tablename__ = "materials"

    material_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    name_en: Mapped[Optional[str]] = mapped_column(String(200))

    group: Mapped[str] = mapped_column(String(40))
    subgroup: Mapped[Optional[str]] = mapped_column(String(80))
    material_type: Mapped[Optional[str]] = mapped_column(String(80))
    color: Mapped[Optional[str]] = mapped_column(String(60))

    texture: Mapped[Optional[str]] = mapped_column(String(80))
    thickness_mm: Mapped[Optional[float]] = mapped_column(Numeric(10, 3))
    density: Mapped[Optional[float]] = mapped_column(Numeric(10, 3))

    unit_primary: Mapped[str] = mapped_column(String(20))
    unit_secondary: Mapped[Optional[str]] = mapped_column(String(20))
    conversion_factor: Mapped[Optional[float]] = mapped_column(Numeric(10, 4))
    specs_notes: Mapped[Optional[str]] = mapped_column(Text)

    price: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    currency: Mapped[Optional[str]] = mapped_column(String(10))
    supplier_name: Mapped[Optional[str]] = mapped_column(String(120))
    supplier_code: Mapped[Optional[str]] = mapped_column(String(60))
    lead_time_days: Mapped[Optional[int]] = mapped_column(Integer)
    min_order_qty: Mapped[Optional[float]] = mapped_column(Numeric(12, 3))
    order_multiplicity: Mapped[Optional[float]] = mapped_column(Numeric(12, 3))
    storage_conditions: Mapped[Optional[str]] = mapped_column(Text)
    warranty_months: Mapped[Optional[int]] = mapped_column(Integer)

    safety_stock: Mapped[Optional[float]] = mapped_column(Numeric(12, 3))
    reorder_point: Mapped[Optional[float]] = mapped_column(Numeric(12, 3))
    max_stock: Mapped[Optional[float]] = mapped_column(Numeric(12, 3))
    warehouse_code: Mapped[Optional[str]] = mapped_column(String(40))
    lot_tracked: Mapped[bool] = mapped_column(Boolean, default=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_critical: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

