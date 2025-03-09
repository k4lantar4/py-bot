"""
Configuration module for the 3X-UI Management System.

This module loads environment variables and provides configuration settings
for the entire application. It uses Pydantic's settings management to validate
and parse environment variables.
"""

import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings class that loads from environment variables.
    """
    # Application metadata
    PROJECT_NAME: str = "3X-UI Management System"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    
    # Security
    SECRET_KEY: str
    # 60 minutes * 24 hours * 7 days = 7 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # CORS configuration
    BACKEND_CORS_ORIGINS: List[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Parse CORS origins from string to list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    DATABASE_URL: PostgresDsn
    
    # Redis
    REDIS_URL: str
    
    # Email
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: Optional[int] = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: Optional[str] = "noreply@example.com"
    
    # Superuser settings (first user created)
    FIRST_SUPERUSER_EMAIL: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin"
    
    # Features toggle
    ENABLE_LOCATION_MANAGEMENT: bool = True
    ENABLE_SERVER_MANAGEMENT: bool = True
    ENABLE_SERVICE_MANAGEMENT: bool = True
    ENABLE_USER_MANAGEMENT: bool = True
    ENABLE_DISCOUNT_MANAGEMENT: bool = True
    ENABLE_FINANCIAL_REPORTS: bool = True
    ENABLE_BULK_MESSAGING: bool = True
    ENABLE_SERVER_MONITORING: bool = True
    ENABLE_AI_FEATURES: bool = True
    
    # 3X-UI API configuration
    THREEXUI_SESSION_REFRESH_MINUTES: int = 60  # Refresh 3X-UI sessions every 60 minutes
    THREEXUI_PING_INTERVAL_MINUTES: int = 5  # Check 3X-UI servers every 5 minutes
    
    # Telegram Bot
    TELEGRAM_BOT_ENABLED: bool = True
    
    # Model config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Create settings instance
settings = Settings()

# Feature toggles as a dictionary for easier access
FEATURE_FLAGS = {
    "location_management": settings.ENABLE_LOCATION_MANAGEMENT,
    "server_management": settings.ENABLE_SERVER_MANAGEMENT,
    "service_management": settings.ENABLE_SERVICE_MANAGEMENT,
    "user_management": settings.ENABLE_USER_MANAGEMENT,
    "discount_management": settings.ENABLE_DISCOUNT_MANAGEMENT,
    "financial_reports": settings.ENABLE_FINANCIAL_REPORTS,
    "bulk_messaging": settings.ENABLE_BULK_MESSAGING,
    "server_monitoring": settings.ENABLE_SERVER_MONITORING,
    "ai_features": settings.ENABLE_AI_FEATURES,
    "telegram_bot": settings.TELEGRAM_BOT_ENABLED,
} 