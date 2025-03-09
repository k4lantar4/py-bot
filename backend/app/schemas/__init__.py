"""
Schemas for the 3X-UI Management System.

This module imports all schemas for the application.
"""

from app.schemas.token import Token, TokenPayload  # noqa
from app.schemas.user import (  # noqa
    User,
    UserCreate,
    UserUpdate,
    UserInDB,
    UserRoleUpdate,
    WalletUpdate,
    UserClient,
)
from app.schemas.role import Role, RoleCreate, RoleUpdate  # noqa
from app.schemas.location import Location, LocationCreate, LocationUpdate, LocationInDB
from app.schemas.server import Server, ServerCreate, ServerUpdate, ServerInDB, ServerStatus, ServerStats
from app.schemas.service import Service, ServiceCreate, ServiceUpdate, ServiceInDB, ServiceStats
from app.schemas.order import Order, OrderCreate, OrderUpdate, OrderInDB, OrderStats
from app.schemas.order import Payment, PaymentCreate, PaymentUpdate, PaymentInDB
from app.schemas.discount import Discount, DiscountCreate, DiscountUpdate, DiscountInDB
from app.schemas.discount import DiscountApply, DiscountApplyResponse
from app.schemas.message import Message, MessageCreate, MessageUpdate, MessageInDB
from app.schemas.message import MessageRecipient, BulkMessageRequest, MessageStats 