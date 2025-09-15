# Configuration for Desktop Application

import os
from pathlib import Path

# Database connection
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432),
    'database': os.getenv('DB_NAME', 'krai_system'),
    'user': os.getenv('DB_USER', 'four'),
    'password': os.getenv('DB_PASSWORD', '')
}

# Database URL for SQLModel
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
)

# Application settings
APP_NAME = "KRAI Production System"
APP_VERSION = "1.0.0"
COMPANY_NAME = "KRAI"

# Production settings
DAILY_PRODUCTION_CAPACITY = 150  # пар в день
DEFAULT_LEAD_TIME_DAYS = 7  # срок поставки по умолчанию

# UI Settings
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
TABLE_ROW_HEIGHT = 30
ENABLE_DARK_MODE = False

# Paths
BASE_DIR = Path(__file__).parent
REPORTS_DIR = BASE_DIR / "reports"
EXPORTS_DIR = BASE_DIR / "exports"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if not exist
for directory in [REPORTS_DIR, EXPORTS_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = LOGS_DIR / 'krai_app.log'