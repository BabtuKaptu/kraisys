"""Reference tables used across the application."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Boolean, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin, generate_uuid


class ReferenceItem(Base, TimestampMixin):
    __tablename__ = "reference_items"

    reference_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    type: Mapped[str] = mapped_column(String(40), index=True)
    code: Mapped[Optional[str]] = mapped_column(String(60))
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    attributes: Mapped[Optional[dict]] = mapped_column(JSON)


class CuttingPart(Base, TimestampMixin):
    __tablename__ = "cutting_parts"

    part_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    category: Mapped[Optional[str]] = mapped_column(String(80))
    unit: Mapped[str] = mapped_column(String(20), default="шт")
    notes: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

