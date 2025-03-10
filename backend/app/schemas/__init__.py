"""
Schemas for the 3X-UI Management System.

This module imports all schemas for the application.
"""

from .token import Token, TokenPayload  # noqa
from .user import (  # noqa
    User,
    UserCreate,
    UserUpdate,
    UserInDB,
    UserRoleUpdate,
    WalletUpdate,
    UserClient,
)
from .role import Role, RoleCreate, RoleUpdate  # noqa
from .location import Location, LocationCreate, LocationUpdate, LocationInDB
from .server import Server, ServerCreate, ServerUpdate, ServerInDB, ServerStatus, ServerStats
from .service import Service, ServiceCreate, ServiceUpdate, ServiceInDB, ServiceStats
from .order import Order, OrderCreate, OrderUpdate, OrderInDB, OrderStats
from .order import Payment, PaymentCreate, PaymentUpdate, PaymentInDB
from .discount import Discount, DiscountCreate, DiscountUpdate, DiscountInDB
from .discount import DiscountApply, DiscountApplyResponse
from .message import Message, MessageCreate, MessageUpdate, MessageInDB
from .message import MessageRecipient, BulkMessageRequest, MessageStats 