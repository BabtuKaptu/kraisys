"""Database connection management for PyQt6 application"""
import psycopg2
from psycopg2 import pool
from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from sqlmodel import create_engine, Session
from config import DATABASE_CONFIG, DATABASE_URL

class DatabaseConnection:
    """Управление подключениями к PostgreSQL"""

    _instance = None
    _engine = None
    _qt_db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            # SQLModel engine для ORM операций
            self._engine = create_engine(DATABASE_URL, echo=False, pool_size=5)

            # Qt database для таблиц
            self._qt_db = QSqlDatabase.addDatabase("QPSQL")
            self._qt_db.setHostName(DATABASE_CONFIG['host'])
            self._qt_db.setPort(DATABASE_CONFIG['port'])
            self._qt_db.setDatabaseName(DATABASE_CONFIG['database'])
            self._qt_db.setUserName(DATABASE_CONFIG['user'])
            self._qt_db.setPassword(DATABASE_CONFIG['password'])

            if not self._qt_db.open():
                print(f"Warning: Cannot open Qt database: {self._qt_db.lastError().text()}")
                # Continue without Qt database

            self.initialized = True
            print(f"Database connected: {DATABASE_CONFIG['database']}@{DATABASE_CONFIG['host']}")

    @property
    def engine(self):
        return self._engine

    @property
    def qt_db(self):
        return self._qt_db

    def get_session(self) -> Session:
        """Получить SQLModel сессию"""
        return Session(self._engine)

    def test_connection(self) -> bool:
        """Тестировать подключение"""
        try:
            query = QSqlQuery()
            query.exec("SELECT 1")
            return query.next()
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False