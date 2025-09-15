# krai_system/models/cutting_parts.py
from sqlmodel import Field, Column, JSON
from typing import Optional, Dict, Any
from .base import Base

class CuttingPart(Base, table=True):
    """Справочник деталей кроя обуви"""
    __tablename__ = "cutting_parts"
    
    # Уникальный код детали
    code: str = Field(unique=True, index=True)
    
    # Название детали
    name: str = Field(index=True)
    
    # Категория детали
    category: Optional[str] = Field(default=None)
    # Категории: SOYUZKA, BEREC, ZADNIK, YAZYK, KANT, VSTAVKA, NADBLOCHNIK, REMESHOK, GOLENISCHE, OTHER
    
    # Является ли деталью кроя (true) или покупным материалом (false)
    is_cutting: bool = Field(default=True)
    
    # Количество по умолчанию (null = зависит от модели)
    default_qty: Optional[int] = Field(default=None)
    
    # Единица измерения
    unit: str = Field(default="шт")
    
    # Примечания и особенности
    notes: Optional[str] = Field(default=None)
    
    # Дополнительные свойства в JSONB
    properties: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    
    # Статус
    is_active: bool = Field(default=True)
    
    @classmethod
    def get_by_category(cls, session, category: str):
        """Получить все детали по категории"""
        return session.query(cls).filter(
            cls.category == category,
            cls.is_active == True
        ).all()
    
    @classmethod
    def get_cutting_only(cls, session):
        """Получить только детали кроя (не покупные)"""
        return session.query(cls).filter(
            cls.is_cutting == True,
            cls.is_active == True
        ).all()