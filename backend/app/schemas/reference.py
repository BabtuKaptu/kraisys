"""Pydantic schemas for reference data."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .common import ListQuery, PaginatedResult


class ReferenceItem(BaseModel):
    id: UUID
    type: str
    code: Optional[str] = None
    name: str
    description: Optional[str] = None
    isActive: bool = True
    attributes: Dict[str, Any] = Field(default_factory=dict)


class ReferenceDraft(BaseModel):
    type: str
    code: Optional[str] = None
    name: str
    description: Optional[str] = None
    isActive: bool = True
    attributes: Dict[str, Any] = Field(default_factory=dict)


class ReferenceListQuery(ListQuery):
    type: Optional[str] = None
    isActive: Optional[bool] = None


class ReferenceListResult(PaginatedResult[ReferenceItem]):
    pass
