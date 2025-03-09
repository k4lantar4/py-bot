"""
Message schemas for the 3X-UI Management System.

This module defines Pydantic models for message data validation and serialization.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field, validator

from app.models.message import MessageStatus, MessageType, MessageChannel


# Shared properties
class MessageBase(BaseModel):
    """
    Base schema for message data shared between requests.
    """
    sender_id: int = Field(..., gt=0, description="Sender user ID")
    subject: Optional[str] = Field(None, max_length=200, description="Message subject")
    content: str = Field(..., description="Message content")
    content_html: Optional[str] = Field(None, description="HTML version of the message content")
    message_type: MessageType = Field(..., description="Message type")
    channel: MessageChannel = Field(..., description="Message delivery channel")
    scheduled_for: Optional[datetime] = Field(None, description="When to send the message")
    template_id: Optional[str] = Field(None, description="Template ID for template-based messages")
    template_data: Optional[Dict[str, Any]] = Field(None, description="Data for template rendering")


class MessageCreate(MessageBase):
    """
    Schema for creating a new message.
    """
    recipient_ids: List[int] = Field(..., description="List of recipient user IDs")


class MessageUpdate(BaseModel):
    """
    Schema for updating an existing message.
    """
    subject: Optional[str] = Field(None, max_length=200, description="Message subject")
    content: Optional[str] = Field(None, description="Message content")
    content_html: Optional[str] = Field(None, description="HTML version of the message content")
    message_type: Optional[MessageType] = Field(None, description="Message type")
    channel: Optional[MessageChannel] = Field(None, description="Message delivery channel")
    status: Optional[MessageStatus] = Field(None, description="Message status")
    scheduled_for: Optional[datetime] = Field(None, description="When to send the message")
    template_id: Optional[str] = Field(None, description="Template ID for template-based messages")
    template_data: Optional[Dict[str, Any]] = Field(None, description="Data for template rendering")


class MessageInDBBase(MessageBase):
    """
    Base schema for messages retrieved from the database.
    """
    id: int
    status: MessageStatus
    created_at: datetime
    updated_at: datetime
    sent_at: Optional[datetime] = None
    total_recipients: int
    successful_deliveries: int
    failed_deliveries: int
    
    class Config:
        from_attributes = True


class Message(MessageInDBBase):
    """
    Schema for message data returned to clients.
    """
    is_scheduled: bool
    delivery_success_rate: float
    sender_name: Optional[str] = Field(None, description="Name of the sender")
    recipient_count: int = Field(..., description="Number of recipients")


class MessageInDB(MessageInDBBase):
    """
    Schema for message data stored in the database.
    """
    pass


class MessageRecipient(BaseModel):
    """
    Schema for message recipient data.
    """
    user_id: int = Field(..., gt=0, description="Recipient user ID")
    message_id: int = Field(..., gt=0, description="Message ID")
    status: MessageStatus = Field(..., description="Delivery status for this recipient")
    sent_at: Optional[datetime] = Field(None, description="When the message was sent to this recipient")
    delivered_at: Optional[datetime] = Field(None, description="When the message was delivered to this recipient")
    error: Optional[str] = Field(None, description="Error message if delivery failed")
    
    class Config:
        from_attributes = True


class BulkMessageRequest(BaseModel):
    """
    Schema for sending a bulk message.
    """
    recipient_ids: List[int] = Field(..., description="List of recipient user IDs")
    subject: Optional[str] = Field(None, max_length=200, description="Message subject")
    content: str = Field(..., description="Message content")
    content_html: Optional[str] = Field(None, description="HTML version of the message content")
    message_type: MessageType = Field(MessageType.ANNOUNCEMENT, description="Message type")
    channel: MessageChannel = Field(MessageChannel.EMAIL, description="Message delivery channel")
    scheduled_for: Optional[datetime] = Field(None, description="When to send the message")
    
    @validator("recipient_ids")
    def validate_recipients(cls, v):
        if not v:
            raise ValueError("At least one recipient is required")
        return v


class MessageStats(BaseModel):
    """
    Schema for message statistics data.
    """
    total_messages: int = Field(0, description="Total number of messages")
    sent_messages: int = Field(0, description="Number of sent messages")
    delivered_messages: int = Field(0, description="Number of delivered messages")
    failed_messages: int = Field(0, description="Number of failed messages")
    pending_messages: int = Field(0, description="Number of pending messages")
    delivery_success_rate: float = Field(0.0, description="Overall delivery success rate")
    
    class Config:
        from_attributes = True 