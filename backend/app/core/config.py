"""
Core configuration settings for the Virtual Account Bot & Dashboard.

This module uses pydantic-settings for type-safe configuration management.
"""

from typing import List, Optional, Union, Any
from pydantic import AnyHttpUrl, PostgresDsn, RedisDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation."""

    # Application Settings
    PROJECT_NAME: str = "Virtual Account Bot"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "default-secret-key-for-development"
    API_V1_STR: str = "/api/v1"
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000

    # Security Settings
    JWT_SECRET_KEY: str = "default-jwt-secret-key-for-development"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    # Define ALLOWED_HOSTS as a string to avoid JSON parsing
    ALLOWED_HOSTS: str = "*"

    # Database Settings
    DATABASE_URL: Optional[PostgresDsn] = None
    DATABASE_POOL_SIZE: int = 32
    DATABASE_MAX_OVERFLOW: int = 64
    DATABASE_POOL_TIMEOUT: int = 30

    # Redis Settings
    REDIS_URL: Optional[RedisDsn] = None
    REDIS_MAX_CONNECTIONS: int = 10
    CACHE_TTL: int = 3600

    # Telegram Bot Settings
    TELEGRAM_BOT_TOKEN: Optional[str] = "default-bot-token"
    TELEGRAM_WEBHOOK_URL: Optional[str] = None
    TELEGRAM_ADMIN_IDS: List[int] = []
    ENABLE_TELEGRAM_NOTIFICATIONS: bool = True
    NOTIFICATION_CHANNEL_ID: Optional[int] = None

    # Payment Settings
    ZARINPAL_MERCHANT: Optional[str] = "default-merchant"
    ZARINPAL_SANDBOX: bool = True

    # Frontend Settings
    CORS_ORIGINS: List[str] = []
    FRONTEND_URL: Optional[str] = "http://localhost:3000"

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
    SENTRY_DSN: Optional[str] = None

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Validate and process CORS origins."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Remove the ALLOWED_HOSTS validator since we're using a string directly
    # and will handle it in the application code

    @field_validator("TELEGRAM_ADMIN_IDS", mode="before")
    def assemble_admin_ids(cls, v: Union[str, List[int]]) -> List[int]:
        """Validate and process admin IDs."""
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                # Try to handle JSON-like string
                try:
                    import json
                    return json.loads(v)
                except:
                    pass
            # Handle comma-separated string
            try:
                return [int(i.strip()) for i in v.split(",")]
            except ValueError:
                return []
        return v

    class Config:
        """Pydantic configuration."""
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create global settings object
settings = Settings()

# Process ALLOWED_HOSTS after settings are loaded
# This will be used in the application code
def get_allowed_hosts() -> List[str]:
    """Convert ALLOWED_HOSTS string to list for application use."""
    if settings.ALLOWED_HOSTS == "*":
        return ["*"]
    return [host.strip() for host in settings.ALLOWED_HOSTS.split(",")] 