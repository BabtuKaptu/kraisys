"""Shared schema utilities and enumerations."""

from __future__ import annotations

from typing import Generic, List, Optional, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel


class Attachment(BaseModel):
    id: UUID
    fileName: str
    fileType: str
    url: str
    uploadedAt: str


class KPIBlock(BaseModel):
    title: str
    value: Union[str, float, int]
    trend: Optional[str] = None
    helperText: Optional[str] = None


T = TypeVar("T")


class PaginatedResult(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    pageSize: int


class ListQuery(BaseModel):
    page: int = 1
    pageSize: int = 10
    search: Optional[str] = None


class EnumValues:
    GENDERS = {"MALE", "FEMALE", "UNISEX", "KIDS"}
    MODEL_TYPES = {"SPORT", "CASUAL", "FORMAL", "WORK", "OUTDOOR", "SPECIAL"}
    MODEL_CATEGORIES = {
        "SNEAKERS",
        "SHOES",
        "BOOTS",
        "SANDALS",
        "SLIPPERS",
        "LOAFERS",
        "OXFORDS",
        "DERBY",
        "OTHER",
    }
    SEASONS = {"SPRING_SUMMER", "FALL_WINTER", "ALL_SEASON", "DEMISEASON", "CUSTOM"}
    LACING_TYPES = {
        "GLUED",
        "STITCHED",
        "HANDMADE",
        "COMBINED",
        "CEMENTED",
        "LASTING",
    }
    MATERIAL_GROUPS = {
        "LEATHER",
        "SOLE",
        "HARDWARE",
        "LINING",
        "CHEMICAL",
        "PACKAGING",
        "TEXTILE",
        "ADHESIVE",
        "OTHER",
    }
    UNIT_OF_MEASURE = {
        "шт",
        "пар",
        "компл",
        "уп",
        "дм²",
        "м²",
        "м",
        "кг",
        "г",
        "л",
        "мл",
    }
