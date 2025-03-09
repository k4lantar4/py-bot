"""
User CRUD operations for the 3X-UI Management System.

This module provides CRUD operations for user data.
"""

from typing import Any, Dict, Optional, Union, List
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate


def get(db: Session, id: int) -> Optional[User]:
    """
    Get a user by ID.
    
    Args:
        db: Database session
        id: User ID
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.id == id).first()


def get_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get a user by email.
    
    Args:
        db: Database session
        email: User email
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.email == email).first()


def get_by_username(db: Session, username: str) -> Optional[User]:
    """
    Get a user by username.
    
    Args:
        db: Database session
        username: Username
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.username == username).first()


def get_multi(
    db: Session, 
    *, 
    skip: int = 0, 
    limit: int = 100,
    is_active: Optional[bool] = None
) -> List[User]:
    """
    Get multiple users with pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        is_active: Filter by active status
        
    Returns:
        List of users
    """
    query = db.query(User)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    return query.offset(skip).limit(limit).all()


def get_count(
    db: Session, 
    *, 
    is_active: Optional[bool] = None
) -> int:
    """
    Get count of users.
    
    Args:
        db: Database session
        is_active: Filter by active status
        
    Returns:
        Count of users
    """
    query = db.query(User)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    return query.count()


def create(db: Session, *, obj_in: UserCreate) -> User:
    """
    Create a new user.
    
    Args:
        db: Database session
        obj_in: User creation data
        
    Returns:
        Created user
    """
    db_obj = User(
        email=obj_in.email,
        username=obj_in.username,
        hashed_password=get_password_hash(obj_in.password),
        full_name=obj_in.full_name,
        is_active=obj_in.is_active,
        is_superuser=obj_in.is_superuser,
        wallet_balance=0.0,
        is_verified=False,
        phone=obj_in.phone,
        telegram_id=obj_in.telegram_id,
        language=obj_in.language,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    # Add roles
    for role_name in obj_in.roles:
        db.execute(
            "INSERT INTO user_roles (user_id, role) VALUES (:user_id, :role)",
            {"user_id": db_obj.id, "role": role_name}
        )
    db.commit()
    
    return db_obj


def update(
    db: Session, 
    *, 
    db_obj: User, 
    obj_in: Union[UserUpdate, Dict[str, Any]]
) -> User:
    """
    Update a user.
    
    Args:
        db: Database session
        db_obj: User to update
        obj_in: User update data
        
    Returns:
        Updated user
    """
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)
    
    # Handle password
    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    
    # Handle roles
    if "roles" in update_data and update_data["roles"]:
        # Delete existing roles
        db.execute(
            "DELETE FROM user_roles WHERE user_id = :user_id",
            {"user_id": db_obj.id}
        )
        
        # Add new roles
        for role_name in update_data["roles"]:
            db.execute(
                "INSERT INTO user_roles (user_id, role) VALUES (:user_id, :role)",
                {"user_id": db_obj.id, "role": role_name}
            )
        
        # Remove roles from update data to prevent SQLAlchemy error
        del update_data["roles"]
    
    # Update user fields
    for field in update_data:
        if hasattr(db_obj, field):
            setattr(db_obj, field, update_data[field])
    
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, *, id: int) -> User:
    """
    Delete a user.
    
    Args:
        db: Database session
        id: User ID
        
    Returns:
        Deleted user
    """
    obj = db.query(User).get(id)
    
    # Delete roles
    db.execute(
        "DELETE FROM user_roles WHERE user_id = :user_id",
        {"user_id": id}
    )
    
    db.delete(obj)
    db.commit()
    return obj


def authenticate(
    db: Session, 
    *, 
    username_or_email: str, 
    password: str
) -> Optional[User]:
    """
    Authenticate a user.
    
    Args:
        db: Database session
        username_or_email: Username or email
        password: Password
        
    Returns:
        User if authentication succeeds, None otherwise
    """
    # Check if input is email
    if "@" in username_or_email:
        user = get_by_email(db, email=username_or_email)
    else:
        user = get_by_username(db, username=username_or_email)
    
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_last_login(db: Session, *, user_id: int) -> User:
    """
    Update the last login timestamp for a user.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Updated user
    """
    user = get(db, id=user_id)
    if user:
        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)
    return user


def update_wallet_balance(
    db: Session, 
    *, 
    user_id: int, 
    amount: float, 
    operation: str
) -> User:
    """
    Update a user's wallet balance.
    
    Args:
        db: Database session
        user_id: User ID
        amount: Amount to add or subtract
        operation: 'add' or 'subtract'
        
    Returns:
        Updated user
    """
    user = get(db, id=user_id)
    if not user:
        return None
    
    if operation == "add":
        user.wallet_balance += amount
    elif operation == "subtract":
        if user.wallet_balance >= amount:
            user.wallet_balance -= amount
        else:
            user.wallet_balance = 0
    
    db.commit()
    db.refresh(user)
    return user 