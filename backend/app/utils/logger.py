"""
Logger utility for the 3X-UI Management System.

This module provides a configured logger for the application.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict

from pythonjsonlogger import jsonlogger

from app.core.config import settings

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging format
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
json_format = "%(asctime)s %(name)s %(levelname)s %(message)s"

# Create formatters
standard_formatter = logging.Formatter(log_format)
json_formatter = jsonlogger.JsonFormatter(json_format)

# Create handlers
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(standard_formatter)

file_handler = logging.FileHandler(logs_dir / "app.log")
file_handler.setFormatter(json_formatter)

error_handler = logging.FileHandler(logs_dir / "error.log")
error_handler.setFormatter(json_formatter)
error_handler.setLevel(logging.ERROR)

# Create logger
logger = logging.getLogger("app")
logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.addHandler(error_handler)


def setup_logging() -> None:
    """Set up logging configuration."""
    # Configure uvicorn access logger
    uvicorn_logger = logging.getLogger("uvicorn.access")
    uvicorn_logger.handlers = []
    uvicorn_logger.addHandler(console_handler)
    uvicorn_logger.addHandler(file_handler)

    # Configure SQLAlchemy logger
    sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
    sqlalchemy_logger.setLevel(logging.INFO if settings.DEBUG else logging.WARNING)
    sqlalchemy_logger.addHandler(console_handler)
    sqlalchemy_logger.addHandler(file_handler)

    # Set up Sentry if configured
    if settings.SENTRY_DSN:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

        sentry_sdk.init(
            dsn=str(settings.SENTRY_DSN),
            environment=settings.ENVIRONMENT,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=1.0,
        )


def log_error(error: Exception, context: Dict[str, Any] = None) -> None:
    """Log an error with context."""
    logger.error(
        str(error),
        extra={
            "context": context or {},
            "error_type": type(error).__name__,
            "error_details": {
                "args": getattr(error, "args", None),
                "message": str(error),
            },
        },
        exc_info=True,
    ) 