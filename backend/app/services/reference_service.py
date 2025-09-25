"""Service helpers for reference data."""

from __future__ import annotations

from typing import List
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import ReferenceItem as ReferenceItemModel
from app.schemas.reference import (
    ReferenceDraft,
    ReferenceItem,
    ReferenceListQuery,
    ReferenceListResult,
)


class ReferenceService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_references(self, query: ReferenceListQuery) -> ReferenceListResult:
        stmt = select(ReferenceItemModel)
        if query.type:
            stmt = stmt.where(ReferenceItemModel.type == query.type)
        if query.isActive is not None:
            stmt = stmt.where(ReferenceItemModel.is_active == query.isActive)
        if query.search:
            pattern = f"%{query.search.lower()}%"
            stmt = stmt.where(func.lower(ReferenceItemModel.name).like(pattern))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.scalar(count_stmt) or 0

        stmt = (
            stmt.order_by(ReferenceItemModel.name.asc())
            .offset((query.page - 1) * query.pageSize)
            .limit(query.pageSize)
        )
        items = self.db.scalars(stmt).all()
        return ReferenceListResult(
            items=[self._to_schema(item) for item in items],
            total=total,
            page=query.page,
            pageSize=query.pageSize,
        )

    def get_reference(self, reference_id: UUID) -> ReferenceItem:
        item = self.db.get(ReferenceItemModel, reference_id)
        if not item:
            raise ValueError("Reference item not found")
        return self._to_schema(item)

    def create_reference(self, payload: ReferenceDraft) -> ReferenceItem:
        entity = ReferenceItemModel()
        self._apply_draft(entity, payload)
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return self._to_schema(entity)

    def update_reference(self, reference_id: UUID, payload: ReferenceDraft) -> ReferenceItem:
        entity = self.db.get(ReferenceItemModel, reference_id)
        if not entity:
            raise ValueError("Reference item not found")
        self._apply_draft(entity, payload)
        self.db.commit()
        self.db.refresh(entity)
        return self._to_schema(entity)

    def delete_reference(self, reference_id: UUID) -> None:
        entity = self.db.get(ReferenceItemModel, reference_id)
        if not entity:
            return
        self.db.delete(entity)
        self.db.commit()

    @staticmethod
    def _apply_draft(entity: ReferenceItemModel, payload: ReferenceDraft) -> None:
        entity.type = payload.type
        entity.code = payload.code
        entity.name = payload.name
        entity.description = payload.description
        entity.is_active = payload.isActive
        entity.attributes = payload.attributes

    @staticmethod
    def _to_schema(entity: ReferenceItemModel) -> ReferenceItem:
        return ReferenceItem(
            id=entity.reference_id,
            type=entity.type,
            code=entity.code,
            name=entity.name,
            description=entity.description,
            isActive=entity.is_active,
            attributes=entity.attributes or {},
        )

