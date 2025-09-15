# kr2/models/warehouse.py
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from sqlmodel import Field, SQLModel, Column, Numeric

class WarehouseStock(SQLModel, table=True):
    """Модель складских остатков"""
    __tablename__ = "warehouse_stock"

    id: Optional[int] = Field(default=None, primary_key=True)
    material_id: int = Field(foreign_key="materials.id")
    warehouse_code: Optional[str] = Field(max_length=20, nullable=True)
    location: Optional[str] = Field(max_length=50, nullable=True)
    quantity: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(15, 3), nullable=True))
    reserved_qty: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(15, 3), nullable=True))
    unit: str = Field(max_length=20)
    batch_number: Optional[str] = Field(max_length=50, nullable=True)
    receipt_date: Optional[date] = Field(default=None, nullable=True)
    expiry_date: Optional[date] = Field(default=None, nullable=True)
    purchase_price: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(12, 2), nullable=True))
    last_receipt_date: Optional[date] = Field(default=None, nullable=True)
    last_issue_date: Optional[date] = Field(default=None, nullable=True)
    updated_at: Optional[datetime] = Field(default=None, nullable=True)

    @property
    def available(self) -> Decimal:
        """Доступное количество (без резерва)"""
        qty = self.quantity or Decimal('0')
        reserved = self.reserved_qty or Decimal('0')
        return qty - reserved

    @property
    def status(self) -> str:
        """Статус складского остатка"""
        # Simplified status check based on quantity
        qty = self.quantity or Decimal('0')
        if qty < Decimal('100'):
            return "CRITICAL"
        elif qty < Decimal('500'):
            return "LOW"
        return "OK"

