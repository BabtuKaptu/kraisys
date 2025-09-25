"""Warehouse endpoints."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.warehouse import (
    WarehouseIssueDraft,
    WarehouseListQuery,
    WarehouseListResult,
    WarehouseReceiptDraft,
    WarehouseStock,
)
from app.services.warehouse_service import WarehouseService

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> WarehouseService:
    return WarehouseService(db)


@router.get("/stock", response_model=WarehouseListResult)
def list_stock(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    search: Optional[str] = None,
    warehouse_code: Optional[str] = Query(None, alias="warehouseCode"),
    status: Optional[str] = None,
    service: WarehouseService = Depends(get_service),
) -> WarehouseListResult:
    query = WarehouseListQuery(
        page=page,
        pageSize=page_size,
        search=search,
        warehouseCode=warehouse_code,
        status=status,
    )
    return service.list_stock(query)


@router.get("/stock/{stock_id}", response_model=WarehouseStock)
def get_stock(stock_id: UUID, service: WarehouseService = Depends(get_service)) -> WarehouseStock:
    try:
        return service.get_stock(stock_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/receipt", status_code=201)
def receipt_materials(
    draft: WarehouseReceiptDraft,
    service: WarehouseService = Depends(get_service),
) -> dict:
    """Process material receipt."""
    try:
        service.receipt(draft)
        return {"message": "Material receipt processed successfully"}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.post("/issue", status_code=201)
def issue_materials(
    draft: WarehouseIssueDraft,
    service: WarehouseService = Depends(get_service),
) -> dict:
    """Process material issue/consumption."""
    try:
        service.issue(draft)
        return {"message": "Material issue processed successfully"}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error") from exc
