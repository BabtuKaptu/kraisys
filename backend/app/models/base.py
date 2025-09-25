"""SQLAlchemy base definitions for the KRAI v0.6 backend."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

Base = declarative_base()


class TimestampMixin:
    """Mixin that adds created/updated timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


def generate_uuid() -> uuid.UUID:
    """Helper for default UUID values (sqlalchemy can't call uuid4 without function)."""

    return uuid.uuid4()


class UUIDMixin:
    """Mixin that provides a UUID primary key."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )

