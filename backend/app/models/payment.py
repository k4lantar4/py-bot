"""Payment model for managing payments."""

from sqlalchemy import Boolean, Column, Integer, String, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
import enum

from .base import Base


class PaymentStatus(str, enum.Enum):
    """Enum for payment statuses."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentProvider(str, enum.Enum):
    """Enum for payment providers."""

    ZARINPAL = "zarinpal"
    CARD = "card"
    WALLET = "wallet"


class Payment(Base):
    """Payment model."""

    # Payment information
    payment_id = Column(String(100), unique=True, index=True)
    amount = Column(Integer, nullable=False)
    currency = Column(String(3), default="IRR")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    provider = Column(Enum(PaymentProvider), nullable=False)

    # Provider-specific information
    provider_payment_id = Column(String(100), nullable=True)
    provider_status = Column(String(50), nullable=True)
    provider_message = Column(Text, nullable=True)

    # Card payment information (for card-to-card payments)
    card_number = Column(String(16), nullable=True)
    card_holder = Column(String(100), nullable=True)
    reference_number = Column(String(50), nullable=True)

    # Relationships
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="payments")
    order = relationship("Order", back_populates="payment", uselist=False)

    # Additional information
    description = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    is_test = Column(Boolean, default=False)

    def __str__(self) -> str:
        """String representation of payment."""
        return f"Payment {self.payment_id} ({self.status})"

    @property
    def is_successful(self) -> bool:
        """Check if payment is successful."""
        return self.status == PaymentStatus.COMPLETED

    @property
    def is_pending(self) -> bool:
        """Check if payment is pending."""
        return self.status == PaymentStatus.PENDING

    @property
    def is_failed(self) -> bool:
        """Check if payment failed."""
        return self.status == PaymentStatus.FAILED

    @property
    def is_refunded(self) -> bool:
        """Check if payment is refunded."""
        return self.status == PaymentStatus.REFUNDED

    @property
    def can_be_refunded(self) -> bool:
        """Check if payment can be refunded."""
        return self.status == PaymentStatus.COMPLETED

    @property
    def formatted_amount(self) -> str:
        """Get formatted amount with currency."""
        if self.currency == "IRR":
            return f"{self.amount:,} ریال"
        elif self.currency == "IRT":
            return f"{self.amount:,} تومان"
        return f"{self.amount:,} {self.currency}" 