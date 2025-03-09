"""
API dependencies for the 3X-UI Management System.

This module defines reusable dependencies for FastAPI endpoints.
"""

from typing import Generator, List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session
from redis import Redis

from app import crud, models, schemas
from app.core.config import settings
from app.db.session import SessionLocal
from app.core import security
from app.core.redis import get_redis_connection
from app.utils.logger import logger

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def get_db() -> Generator:
    """
    Get a database session.
    
    Yields:
        Session: SQLAlchemy session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis() -> Redis:
    """
    Get a Redis connection.
    
    Returns:
        Redis: Redis connection
    """
    return get_redis_connection()


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> models.User:
    """
    Get the current authenticated user.
    
    Args:
        db: SQLAlchemy session
        token: JWT token
        
    Returns:
        models.User: Current user
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError) as e:
        logger.warning(f"JWT token validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        logger.warning(f"User not found: {token_data.sub}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Update last activity in Redis
    redis = get_redis()
    redis.set(f"user:{user.id}:last_activity", "true", ex=settings.SESSION_LIFETIME_SECONDS)
    
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Get the current active user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        models.User: Current active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        logger.warning(f"Inactive user attempted to access API: {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


def check_user_role(required_roles: List[str]):
    """
    Check if user has required roles.
    
    Args:
        required_roles: List of required role names
        
    Returns:
        function: Dependency function to check user roles
    """
    def _check_user_role(
        current_user: models.User = Depends(get_current_active_user),
    ) -> models.User:
        # Superuser has all permissions
        if current_user.is_superuser:
            return current_user
        
        # Check if user has any of the required roles
        user_roles = current_user.role_names
        if not any(role in user_roles for role in required_roles):
            logger.warning(
                f"User {current_user.username} with roles {user_roles} "
                f"attempted to access a restricted endpoint requiring {required_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user doesn't have enough privileges",
            )
        return current_user
    
    return _check_user_role 