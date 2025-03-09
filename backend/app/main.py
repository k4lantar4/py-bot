"""
Main FastAPI application for the 3X-UI Management System.

This module initializes the FastAPI application, sets up middleware,
exception handlers, and includes the API routers.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from sqlalchemy.orm import Session
import emoji

from app.api.api_v1.api import api_router
from app.core.config import settings, FEATURE_FLAGS
from app.db.session import engine, Base, get_db
from app.core import security
from app.core.redis import redis_client


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for managing 3X-UI panels",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=None,  # Disable default docs route to use custom one
    redoc_url=None,  # Disable default redoc
)

# Set up CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Custom exception handlers
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Custom HTTP exception handler with friendly messages and emojis.
    """
    error_emoji = emoji.emojize(":warning:")
    if exc.status_code >= 500:
        error_emoji = emoji.emojize(":red_exclamation_mark:")
    elif exc.status_code >= 400:
        error_emoji = emoji.emojize(":cross_mark:")
    
    # Return a custom, more user-friendly error message
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": f"{error_emoji} {exc.detail}",
            "code": exc.status_code,
            "success": False,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Custom validation exception handler with friendly messages and emojis.
    """
    error_emoji = emoji.emojize(":memo:")
    errors = exc.errors()
    
    # Extract field names and error messages for a more user-friendly response
    validation_errors = []
    for error in errors:
        field = ".".join(str(loc) for loc in error["loc"][1:]) if len(error["loc"]) > 1 else "Input"
        message = error["msg"]
        validation_errors.append(f"{field}: {message}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": f"{error_emoji} Validation error",
            "details": validation_errors,
            "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "success": False,
        },
    )


# Health check endpoint
@app.get("/ping", tags=["Health"])
def ping() -> Dict[str, str]:
    """
    Simple health check endpoint.
    """
    return {"status": "ok", "message": emoji.emojize("Server is running :check_mark:")}


# Feature flags endpoint
@app.get("/features", tags=["Config"])
def features() -> Dict[str, Dict[str, bool]]:
    """
    Get enabled features.
    """
    return {"features": FEATURE_FLAGS}


# Custom docs endpoint
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html() -> HTMLResponse:
    """
    Custom Swagger UI with the project name and version.
    """
    return get_swagger_ui_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=f"{settings.PROJECT_NAME} API - v{settings.VERSION}",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    )


# Redirect root to docs
@app.get("/", include_in_schema=False)
async def redirect_to_docs() -> RedirectResponse:
    """
    Redirect root path to documentation.
    """
    return RedirectResponse(url="/docs")


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Event handlers
@app.on_event("startup")
async def startup_event() -> None:
    """
    Actions to perform on application startup.
    """
    logger.info("Starting up the application...")
    
    # Check Redis connection
    try:
        redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
    
    # Log enabled features
    enabled_features = [name for name, enabled in FEATURE_FLAGS.items() if enabled]
    logger.info(f"Enabled features: {', '.join(enabled_features)}")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    Actions to perform on application shutdown.
    """
    logger.info("Shutting down the application...") 