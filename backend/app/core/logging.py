"""
Comprehensive logging configuration for KRAI System v0.6
"""

import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime
import json


def setup_logging():
    """Setup comprehensive logging for the application"""

    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s:%(lineno)d | %(message)s'
    )

    simple_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s'
    )

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)

    # Main log file (DEBUG and above) - rotating
    main_file_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "krai_backend.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    main_file_handler.setLevel(logging.DEBUG)
    main_file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(main_file_handler)

    # Error log file (ERROR and above)
    error_file_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "krai_errors.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_file_handler)

    # API requests log file
    api_file_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "krai_api.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    api_file_handler.setLevel(logging.INFO)
    api_file_handler.setFormatter(detailed_formatter)

    # Create API logger
    api_logger = logging.getLogger("krai.api")
    api_logger.addHandler(api_file_handler)
    api_logger.setLevel(logging.INFO)

    # Database operations logger
    db_file_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "krai_database.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    db_file_handler.setLevel(logging.DEBUG)
    db_file_handler.setFormatter(detailed_formatter)

    db_logger = logging.getLogger("krai.database")
    db_logger.addHandler(db_file_handler)
    db_logger.setLevel(logging.DEBUG)

    # Test results logger
    test_file_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "krai_tests.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    test_file_handler.setLevel(logging.INFO)
    test_file_handler.setFormatter(detailed_formatter)

    test_logger = logging.getLogger("krai.tests")
    test_logger.addHandler(test_file_handler)
    test_logger.setLevel(logging.INFO)

    logging.info("Logging system initialized")
    return root_logger


def log_api_request(method: str, path: str, params: dict = None, body: dict = None):
    """Log API request details"""
    logger = logging.getLogger("krai.api")
    request_data = {
        "method": method,
        "path": path,
        "params": params,
        "body": body,
        "timestamp": datetime.now().isoformat()
    }
    logger.info(f"API Request: {json.dumps(request_data, default=str, ensure_ascii=False)}")


def log_api_response(path: str, status_code: int, response_data: dict = None, error: str = None):
    """Log API response details"""
    logger = logging.getLogger("krai.api")
    response_info = {
        "path": path,
        "status_code": status_code,
        "response": response_data,
        "error": error,
        "timestamp": datetime.now().isoformat()
    }
    if status_code >= 400:
        logger.error(f"API Error Response: {json.dumps(response_info, default=str, ensure_ascii=False)}")
    else:
        logger.info(f"API Response: {json.dumps(response_info, default=str, ensure_ascii=False)}")


def log_database_operation(operation: str, table: str, details: dict = None):
    """Log database operations"""
    logger = logging.getLogger("krai.database")
    db_info = {
        "operation": operation,
        "table": table,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    logger.info(f"DB Operation: {json.dumps(db_info, default=str, ensure_ascii=False)}")


def log_test_result(test_name: str, status: str, details: dict = None, error: str = None):
    """Log test results"""
    logger = logging.getLogger("krai.tests")
    test_info = {
        "test_name": test_name,
        "status": status,
        "details": details,
        "error": error,
        "timestamp": datetime.now().isoformat()
    }
    if status == "FAILED":
        logger.error(f"Test Failed: {json.dumps(test_info, default=str, ensure_ascii=False)}")
    else:
        logger.info(f"Test Result: {json.dumps(test_info, default=str, ensure_ascii=False)}")