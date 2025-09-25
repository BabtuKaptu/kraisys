"""FastAPI endpoints for footwear models backed by the normalized PostgreSQL schema."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import logging

from app.db.database import get_db
from app.schemas.model import (
    ModelCreateRequest,
    ModelResponse,
    ModelUpdateRequest,
    ModelVariant as ModelVariantSchema,
    ModelsListQuery,
    ModelsListResult,
)
from app.services.model_service import ModelService

router = APIRouter()

logger = logging.getLogger(__name__)


def get_service(db: Session = Depends(get_db)) -> ModelService:
    logger.info("endpoint get_service: injecting ModelService")
    return ModelService(db)


@router.get("/", response_model=ModelsListResult)
def list_models(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    gender: Optional[str] = None,
    model_type: Optional[str] = Query(None, alias="modelType"),
    category: Optional[str] = None,
    status: Optional[str] = None,
    service: ModelService = Depends(get_service),
) -> ModelsListResult:
    query = ModelsListQuery(
        page=page,
        pageSize=page_size,
        search=search,
        gender=gender,
        modelType=model_type,
        category=category,
        status=status,
    )
    return service.list_models(query)


@router.get("/{model_id}", response_model=ModelResponse)
def get_model(model_id: UUID, service: ModelService = Depends(get_service)) -> ModelResponse:
    try:
        return service.get_model(model_id)
    except ValueError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/", response_model=ModelResponse, status_code=201)
def create_model(payload: ModelCreateRequest, service: ModelService = Depends(get_service)) -> ModelResponse:
    logger.info("START: create_model called with payload: %s", payload)
    try:
        return service.create_model(payload)
    except IntegrityError as exc:
        # Likely unique constraint (e.g., article)
        logger.exception("create_model: integrity error")
        raise HTTPException(
            status_code=409,
            detail={
                "code": "CONFLICT",
                "message": "Unique constraint violated (possibly article exists)",
            },
        ) from exc
    except ValueError as exc:
        logger.exception("create_model: validation error")
        raise HTTPException(
            status_code=422,
            detail={"code": "VALIDATION_ERROR", "message": str(exc)},
        ) from exc
    except Exception as exc:
        logger.exception("create_model: unexpected error")
        raise HTTPException(
            status_code=400,
            detail={"code": "BAD_REQUEST", "message": str(exc)},
        ) from exc


@router.put("/{model_id}", response_model=ModelResponse)
def update_model(
    model_id: UUID,
    payload: ModelUpdateRequest,
    service: ModelService = Depends(get_service),
) -> ModelResponse:
    try:
        return service.update_model(model_id, payload)
    except IntegrityError as exc:
        logger.exception("update_model: integrity error")
        raise HTTPException(
            status_code=409,
            detail={
                "code": "CONFLICT",
                "message": "Unique or FK constraint violated",
            },
        ) from exc
    except ValueError as exc:  # either not found or validation
        msg = str(exc)
        if msg == "Model not found":
            raise HTTPException(status_code=404, detail=msg) from exc
        logger.exception("update_model: validation error")
        raise HTTPException(status_code=422, detail={"code": "VALIDATION_ERROR", "message": msg}) from exc
    except Exception as exc:
        logger.exception("update_model: unexpected error")
        raise HTTPException(status_code=400, detail={"code": "BAD_REQUEST", "message": str(exc)}) from exc


@router.delete("/{model_id}", status_code=204)
def delete_model(model_id: UUID, service: ModelService = Depends(get_service)):
    service.delete_model(model_id)


@router.post("/{model_id}/variants", response_model=ModelResponse)
def upsert_variant(
    model_id: UUID,
    payload: ModelVariantSchema,
    service: ModelService = Depends(get_service),
) -> ModelResponse:
    try:
        return service.upsert_variant(model_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{model_id}/variants/{variant_id}", response_model=ModelResponse)
def delete_variant(
    model_id: UUID,
    variant_id: UUID,
    service: ModelService = Depends(get_service),
) -> ModelResponse:
    try:
        return service.delete_variant(model_id, variant_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
