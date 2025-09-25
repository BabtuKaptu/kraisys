"""Endpoints serving reference data (perforation types, cutting parts, etc.)."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.reference import ReferenceDraft, ReferenceListQuery, ReferenceListResult, ReferenceItem
from app.services.reference_service import ReferenceService

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> ReferenceService:
    return ReferenceService(db)


@router.get("/", response_model=ReferenceListResult)
def list_references(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    type: Optional[str] = None,
    is_active: Optional[bool] = Query(None, alias="isActive"),
    service: ReferenceService = Depends(get_service),
) -> ReferenceListResult:
    query = ReferenceListQuery(
        page=page,
        pageSize=page_size,
        search=search,
        type=type,
        isActive=is_active,
    )
    return service.list_references(query)


@router.get("/{reference_id}", response_model=ReferenceItem)
def get_reference(reference_id: UUID, service: ReferenceService = Depends(get_service)) -> ReferenceItem:
    try:
        return service.get_reference(reference_id)
    except ValueError as exc:  # pragma: no cover
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/", response_model=ReferenceItem, status_code=201)
def create_reference(payload: ReferenceDraft, service: ReferenceService = Depends(get_service)) -> ReferenceItem:
    return service.create_reference(payload)


@router.put("/{reference_id}", response_model=ReferenceItem)
def update_reference(
    reference_id: UUID,
    payload: ReferenceDraft,
    service: ReferenceService = Depends(get_service),
) -> ReferenceItem:
    try:
        return service.update_reference(reference_id, payload)
    except ValueError as exc:  # pragma: no cover
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{reference_id}", status_code=204)
def delete_reference(reference_id: UUID, service: ReferenceService = Depends(get_service)):
    service.delete_reference(reference_id)
