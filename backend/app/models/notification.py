# ============================================
# FILE 1: backend/app/models/notification.py
# ============================================
from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class Notification(Document):
    user_id: str = Field(..., index=True)  # clerk_user_id
    
    # Notification details
    notification_type: str = Field(...)  # 'welcome', 'debt_created', 'payment_reminder', etc.
    subject: str = Field(...)
    message: str = Field(...)
    
    # Delivery status
    status: str = Field(default="pending")  # 'pending', 'sent', 'failed'
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "notifications"
        indexes = [
            "user_id",
            "notification_type",
            "status",
            "created_at"
        ]


class NotificationPreference(Document):
    user_id: str = Field(..., unique=True, index=True)  # clerk_user_id
    
    # Email preferences
    email_enabled: bool = Field(default=True)
    
    # Notification types enabled/disabled
    welcome_emails: bool = Field(default=True)
    debt_notifications: bool = Field(default=True)
    payment_reminders: bool = Field(default=True)
    milestone_celebrations: bool = Field(default=True)
    monthly_reports: bool = Field(default=True)
    tips_and_education: bool = Field(default=True)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "notification_preferences"
        indexes = ["user_id"]
