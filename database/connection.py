"""Database connection management for PyQt6 application"""
import psycopg2
from psycopg2 import pool
from sqlmodel import create_engine, Session, select
from config import DATABASE_CONFIG, DATABASE_URL

class DatabaseConnection:
    """Управление подключениями к PostgreSQL"""

    _instance = None
    _engine = None
    _pg_pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            try:
                # SQLModel engine для ORM операций
                self._engine = create_engine(DATABASE_URL, echo=False, pool_size=5)

                # Проверяем подключение
                with self.get_session() as session:
                    session.exec(select(1))
                    print(f"✓ Database connected: {DATABASE_CONFIG['database']}@{DATABASE_CONFIG['host']}")

                # Создаем пул подключений для прямых SQL запросов
                self._pg_pool = psycopg2.pool.SimpleConnectionPool(
                    1, 5,
                    host=DATABASE_CONFIG['host'],
                    port=DATABASE_CONFIG['port'],
                    database=DATABASE_CONFIG['database'],
                    user=DATABASE_CONFIG['user'],
                    password=DATABASE_CONFIG['password']
                )

                self.initialized = True

            except Exception as e:
                print(f"⚠️ Database connection failed: {e}")
                self.initialized = False
                raise

    @property
    def engine(self):
        return self._engine

    def get_session(self) -> Session:
        """Получить SQLModel сессию"""
        return Session(self._engine)

    def get_connection(self):
        """Получить прямое psycopg2 соединение из пула"""
        if self._pg_pool:
            return self._pg_pool.getconn()
        return None

    def put_connection(self, conn):
        """Вернуть соединение в пул"""
        if self._pg_pool and conn:
            self._pg_pool.putconn(conn)

    def test_connection(self) -> bool:
        """Тестировать подключение"""
        try:
            with self.get_session() as session:
                result = session.exec(select(1))
                return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False