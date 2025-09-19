"""
Warehouse models for KRAI System v0.6
Inventory and stock management
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, String, Integer, Numeric, Boolean, ForeignKey, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class WarehouseStock(BaseModel):
    """Складские остатки"""
    __tablename__ = "warehouse_stock"

    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"))
    warehouse_code: Mapped[Optional[str]] = mapped_column(String(20))
    location: Mapped[Optional[str]] = mapped_column(String(50))

    quantity: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 3))
    reserved_qty: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 3))
    unit: Mapped[str] = mapped_column(String(20))

    batch_number: Mapped[Optional[str]] = mapped_column(String(50))
    receipt_date: Mapped[Optional[date]] = mapped_column(Date)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    purchase_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))

    last_receipt_date: Mapped[Optional[date]] = mapped_column(Date)
    last_issue_date: Mapped[Optional[date]] = mapped_column(Date)

    # Связи
    material: Mapped["Material"] = relationship("Material", back_populates="warehouse_stocks")

    @property
    def available(self) -> Decimal:
        """Доступное количество (без резерва)"""
        qty = self.quantity or Decimal('0')
        reserved = self.reserved_qty or Decimal('0')
        return qty - reserved

    @property
    def status(self) -> str:
        """Статус складского остатка"""
        qty = self.quantity or Decimal('0')
        if qty < Decimal('100'):
            return "CRITICAL"
        elif qty < Decimal('500'):
            return "LOW"
        return "OK"


class StockTransaction(BaseModel):
    """Транзакции по складу"""
    __tablename__ = "stock_transactions"

    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id"))
    warehouse_stock_id: Mapped[int] = mapped_column(ForeignKey("warehouse_stock.id"))

    transaction_type: Mapped[str] = mapped_column(String(20))  # RECEIPT, ISSUE, TRANSFER, ADJUSTMENT
    quantity: Mapped[Decimal] = mapped_column(Numeric(15, 3))
    unit: Mapped[str] = mapped_column(String(20))

    reference_number: Mapped[Optional[str]] = mapped_column(String(50))  # номер документа
    reference_type: Mapped[Optional[str]] = mapped_column(String(50))  # ORDER, PURCHASE, MANUAL

    notes: Mapped[Optional[str]] = mapped_column(String(500))
    performed_by: Mapped[Optional[str]] = mapped_column(String(100))

    # Связи
    material: Mapped["Material"] = relationship("Material")
    warehouse_stock: Mapped["WarehouseStock"] = relationship("WarehouseStock")


# Импорт для связей
from .materials import Material