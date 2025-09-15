# krai_system/services/database.py
import os
from sqlmodel import create_engine, Session, select
from typing import Optional, List, Type, TypeVar
from ..models.base import Base

# Типы для генериков
T = TypeVar('T', bound=Base)

# Создание движка БД
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://four@localhost:5432/krai_system"
)

engine = create_engine(DATABASE_URL, echo=True)

class DatabaseService:
    """Сервис для работы с базой данных"""
    
    @staticmethod
    def get_session() -> Session:
        """Получить сессию БД"""
        return Session(engine)
    
    @staticmethod
    def get_all(model: Type[T]) -> List[T]:
        """Получить все записи модели"""
        with Session(engine) as session:
            statement = select(model)
            results = session.exec(statement)
            return results.all()
    
    @staticmethod
    def get_by_id(model: Type[T], id: str) -> Optional[T]:
        """Получить запись по ID"""
        with Session(engine) as session:
            statement = select(model).where(model.id == id)
            result = session.exec(statement)
            return result.first()
    
    @staticmethod
    def create(instance: T) -> T:
        """Создать новую запись"""
        with Session(engine) as session:
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance
    
    @staticmethod
    def update(instance: T) -> T:
        """Обновить запись"""
        with Session(engine) as session:
            # Используем merge для обработки отсоединенных объектов
            merged_instance = session.merge(instance)
            session.commit()
            session.refresh(merged_instance)
            return merged_instance
    
    @staticmethod
    def delete(model: Type[T], id: str) -> bool:
        """Удалить запись"""
        with Session(engine) as session:
            statement = select(model).where(model.id == id)
            result = session.exec(statement)
            instance = result.first()
            if instance:
                session.delete(instance)
                session.commit()
                return True
            return False
    
    @staticmethod
    def execute_query(query: str) -> list:
        """Выполнить произвольный SQL запрос"""
        with Session(engine) as session:
            result = session.execute(query)
            return result.fetchall()