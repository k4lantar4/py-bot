"""
User API endpoints for the 3X-UI Management System.

This module defines the API endpoints for user management.
"""

from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.utils.logger import logger

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
async def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0, description="Skip N items"),
    limit: int = Query(100, ge=1, le=1000, description="Limit to N items"),
    current_user: models.User = Depends(deps.check_user_role(["admin", "manager"])),
) -> Any:
    """
    Retrieve users.
    
    Requires admin or manager role.
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    logger.info(f"Retrieved {len(users)} users")
    return users


@router.post("/", response_model=schemas.User)
async def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(deps.check_user_role(["admin"])),
) -> Any:
    """
    Create new user.
    
    Requires admin role.
    """
    # Check if user with given email exists
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        logger.warning(f"Attempt to create user with existing email: {user_in.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Check if user with given username exists
    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        logger.warning(f"Attempt to create user with existing username: {user_in.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    # Create user
    user = crud.user.create(db, obj_in=user_in)
    logger.info(f"User created: {user.username}")
    return user


@router.get("/me", response_model=schemas.User)
async def read_user_me(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.put("/me", response_model=schemas.User)
async def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update current user.
    """
    # Prevent user from changing their own roles or superuser status
    if user_in.roles is not None:
        logger.warning(f"User {current_user.username} attempted to change their roles")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Changing roles not allowed",
        )
    
    if user_in.is_superuser is not None:
        logger.warning(f"User {current_user.username} attempted to change their superuser status")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Changing superuser status not allowed",
        )
    
    # Check email uniqueness if changing email
    if user_in.email is not None and user_in.email != current_user.email:
        user = crud.user.get_by_email(db, email=user_in.email)
        if user:
            logger.warning(f"User {current_user.username} attempted to change email to existing one: {user_in.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    
    # Check username uniqueness if changing username
    if user_in.username is not None and user_in.username != current_user.username:
        user = crud.user.get_by_username(db, username=user_in.username)
        if user:
            logger.warning(f"User {current_user.username} attempted to change username to existing one: {user_in.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
    
    # Update user
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    logger.info(f"User {user.username} updated their profile")
    return user


@router.put("/me/wallet", response_model=schemas.User)
async def update_user_wallet(
    *,
    db: Session = Depends(deps.get_db),
    wallet_update: schemas.WalletUpdate,
    current_user: models.User = Depends(deps.check_user_role(["admin"])),
) -> Any:
    """
    Update user wallet balance.
    
    Requires admin role.
    """
    user = crud.user.update_wallet_balance(
        db,
        user_id=current_user.id,
        amount=wallet_update.amount,
        operation=wallet_update.operation
    )
    
    if not user:
        logger.error(f"User not found for wallet update: {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    logger.info(f"User {user.username} wallet updated: {wallet_update.operation} {wallet_update.amount}")
    return user


@router.get("/{user_id}", response_model=schemas.User)
async def read_user_by_id(
    user_id: int = Path(..., gt=0, description="User ID"),
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    # Check if user is requesting their own information or has admin/manager role
    is_admin_or_manager = any(role in current_user.role_names for role in ["admin", "manager"])
    if user_id != current_user.id and not is_admin_or_manager:
        logger.warning(f"User {current_user.username} attempted to access another user's data: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    
    # Get user
    user = crud.user.get(db, id=user_id)
    if not user:
        logger.warning(f"Attempted to access non-existent user: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user


@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int = Path(..., gt=0, description="User ID"),
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.check_user_role(["admin"])),
) -> Any:
    """
    Update a user.
    
    Requires admin role.
    """
    # Get user
    user = crud.user.get(db, id=user_id)
    if not user:
        logger.warning(f"Attempted to update non-existent user: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check email uniqueness if changing email
    if user_in.email is not None and user_in.email != user.email:
        user_with_email = crud.user.get_by_email(db, email=user_in.email)
        if user_with_email:
            logger.warning(f"Attempted to update user {user_id} with existing email: {user_in.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    
    # Check username uniqueness if changing username
    if user_in.username is not None and user_in.username != user.username:
        user_with_username = crud.user.get_by_username(db, username=user_in.username)
        if user_with_username:
            logger.warning(f"Attempted to update user {user_id} with existing username: {user_in.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
    
    # Update user
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    logger.info(f"User {user.id} updated by admin {current_user.username}")
    return user


@router.delete("/{user_id}", response_model=schemas.User)
async def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int = Path(..., gt=0, description="User ID"),
    current_user: models.User = Depends(deps.check_user_role(["admin"])),
) -> Any:
    """
    Delete a user.
    
    Requires admin role.
    """
    # Prevent user from deleting themselves
    if user_id == current_user.id:
        logger.warning(f"User {current_user.username} attempted to delete themselves")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself",
        )
    
    # Get user
    user = crud.user.get(db, id=user_id)
    if not user:
        logger.warning(f"Attempted to delete non-existent user: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Delete user
    user = crud.user.delete(db, id=user_id)
    logger.info(f"User {user.username} deleted by admin {current_user.username}")
    return user


@router.get("/me/clients", response_model=List[schemas.UserClient])
async def read_user_clients(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0, description="Skip N items"),
    limit: int = Query(100, ge=1, le=1000, description="Limit to N items"),
) -> Any:
    """
    Get current user's clients.
    """
    # In a real implementation, you would get the user's clients from the database
    # For now, we'll return an empty list
    return []


@router.put("/{user_id}/roles", response_model=schemas.User)
async def update_user_roles(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int = Path(..., gt=0, description="User ID"),
    roles_update: schemas.UserRoleUpdate,
    current_user: models.User = Depends(deps.check_user_role(["admin"])),
) -> Any:
    """
    Update a user's roles.
    
    Requires admin role.
    """
    # Get user
    user = crud.user.get(db, id=user_id)
    if not user:
        logger.warning(f"Attempted to update roles for non-existent user: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Update user roles
    user = crud.user.update(db, db_obj=user, obj_in={"roles": roles_update.roles})
    logger.info(f"User {user.username} roles updated by admin {current_user.username}: {roles_update.roles}")
    return user


@router.put("/{user_id}/wallet", response_model=schemas.User)
async def update_user_wallet_by_id(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int = Path(..., gt=0, description="User ID"),
    wallet_update: schemas.WalletUpdate,
    current_user: models.User = Depends(deps.check_user_role(["admin"])),
) -> Any:
    """
    Update a user's wallet balance.
    
    Requires admin role.
    """
    # Get user
    user = crud.user.get(db, id=user_id)
    if not user:
        logger.warning(f"Attempted to update wallet for non-existent user: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Update user wallet
    user = crud.user.update_wallet_balance(
        db,
        user_id=user_id,
        amount=wallet_update.amount,
        operation=wallet_update.operation
    )
    
    logger.info(f"User {user.username} wallet updated by admin {current_user.username}: {wallet_update.operation} {wallet_update.amount}")
    return user 