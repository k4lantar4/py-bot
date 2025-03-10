import logging
import json_logging
from pythonjsonlogger import jsonlogger
from config import settings

def setup_logging():
    """Configure structured JSON logging"""
    json_logging.init_fastapi()
    
    logger = logging.getLogger("telegram_bot")
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    logger.setLevel(settings.LOG_LEVEL)
    
    return logger

# Sentry integration
if settings.SENTRY_DSN:
    import sentry_sdk
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    ) 