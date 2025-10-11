# ============================================
# FILE 3: backend/app/api/routes/notifications.py
# ============================================
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.models.user import User
from app.models.notification import Notification, NotificationPreference
from app.services.notification_service import NotificationService
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])


# ============ SCHEMAS ============

class NotificationPreferenceUpdate(BaseModel):
    email_enabled: bool = Field(default=True)
    welcome_emails: bool = Field(default=True)
    debt_notifications: bool = Field(default=True)
    payment_reminders: bool = Field(default=True)
    milestone_celebrations: bool = Field(default=True)
    monthly_reports: bool = Field(default=True)
    tips_and_education: bool = Field(default=True)


class NotificationResponse(BaseModel):
    id: str
    notification_type: str
    subject: str
    status: str
    sent_at: Optional[str]
    created_at: str


class TestEmailRequest(BaseModel):
    email_type: str = Field(..., description="welcome, debt_created, payment_reminder, milestone, monthly_report")
    
    
# ============ ROUTES ============

@router.get("/preferences")
async def get_notification_preferences(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get current user's notification preferences"""
    prefs = await NotificationService.get_preferences(current_user.clerk_user_id)
    return {
        "email_enabled": prefs.email_enabled,
        "welcome_emails": prefs.welcome_emails,
        "debt_notifications": prefs.debt_notifications,
        "payment_reminders": prefs.payment_reminders,
        "milestone_celebrations": prefs.milestone_celebrations,
        "monthly_reports": prefs.monthly_reports,
        "tips_and_education": prefs.tips_and_education
    }


@router.put("/preferences")
async def update_notification_preferences(
    request: Request,
    preferences: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update notification preferences"""
    updated_prefs = await NotificationService.update_preferences(
        user_id=current_user.clerk_user_id,
        preferences_data=preferences.model_dump()
    )
    
    if not updated_prefs:
        raise HTTPException(status_code=404, detail="Preferences not found")
    
    return {
        "message": "Preferences updated successfully",
        "preferences": {
            "email_enabled": updated_prefs.email_enabled,
            "welcome_emails": updated_prefs.welcome_emails,
            "debt_notifications": updated_prefs.debt_notifications,
            "payment_reminders": updated_prefs.payment_reminders,
            "milestone_celebrations": updated_prefs.milestone_celebrations,
            "monthly_reports": updated_prefs.monthly_reports,
            "tips_and_education": updated_prefs.tips_and_education
        }
    }


@router.get("/history")
async def get_notification_history(
    request: Request,
    current_user: User = Depends(get_current_user),
    limit: int = 20
):
    """Get notification history for current user"""
    notifications = await Notification.find(
        Notification.user_id == current_user.clerk_user_id
    ).sort(-Notification.created_at).limit(limit).to_list()
    
    return {
        "notifications": [
            {
                "id": str(notif.id),
                "notification_type": notif.notification_type,
                "subject": notif.subject,
                "status": notif.status,
                "sent_at": notif.sent_at.isoformat() if notif.sent_at else None,
                "created_at": notif.created_at.isoformat()
            }
            for notif in notifications
        ]
    }


@router.post("/test/{email_type}")
async def send_test_notification(
    email_type: str,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Test endpoint to send different types of emails
    email_type: welcome, debt_created, payment_reminder, milestone, monthly_report
    """
    user_name = current_user.first_name or "User"
    
    result = None
    
    if email_type == "welcome":
        result = await NotificationService.send_welcome_email(
            user_id=current_user.clerk_user_id,
            user_name=user_name
        )
    
    elif email_type == "debt_created":
        result = await NotificationService.send_debt_created_email(
            user_id=current_user.clerk_user_id,
            user_name=user_name,
            debt_name="Test Credit Card",
            debt_amount=50000.0
        )
    
    elif email_type == "payment_reminder":
        result = await NotificationService.send_payment_reminder(
            user_id=current_user.clerk_user_id,
            user_name=user_name,
            debt_name="Test Loan",
            due_date="2025-10-15"
        )
    
    elif email_type == "milestone":
        result = await NotificationService.send_milestone_email(
            user_id=current_user.clerk_user_id,
            user_name=user_name,
            milestone="First ₹10,000 paid off",
            amount_paid=10000.0
        )
    
    elif email_type == "monthly_report":
        result = await NotificationService.send_monthly_report(
            user_id=current_user.clerk_user_id,
            user_name=user_name,
            total_debt=100000.0,
            paid_this_month=5000.0,
            interest_saved=1200.0
        )
    
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid email_type. Use: welcome, debt_created, payment_reminder, milestone, monthly_report"
        )
    
    if result:
        return {
            "message": f"Test {email_type} email sent successfully!",
            "notification_id": str(result.id),
            "status": result.status
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to send test email")