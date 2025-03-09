"""
CRUD operations for role data.

This module provides CRUD operations for role data.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate


def get(db: Session, id: int) -> Optional[Role]:
    """
    Get a role by ID.
    
    Args:
        db: SQLAlchemy session
        id: Role ID
        
    Returns:
        Role: Role object or None
    """
    return db.query(Role).filter(Role.id == id).first()


def get_by_name(db: Session, name: str) -> Optional[Role]:
    """
    Get a role by name.
    
    Args:
        db: SQLAlchemy session
        name: Role name
        
    Returns:
        Role: Role object or None
    """
    return db.query(Role).filter(Role.name == name).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
    """
    Get multiple roles.
    
    Args:
        db: SQLAlchemy session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List[Role]: List of role objects
    """
    return db.query(Role).offset(skip).limit(limit).all()


def create(db: Session, obj_in: RoleCreate) -> Role:
    """
    Create a new role.
    
    Args:
        db: SQLAlchemy session
        obj_in: Role creation data
        
    Returns:
        Role: Created role object
    """
    db_obj = Role(
        name=obj_in.name,
        description=obj_in.description,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, db_obj: Role, obj_in: RoleUpdate) -> Role:
    """
    Update a role.
    
    Args:
        db: SQLAlchemy session
        db_obj: Role object to update
        obj_in: Role update data
        
    Returns:
        Role: Updated role object
    """
    if obj_in.name is not None:
        db_obj.name = obj_in.name
    if obj_in.description is not None:
        db_obj.description = obj_in.description
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, id: int) -> Optional[Role]:
    """
    Delete a role.
    
    Args:
        db: SQLAlchemy session
        id: Role ID
        
    Returns:
        Role: Deleted role object or None
    """
    db_obj = db.query(Role).filter(Role.id == id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj 