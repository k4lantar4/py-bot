"""
Core configuration settings for the Virtual Account Bot & Dashboard.

This module uses pydantic-settings for type-safe configuration management.
"""

from typing import List, Optional, Union
from pydantic import AnyHttpUrl, PostgresDsn, RedisDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation."""

    # Application Settings
    PROJECT_NAME: str = "Virtual Account Bot"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    API_V1_STR: str = "/api/v1"
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000

    # Security Settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALLOWED_HOSTS: List[str] = ["*"]

    # Database Settings
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 32
    DATABASE_MAX_OVERFLOW: int = 64
    DATABASE_POOL_TIMEOUT: int = 30

    # Redis Settings
    REDIS_URL: RedisDsn
    REDIS_MAX_CONNECTIONS: int = 10
    CACHE_TTL: int = 3600

    # Telegram Bot Settings
    TELEGRAM_BOT_TOKEN: SecretStr
    TELEGRAM_WEBHOOK_URL: Optional[AnyHttpUrl] = None
    TELEGRAM_ADMIN_IDS: List[int] = []
    ENABLE_TELEGRAM_NOTIFICATIONS: bool = True
    NOTIFICATION_CHANNEL_ID: Optional[int] = None

    # Payment Settings
    ZARINPAL_MERCHANT: SecretStr
    ZARINPAL_SANDBOX: bool = True

    # Frontend Settings
    CORS_ORIGINS: List[AnyHttpUrl] = []
    FRONTEND_URL: AnyHttpUrl

    # Localization Settings
    DEFAULT_LANGUAGE: str = "fa"
    AVAILABLE_LANGUAGES: List[str] = ["fa", "en"]
    JALALI_DATE: bool = True

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_SECOND: int = 10

    # Development Tools
    ENABLE_DOCS: bool = True
    ENABLE_REDOC: bool = True

    # Monitoring & Logging
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: Optional[AnyHttpUrl] = None

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Validate and process CORS origins."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @field_validator("TELEGRAM_ADMIN_IDS", mode="before")
    def assemble_admin_ids(cls, v: Union[str, List[int]]) -> List[int]:
        """Validate and process admin IDs."""
        if isinstance(v, str):
            return [int(i.strip()) for i in v.split(",")]
        return v

    class Config:
        """Pydantic configuration."""
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create global settings object
settings = Settings() 