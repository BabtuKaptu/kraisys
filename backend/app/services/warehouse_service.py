"""Service layer for warehouse operations."""

from __future__ import annotations

from typing import List
from uuid import UUID

from datetime import datetime, date
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Material, WarehouseStock
from app.schemas.material import MaterialReference
from app.schemas.warehouse import (
    WarehouseIssueDraft,
    WarehouseListQuery,
    WarehouseListResult,
    WarehouseReceiptDraft,
    WarehouseStock as WarehouseStockSchema,
    WarehouseStockListItem,
)


class WarehouseService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_stock(self, query: WarehouseListQuery) -> WarehouseListResult:
        stmt = select(WarehouseStock).options(selectinload(WarehouseStock.material))
        if query.search:
            pattern = f"%{query.search.lower()}%"
            stmt = stmt.join(WarehouseStock.material).where(
                func.lower(Material.name).like(pattern) | func.lower(Material.code).like(pattern)
            )
        if query.warehouseCode:
            stmt = stmt.where(WarehouseStock.warehouse_code == query.warehouseCode)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.scalar(count_stmt) or 0

        stmt = (
            stmt.order_by(WarehouseStock.updated_at.desc())
            .offset((query.page - 1) * query.pageSize)
            .limit(query.pageSize)
        )
        stocks = self.db.scalars(stmt).all()

        items: List[WarehouseStockListItem] = [self._to_list_item(stock) for stock in stocks]
        if query.status:
            target = query.status.upper()
            items = [item for item in items if item.status == target]
            total = len(items)

        return WarehouseListResult(items=items, total=total, page=query.page, pageSize=query.pageSize)

    def get_stock(self, stock_id: UUID) -> WarehouseStockSchema:
        stock = self.db.get(WarehouseStock, stock_id)
        if not stock:
            raise ValueError("Stock item not found")
        return self._to_schema(stock)

    # ------------------------------------------------------------------
    def _to_schema(self, stock: WarehouseStock) -> WarehouseStockSchema:
        material_ref = MaterialReference(
            id=stock.material.material_id,
            code=stock.material.code,
            name=stock.material.name,
            group=stock.material.group,
            unit=stock.material.unit_primary,
            color=stock.material.color,
        )
        quantity = float(stock.quantity or 0)
        reserved = float(stock.reserved_quantity or 0)
        available = quantity - reserved
        total_value = (float(stock.purchase_price) if stock.purchase_price else 0) * available
        status = "OK"
        if available < 100:
            status = "CRITICAL"
        elif available < 500:
            status = "LOW"

        return WarehouseStockSchema(
            id=stock.stock_id,
            material=material_ref,
            batchNumber=stock.batch_number,
            warehouseCode=stock.warehouse_code,
            location=stock.location,
            quantity=quantity,
            reservedQuantity=reserved,
            unit=stock.unit,
            purchasePrice=float(stock.purchase_price) if stock.purchase_price is not None else None,
            receiptDate=stock.receipt_date,
            expiryDate=stock.expiry_date,
            lastReceiptDate=stock.last_receipt_date,
            lastIssueDate=stock.last_issue_date,
            notes=stock.notes,
            availableQuantity=available,
            status=status,
            totalValue=total_value,
            updatedAt=stock.updated_at,
        )

    def _process_receipt_date(self, receipt_date_input):
        """Convert receipt date to date object."""
        if receipt_date_input is None:
            return datetime.utcnow().date()
        elif isinstance(receipt_date_input, str):
            return datetime.fromisoformat(receipt_date_input.replace('Z', '+00:00')).date()
        elif isinstance(receipt_date_input, datetime):
            return receipt_date_input.date()
        else:
            # Fallback для любых других типов
            return datetime.utcnow().date()

    def _generate_batch_number(self, material_id: str, receipt_date) -> str:
        """Generate human-readable batch number for material receipt."""
        from datetime import datetime
        
        # Get material code from database
        from app.models import Material
        material = self.db.query(Material).filter(Material.material_id == material_id).first()
        material_code = material.code if material else "MAT"
        
        # Format date
        if isinstance(receipt_date, str):
            date_obj = datetime.fromisoformat(receipt_date.replace('Z', '+00:00'))
        elif hasattr(receipt_date, 'date'):
            date_obj = receipt_date
        else:
            date_obj = datetime.now()
            
        today_str = date_obj.strftime('%Y%m%d')
        
        # Count DISTINCT batch numbers for this material today (not records!)
        from sqlalchemy import func, and_
        from app.models import WarehouseStock
        
        existing_batches = self.db.query(func.count(func.distinct(WarehouseStock.batch_number))).filter(
            and_(
                WarehouseStock.material_id == material_id,
                WarehouseStock.batch_number.like(f"{material_code}-{today_str}-%"),
                WarehouseStock.batch_number.isnot(None)
            )
        ).scalar() or 0
        
        seq_number = str(existing_batches + 1).zfill(3)  # 001, 002, 003...
        
        # Format: МАТЕРИАЛ-YYYYMMDD-NNN
        return f"{material_code}-{today_str}-{seq_number}"

    def receipt(self, draft: WarehouseReceiptDraft) -> None:
        """Process material receipt."""
        import logging
        from decimal import Decimal
        logger = logging.getLogger(__name__)
        logger.info(f"Starting receipt processing: {draft}")
        try:
            for line in draft.lines:
                logger.info(f"Processing line: {line}")
                
                # Генерируем уникальную партию для каждого прихода
                receipt_date = self._process_receipt_date(line.receiptDate)
                batch_number = line.batchNumber or self._generate_batch_number(line.materialId, receipt_date)
                logger.info(f"Generated batch number: {batch_number}")
                
                # Ищем существующую запись по партии (всегда будет новая для нового прихода)
                query = self.db.query(WarehouseStock).filter(
                    WarehouseStock.material_id == line.materialId,
                    WarehouseStock.warehouse_code == line.warehouseCode,
                    WarehouseStock.batch_number == batch_number
                )
                
                stock = query.first()
                
                if stock:
                    # Обновить существующий остаток
                    current_qty = Decimal(str(stock.quantity or 0))
                    add_qty = Decimal(str(line.quantity))
                    stock.quantity = current_qty + add_qty
                    stock.last_receipt_date = receipt_date
                    if line.price is not None:
                        stock.purchase_price = line.price
                    if line.location:
                        stock.location = line.location
                    # updated_at обновляется автоматически через onupdate=func.now()
                else:
                    # Создать новую запись
                    stock = WarehouseStock(
                        material_id=line.materialId,
                        warehouse_code=line.warehouseCode,
                        location=line.location,
                        quantity=Decimal(str(line.quantity)),
                        reserved_quantity=0,
                        unit=line.unit,
                        purchase_price=line.price,
                        batch_number=batch_number,  # Используем сгенерированную партию
                        receipt_date=receipt_date,
                        last_receipt_date=receipt_date,
                        notes=line.comments,
                        # updated_at устанавливается автоматически
                    )
                    self.db.add(stock)
            
            logger.info("Committing transaction...")
            self.db.commit()
            logger.info("Transaction committed successfully")
        except Exception as e:
            logger.error(f"Exception in receipt: {e}", exc_info=True)
            self.db.rollback()
            raise e

    def issue(self, draft: WarehouseIssueDraft) -> None:
        """Process material issue/consumption."""
        for line in draft.lines:
            stock = self.db.get(WarehouseStock, line.stockId)
            if not stock:
                raise ValueError(f"Stock item {line.stockId} not found")
            
            available = (stock.quantity or 0) - (stock.reserved_quantity or 0)
            if available < line.quantity:
                raise ValueError(f"Insufficient stock: available {available}, requested {line.quantity}")
            
            # Списать материал
            stock.quantity = (stock.quantity or 0) - line.quantity
            stock.last_issue_date = datetime.utcnow().date()
            # updated_at обновляется автоматически через onupdate=func.now()
            
            # Добавить комментарий к notes если есть
            if line.comments:
                existing_notes = stock.notes or ""
                timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
                new_note = f"[{timestamp}] {line.reason}: {line.comments}"
                stock.notes = f"{existing_notes}\n{new_note}" if existing_notes else new_note
        
        self.db.commit()

    def _to_list_item(self, stock: WarehouseStock) -> WarehouseStockListItem:
        """Convert WarehouseStock model to WarehouseStockListItem schema."""
        schema_data = self._to_schema(stock)
        return WarehouseStockListItem(**schema_data.model_dump())
