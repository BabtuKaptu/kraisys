"""
Configuration settings for KRAI System v0.6
"""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Project Info
    PROJECT_NAME: str = "KRAI Production System"
    VERSION: str = "0.7.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://four@localhost:5432/krai_mrp_v06",
        description="PostgreSQL database URL"
    )

    # Security
    SECRET_KEY: str = Field(
        default="your-super-secret-key-change-in-production",
        description="Secret key for JWT token generation"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:3001",  # Vite dev server (actual port)
        "http://localhost:5173",  # Vite dev server (default)
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173"
    ]

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Telegram Bot for 2FA
    TELEGRAM_BOT_TOKEN: Optional[str] = None

    # Production Settings
    DAILY_PRODUCTION_CAPACITY: int = 150
    DEFAULT_LEAD_TIME_DAYS: int = 7

    # Environment
    ENVIRONMENT: str = Field(default="development")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
