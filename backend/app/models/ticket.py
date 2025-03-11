"""Ticket model for managing support tickets."""

from sqlalchemy import Boolean, Column, Integer, String, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
import enum

from .base import Base


class TicketStatus(str, enum.Enum):
    """Enum for ticket statuses."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING = "waiting"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, enum.Enum):
    """Enum for ticket priorities."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketCategory(str, enum.Enum):
    """Enum for ticket categories."""

    GENERAL = "general"
    TECHNICAL = "technical"
    BILLING = "billing"
    ACCOUNT = "account"
    OTHER = "other"


class Ticket(Base):
    """Ticket model."""

    # Basic information
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM)
    category = Column(Enum(TicketCategory), default=TicketCategory.GENERAL)

    # Relationships
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="tickets")
    assigned_to_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    replies = relationship("TicketReply", back_populates="ticket")

    # Additional information
    order_id = Column(Integer, ForeignKey("order.id"), nullable=True)
    order = relationship("Order")
    account_id = Column(Integer, ForeignKey("virtualaccount.id"), nullable=True)
    account = relationship("VirtualAccount")
    metadata = Column(JSON, nullable=True)

    def __str__(self) -> str:
        """String representation of ticket."""
        return f"Ticket #{self.id} - {self.title} ({self.status})"

    @property
    def is_open(self) -> bool:
        """Check if ticket is open."""
        return self.status in [TicketStatus.OPEN, TicketStatus.IN_PROGRESS]

    @property
    def is_closed(self) -> bool:
        """Check if ticket is closed."""
        return self.status in [TicketStatus.RESOLVED, TicketStatus.CLOSED]

    @property
    def can_be_reopened(self) -> bool:
        """Check if ticket can be reopened."""
        return self.status in [TicketStatus.RESOLVED, TicketStatus.CLOSED]


class TicketReply(Base):
    """Ticket reply model."""

    # Basic information
    content = Column(Text, nullable=False)
    is_staff_reply = Column(Boolean, default=False)

    # Relationships
    ticket_id = Column(Integer, ForeignKey("ticket.id"), nullable=False)
    ticket = relationship("Ticket", back_populates="replies")
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User")

    def __str__(self) -> str:
        """String representation of ticket reply."""
        return f"Reply to Ticket #{self.ticket_id} by {self.user.display_name}" 