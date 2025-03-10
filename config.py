import os
from pathlib import Path
from typing import Optional

class Settings:
    # Base paths
    BASE_DIR: Path = Path(__file__).parent
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    API_TOKEN: str = os.getenv("BOT_API_TOKEN")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./bot.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")

settings = Settings() 