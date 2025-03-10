"""
Main FastAPI application for the 3X-UI Management System.

This module defines the main FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.api_v1.api import api_router
from .core.config import settings
from .utils.logger import logger

# Create FastAPI app
app = FastAPI(
    title="3X-UI Management System",
    description="API for managing 3X-UI instances",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
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

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["status"])
async def root():
    """
    Root endpoint for health check.
    """
    return {"status": "ok", "message": "3X-UI Management System API is running"}


@app.get("/health", tags=["status"])
async def health():
    """
    Health check endpoint.
    """
    return {"status": "ok"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler.
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    ) 