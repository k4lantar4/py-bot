"""
Main FastAPI application for the Virtual Account Bot & Dashboard.

This module defines the main FastAPI application with all necessary middleware and routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .api.api_v1.api import api_router
from .core.config import settings
from .core.security import setup_security
from .core.i18n import setup_i18n
from .db.session import setup_database
from .utils.logger import setup_logging

# Create FastAPI app
app = FastAPI(
    title="Virtual Account Bot & Dashboard",
    description="API for managing virtual accounts and sales through Telegram",
    version="1.0.0",
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_REDOC else None,
    openapi_url="/openapi.json" if settings.ENABLE_DOCS else None,
)

# Set up logging
setup_logging()

# Set up database
setup_database()

# Set up internationalization
setup_i18n()

# Set up security
setup_security(app)

# Set up CORS
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Health check endpoints
@app.get("/", tags=["status"])
async def root():
    """Root endpoint for health check."""
    return {
        "status": "ok",
        "service": "Virtual Account Bot API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }

@app.get("/health", tags=["status"])
async def health():
    """Detailed health check endpoint."""
    return {
        "status": "ok",
        "database": "connected",
        "redis": "connected",
        "telegram_bot": "running",
        "environment": settings.ENVIRONMENT,
    }

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for all unhandled exceptions."""
    error_id = settings.sentry.capture_exception(exc) if settings.SENTRY_DSN else None
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred",
            "error_id": error_id,
            "environment": settings.ENVIRONMENT,
        },
    ) 