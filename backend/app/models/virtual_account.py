"""Virtual account model for managing virtual accounts."""

from sqlalchemy import Boolean, Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from .base import Base


class AccountType(str, enum.Enum):
    """Enum for account types."""

    STANDARD = "standard"
    PREMIUM = "premium"
    VIP = "vip"


class AccountStatus(str, enum.Enum):
    """Enum for account statuses."""

    AVAILABLE = "available"
    SOLD = "sold"
    EXPIRED = "expired"
    DISABLED = "disabled"


class VirtualAccount(Base):
    """Virtual account model."""

    # Basic information
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    account_type = Column(Enum(AccountType), default=AccountType.STANDARD)
    status = Column(Enum(AccountStatus), default=AccountStatus.AVAILABLE)

    # Account details
    username = Column(String(100), unique=True)
    password = Column(String(255))
    server_address = Column(String(255))
    expiry_date = Column(String(10), nullable=True)  # YYYY-MM-DD format

    # Pricing
    price = Column(Integer, default=0)
    discount_price = Column(Integer, nullable=True)

    # Usage limits
    data_limit = Column(Integer, default=0)  # In GB
    speed_limit = Column(Integer, default=0)  # In Mbps
    concurrent_connections = Column(Integer, default=1)

    # Status flags
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    auto_renew = Column(Boolean, default=False)

    # Relationships
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    user = relationship("User", back_populates="accounts")
    order_id = Column(Integer, ForeignKey("order.id"), nullable=True)
    order = relationship("Order", back_populates="accounts")

    def __str__(self) -> str:
        """String representation of virtual account."""
        return f"{self.name} ({self.account_type})"

    @property
    def is_available(self) -> bool:
        """Check if account is available for purchase."""
        return self.status == AccountStatus.AVAILABLE and self.is_active

    @property
    def current_price(self) -> int:
        """Get current price (considering discounts)."""
        return self.discount_price if self.discount_price else self.price

    @property
    def has_discount(self) -> bool:
        """Check if account has active discount."""
        return bool(self.discount_price and self.discount_price < self.price) 