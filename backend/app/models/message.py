"""
Message model for the 3X-UI Management System.

This module defines the SQLAlchemy ORM model for messages sent to users
via various channels (email, Telegram, etc.).
"""

import enum
from typing import List, Optional

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, JSON, func, Table
from sqlalchemy.orm import relationship

from app.db.session import Base


# Message status enumeration
class MessageStatus(str, enum.Enum):
    """
    Enumeration of message statuses.
    """
    DRAFT = "draft"
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Message type enumeration
class MessageType(str, enum.Enum):
    """
    Enumeration of message types.
    """
    ANNOUNCEMENT = "announcement"
    NOTIFICATION = "notification"
    MARKETING = "marketing"
    TRANSACTIONAL = "transactional"
    SUPPORT = "support"


# Message channel enumeration
class MessageChannel(str, enum.Enum):
    """
    Enumeration of message delivery channels.
    """
    EMAIL = "email"
    TELEGRAM = "telegram"
    SMS = "sms"
    PUSH = "push"
    SYSTEM = "system"  # In-app notification


# Message-recipient association table for many-to-many relationship
message_recipients = Table(
    "message_recipients",
    Base.metadata,
    Column("message_id", Integer, ForeignKey("messages.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("status", Enum(MessageStatus), default=MessageStatus.QUEUED),
    Column("sent_at", DateTime, nullable=True),
    Column("delivered_at", DateTime, nullable=True),
    Column("error", Text, nullable=True),
)


class Message(Base):
    """
    SQLAlchemy model for messages.
    """
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Message content
    subject = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    content_html = Column(Text, nullable=True)  # HTML version for email
    
    # Message metadata
    message_type = Column(Enum(MessageType), nullable=False)
    channel = Column(Enum(MessageChannel), nullable=False)
    status = Column(Enum(MessageStatus), default=MessageStatus.DRAFT)
    scheduled_for = Column(DateTime, nullable=True)  # When to send
    template_id = Column(String, nullable=True)  # For template-based messages
    template_data = Column(JSON, nullable=True)  # Data for template rendering
    
    # Message tracking
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    sent_at = Column(DateTime, nullable=True)
    total_recipients = Column(Integer, default=0)
    successful_deliveries = Column(Integer, default=0)
    failed_deliveries = Column(Integer, default=0)
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id])
    recipients = relationship(
        "User",
        secondary=message_recipients,
        backref="received_messages"
    )
    
    @property
    def is_scheduled(self) -> bool:
        """
        Check if the message is scheduled for future delivery.
        
        Returns:
            True if scheduled, False otherwise
        """
        if not self.scheduled_for:
            return False
        return self.scheduled_for > func.now()
    
    @property
    def delivery_success_rate(self) -> float:
        """
        Calculate the message delivery success rate.
        
        Returns:
            Success rate as a percentage
        """
        if self.total_recipients == 0:
            return 0.0
        return (self.successful_deliveries / self.total_recipients) * 100.0 