"""
Authentication API endpoints for the 3X-UI Management System.

This module defines the API endpoints for user authentication and token management.
"""

from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from redis import Redis

from app import schemas, models, crud
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.utils.logger import logger

router = APIRouter()


@router.post("/login", response_model=schemas.Token)
async def login_access_token(
    db: Session = Depends(deps.get_db),
    redis: Redis = Depends(deps.get_redis),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # Authenticate user
    user = crud.user.authenticate(
        db, username_or_email=form_data.username, password=form_data.password
    )
    if not user:
        logger.warning(f"Failed login attempt for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    # Check if user is active
    if not user.is_active:
        logger.warning(f"Inactive user attempted to login: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    
    # Update last login timestamp
    crud.user.update_last_login(db, user_id=user.id)
    
    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    
    # Generate refresh token
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = security.create_refresh_token(
        subject=str(user.id), expires_delta=refresh_token_expires
    )
    
    # Store refresh token in Redis
    redis.setex(
        f"refresh_token:{user.id}",
        settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token
    )
    
    # Log successful login
    logger.info(f"User logged in: {user.username}")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh-token", response_model=schemas.Token)
async def refresh_token(
    db: Session = Depends(deps.get_db),
    redis: Redis = Depends(deps.get_redis),
    refresh_token: str = Body(...),
) -> Any:
    """
    Refresh access token using refresh token.
    """
    try:
        # Decode refresh token
        payload = security.decode_token(refresh_token)
        if payload.get("type") != "refresh":
            logger.warning(f"Invalid token type for refresh: {payload.get('type')}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Refresh token missing user ID")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        
        # Verify refresh token in Redis
        stored_token = redis.get(f"refresh_token:{user_id}")
        if not stored_token or stored_token.decode() != refresh_token:
            logger.warning(f"Invalid or expired refresh token for user ID: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        
        # Get user from database
        user = crud.user.get(db, id=int(user_id))
        if not user:
            logger.warning(f"User not found for refresh token: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        if not user.is_active:
            logger.warning(f"Inactive user attempted to refresh token: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )
        
        # Generate new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            subject=str(user.id), expires_delta=access_token_expires
        )
        
        # Generate new refresh token
        refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        new_refresh_token = security.create_refresh_token(
            subject=str(user.id), expires_delta=refresh_token_expires
        )
        
        # Update refresh token in Redis
        redis.setex(
            f"refresh_token:{user.id}",
            settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
            new_refresh_token
        )
        
        # Log successful token refresh
        logger.info(f"User refreshed token: {user.username}")
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
    
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


@router.post("/logout")
async def logout(
    redis: Redis = Depends(deps.get_redis),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Logout the current user by invalidating their refresh token.
    """
    # Remove refresh token from Redis
    redis.delete(f"refresh_token:{current_user.id}")
    
    # Log logout
    logger.info(f"User logged out: {current_user.username}")
    
    return {"message": "Successfully logged out"}


@router.post("/password-reset-request")
async def request_password_reset(
    email: str = Body(...),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Request a password reset.
    
    In a production environment, this would send an email with a reset token.
    For this example, we'll just log that a reset was requested.
    """
    user = crud.user.get_by_email(db, email=email)
    if user:
        # Generate reset token
        reset_token = security.create_password_reset_token(
            subject=str(user.id)
        )
        
        # In production, send email with reset token
        # For now, just log it
        logger.info(f"Password reset requested for user: {user.username}")
        logger.info(f"Password reset token: {reset_token}")
        
    # Always return success to prevent email enumeration
    return {"message": "If a registered email was provided, a password reset link was sent"}


@router.post("/password-reset")
async def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Reset password using a reset token.
    """
    try:
        # Decode reset token
        payload = security.decode_token(token)
        if payload.get("type") != "reset":
            logger.warning(f"Invalid token type for password reset: {payload.get('type')}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid reset token",
            )
        
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Reset token missing user ID")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid reset token",
            )
        
        # Get user from database
        user = crud.user.get(db, id=int(user_id))
        if not user:
            logger.warning(f"User not found for password reset: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        # Update user password
        crud.user.update(db, db_obj=user, obj_in={"password": new_password})
        
        # Log password reset
        logger.info(f"Password reset successful for user: {user.username}")
        
        return {"message": "Password successfully reset"}
    
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token for password reset",
        )


@router.get("/verify-token")
async def verify_token(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Verify that the access token is valid and return the current user.
    """
    return {"status": "ok", "user_id": current_user.id, "username": current_user.username}


@router.post("/register", response_model=schemas.User)
async def register(
    user_in: schemas.UserCreate,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Register a new user.
    """
    # Check if user with given email or username exists
    user_email = crud.user.get_by_email(db, email=user_in.email)
    if user_email:
        logger.warning(f"Registration attempt with existing email: {user_in.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    user_username = crud.user.get_by_username(db, username=user_in.username)
    if user_username:
        logger.warning(f"Registration attempt with existing username: {user_in.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    # Create new user
    user = crud.user.create(db, obj_in=user_in)
    logger.info(f"New user registered: {user.username}")
    
    return user


@router.post("/forgot-password")
async def forgot_password(
    email: str = Body(..., embed=True),
    db: Session = Depends(deps.get_db)
) -> Dict[str, str]:
    """
    Password recovery endpoint. Sends a password reset email to the user.
    """
    user = crud.user.get_by_email(db, email=email)
    
    if not user:
        # Don't reveal that the user doesn't exist
        logger.warning(f"Password recovery attempted for non-existent email: {email}")
        return {"message": "If your email is registered, you will receive a password reset link"}
    
    if not user.is_active:
        logger.warning(f"Password recovery attempted for inactive user: {email}")
        return {"message": "If your email is registered, you will receive a password reset link"}
    
    # In a real application, you would generate a password reset token
    # and send an email with a link to reset the password
    password_reset_token = security.create_access_token(
        user.id,
        expires_delta=timedelta(hours=24),
    )
    
    # Here you would send the email
    # send_reset_password_email(email_to=user.email, token=password_reset_token)
    
    logger.info(f"Password reset requested for user: {user.username}")
    
    return {"message": "Password reset email sent"}


@router.post("/reset-password")
async def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(deps.get_db)
) -> Dict[str, str]:
    """
    Reset password endpoint. Takes a token and new password.
    """
    try:
        # Decode the token
        payload = security.decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            logger.warning("User ID not found in password reset token")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token",
            )
        
        # Get the user
        user = crud.user.get(db, id=int(user_id))
        if not user or not user.is_active:
            logger.warning(f"User not found or inactive during password reset: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token",
            )
        
        # Update the password
        hashed_password = get_password_hash(new_password)
        user.hashed_password = hashed_password
        db.commit()
        
        logger.info(f"Password reset successful for user: {user.username}")
        
        return {"message": "Password reset successful"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token",
        ) 