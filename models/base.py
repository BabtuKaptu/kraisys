# krai_system/models/base.py
from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime
import uuid

class Base(SQLModel):
    """Базовый класс для всех моделей"""
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)