"""SQLAlchemy models for warehouse domain."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, generate_uuid
from .material import Material


class WarehouseStock(Base):
    __tablename__ = "warehouse_stock"

    stock_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    material_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("materials.material_id", ondelete="CASCADE"), index=True
    )
    warehouse_code: Mapped[str] = mapped_column(String(40))
    location: Mapped[Optional[str]] = mapped_column(String(40))
    quantity: Mapped[Optional[float]] = mapped_column(Numeric(15, 3))
    reserved_quantity: Mapped[Optional[float]] = mapped_column(Numeric(15, 3))
    unit: Mapped[str] = mapped_column(String(20))
    purchase_price: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    batch_number: Mapped[Optional[str]] = mapped_column(String(50))
    receipt_date: Mapped[Optional[date]] = mapped_column(Date)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    last_receipt_date: Mapped[Optional[date]] = mapped_column(Date)
    last_issue_date: Mapped[Optional[date]] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    material: Mapped[Material] = relationship()


class WarehouseTransaction(Base):
    __tablename__ = "warehouse_transactions"

    transaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    stock_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("warehouse_stock.stock_id", ondelete="CASCADE"), index=True
    )
    material_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("materials.material_id", ondelete="CASCADE"), index=True
    )
    transaction_type: Mapped[str] = mapped_column(String(20))
    quantity: Mapped[float] = mapped_column(Numeric(15, 3))
    unit: Mapped[str] = mapped_column(String(20))
    warehouse_from: Mapped[Optional[str]] = mapped_column(String(40))
    warehouse_to: Mapped[Optional[str]] = mapped_column(String(40))
    reference_number: Mapped[Optional[str]] = mapped_column(String(80))
    reference_type: Mapped[Optional[str]] = mapped_column(String(40))
    reason: Mapped[Optional[str]] = mapped_column(String(80))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    performed_by: Mapped[Optional[str]] = mapped_column(String(80))
    performed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
