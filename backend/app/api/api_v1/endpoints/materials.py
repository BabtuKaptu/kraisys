"""FastAPI endpoints for materials."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.material import (
    MaterialCreateRequest,
    MaterialResponse,
    MaterialUpdateRequest,
    MaterialsListResult,
    MaterialsListQuery,
)
from app.services.material_service import MaterialService

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> MaterialService:
    return MaterialService(db)


@router.get("/", response_model=MaterialsListResult)
def list_materials(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    group: Optional[str] = None,
    subgroup: Optional[str] = None,
    is_active: Optional[bool] = Query(None, alias="isActive"),
    is_critical: Optional[bool] = Query(None, alias="isCritical"),
    price_min: Optional[float] = Query(None, alias="priceMin"),
    price_max: Optional[float] = Query(None, alias="priceMax"),
    service: MaterialService = Depends(get_service),
) -> MaterialsListResult:
    query = MaterialsListQuery(
        page=page,
        pageSize=page_size,
        search=search,
        group=group,
        subgroup=subgroup,
        isActive=is_active,
        isCritical=is_critical,
        priceMin=price_min,
        priceMax=price_max,
    )
    return service.list_materials(query)


@router.get("/{material_id}", response_model=MaterialResponse)
def get_material(material_id: UUID, service: MaterialService = Depends(get_service)) -> MaterialResponse:
    try:
        return service.get_material(material_id)
    except ValueError as exc:  # pragma: no cover
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/", response_model=MaterialResponse, status_code=201)
def create_material(payload: MaterialCreateRequest, service: MaterialService = Depends(get_service)) -> MaterialResponse:
    return service.create_material(payload)


@router.put("/{material_id}", response_model=MaterialResponse)
def update_material(
    material_id: UUID,
    payload: MaterialUpdateRequest,
    service: MaterialService = Depends(get_service),
) -> MaterialResponse:
    try:
        return service.update_material(material_id, payload)
    except ValueError as exc:  # pragma: no cover
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{material_id}", status_code=204)
def delete_material(material_id: UUID, service: MaterialService = Depends(get_service)):
    service.delete_material(material_id)
