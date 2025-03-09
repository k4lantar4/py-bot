"""
CRUD operations for the 3X-UI Management System.

This module imports all CRUD operations for the application.
"""

from app.crud.user import (  # noqa
    get,
    get_by_email,
    get_by_username,
    get_multi,
    get_count,
    create,
    update,
    delete,
    authenticate,
    update_last_login,
    update_wallet_balance,
)

from app.crud import role  # noqa 