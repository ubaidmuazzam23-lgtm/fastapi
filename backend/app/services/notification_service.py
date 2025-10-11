"""
Notification Service - Handles Email notifications with FinanceBrews branding
app/services/notification_service.py
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, Dict, Any
from datetime import datetime
from io import BytesIO
import logging

from app.models.notification import Notification, NotificationPreference
from app.models.user import User
from app.config.settings import settings
from app.services.pdf_service import PDFService

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Email configuration from settings
SMTP_HOST = settings.SMTP_HOST
SMTP_PORT = settings.SMTP_PORT
SMTP_USER = settings.SMTP_USER
SMTP_PASSWORD = settings.SMTP_PASSWORD
FROM_EMAIL = settings.FROM_EMAIL
APP_NAME = "FinanceBrews"

# Debug logging
print(f"DEBUG: Email config loaded - SMTP_USER: {SMTP_USER}, SMTP_HOST: {SMTP_HOST}, SMTP_PORT: {SMTP_PORT}")


class NotificationService:
    
    # ============ EMAIL TEMPLATES ============
    
    @staticmethod
    def get_welcome_email(user_name: str) -> Dict[str, str]:
        """Welcome email template - FinanceBrews themed"""
        return {
            "subject": f"Welcome to FinanceBrews - Let's Brew Your Financial Freedom!",
            "body": f"""
            <html>
                <body style="font-family: 'Arial', sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #FEF3C7 0%, #FED7AA 100%);">
                    <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.15);">
                        
                        <!-- Header with Coffee Icon -->
                        <div style="background: linear-gradient(135deg, #92400E 0%, #B45309 100%); padding: 40px 30px; text-align: center;">
                            <div style="font-size: 48px; margin-bottom: 10px;">☕</div>
                            <h1 style="color: white; margin: 0; font-size: 28px; font-weight: bold;">Welcome to FinanceBrews!</h1>
                            <p style="color: #FED7AA; margin-top: 10px; font-size: 16px;">Brewing Your Way to Financial Freedom</p>
                        </div>
                        
                        <!-- Main Content -->
                        <div style="padding: 40px 30px;">
                            <p style="color: #451A03; font-size: 18px; line-height: 1.6; margin: 0 0 20px 0;">
                                Hey {user_name},
                            </p>
                            <p style="color: #78350F; font-size: 16px; line-height: 1.7; margin: 0 0 20px 0;">
                                Welcome to the FinanceBrews family! Just like brewing the perfect cup of coffee, achieving financial freedom takes the right ingredients, 
                                the perfect temperature, and a little patience. We're here to guide you through every step of your journey.
                            </p>
                            
                            <!-- Features Box -->
                            <div style="background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%); border-left: 4px solid #D97706; padding: 25px; border-radius: 10px; margin: 30px 0;">
                                <h3 style="color: #92400E; margin: 0 0 15px 0; font-size: 18px;">Your Financial Brew Includes:</h3>
                                <ul style="margin: 0; padding-left: 20px; color: #78350F;">
                                    <li style="margin-bottom: 10px; line-height: 1.6;">
                                        <strong>Smart Debt Tracking</strong> - All your debts in one aromatic blend
                                    </li>
                                    <li style="margin-bottom: 10px; line-height: 1.6;">
                                        <strong>AI-Powered Strategies</strong> - Personalized recipes for debt freedom
                                    </li>
                                    <li style="margin-bottom: 10px; line-height: 1.6;">
                                        <strong>Credit Score Boost</strong> - Watch your score percolate to new heights
                                    </li>
                                    <li style="margin-bottom: 10px; line-height: 1.6;">
                                        <strong>24/7 AI Advisor</strong> - Your financial barista, always ready to help
                                    </li>
                                </ul>
                            </div>
                        </div>
                        
                        <!-- Footer -->
                        <div style="background: #FFFBEB; padding: 25px 30px; text-align: center; border-top: 1px solid #FED7AA;">
                            <p style="color: #92400E; margin: 0; font-size: 13px; line-height: 1.6;">
                                You're receiving this because you joined FinanceBrews.<br>
                                Made with coffee and financial wisdom in India
                            </p>
                        </div>
                    </div>
                </body>
            </html>
            """
        }
    
    @staticmethod
    def get_debt_created_email(user_name: str, debt_name: str, debt_amount: float) -> Dict[str, str]:
        """Debt created confirmation email - FinanceBrews themed"""
        return {
            "subject": f"Debt Added to Your Brew - {debt_name}",
            "body": f"""
            <html>
                <body style="font-family: 'Arial', sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #FEF3C7 0%, #FED7AA 100%);">
                    <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.15);">
                        
                        <!-- Header -->
                        <div style="background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%); padding: 35px 30px; text-align: center;">
                            <div style="font-size: 42px; margin-bottom: 10px;">✅</div>
                            <h1 style="color: white; margin: 0; font-size: 26px; font-weight: bold;">Debt Successfully Added!</h1>
                        </div>
                        
                        <!-- Main Content -->
                        <div style="padding: 40px 30px;">
                            <p style="color: #451A03; font-size: 18px; line-height: 1.6; margin: 0 0 20px 0;">
                                Hi {user_name},
                            </p>
                            <p style="color: #78350F; font-size: 16px; line-height: 1.7; margin: 0 0 25px 0;">
                                Great job taking the first step! We've added this debt to your financial blend. Every great brew starts with knowing your ingredients.
                            </p>
                            
                            <!-- Debt Details Card -->
                            <div style="background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%); border-left: 4px solid #3B82F6; padding: 25px; border-radius: 10px; margin: 25px 0;">
                                <h3 style="color: #1E40AF; margin: 0 0 15px 0; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">Debt Details</h3>
                                <div style="margin-bottom: 15px;">
                                    <span style="color: #1E3A8A; font-size: 14px; display: block; margin-bottom: 5px;">Name</span>
                                    <span style="color: #1E3A8A; font-size: 20px; font-weight: bold;">{debt_name}</span>
                                </div>
                                <div>
                                    <span style="color: #1E3A8A; font-size: 14px; display: block; margin-bottom: 5px;">Amount</span>
                                    <span style="color: #1E40AF; font-size: 28px; font-weight: bold;">₹{debt_amount:,.2f}</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Footer -->
                        <div style="background: #FFFBEB; padding: 25px 30px; text-align: center; border-top: 1px solid #FED7AA;">
                            <p style="color: #92400E; margin: 0; font-size: 13px;">
                                Keep brewing your financial success!<br>
                                - The FinanceBrews Team
                            </p>
                        </div>
                    </div>
                </body>
            </html>
            """
        }
    
    # ============ CORE EMAIL SENDING ============
    
    @staticmethod
    async def send_email(to_email: str, subject: str, body: str) -> bool:
        """Send email using SMTP"""
        try:
            print(f"DEBUG: Starting email send")
            print(f"   To: {to_email}")
            print(f"   From: {FROM_EMAIL}")
            print(f"   Subject: {subject}")
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = FROM_EMAIL
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach HTML body
            html_part = MIMEText(body, 'html')
            msg.attach(html_part)
            
            print(f"   Connecting to SMTP server...")
            # Send email
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                print(f"   Starting TLS...")
                server.starttls()
                print(f"   Logging in...")
                server.login(SMTP_USER, SMTP_PASSWORD)
                print(f"   Sending message...")
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to {to_email}")
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ ERROR: Failed to send email to {to_email}")
            print(f"   Error: {str(e)}")
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    @staticmethod
    async def send_email_with_attachment(to_email: str, subject: str, body: str, attachment_data: BytesIO, filename: str) -> bool:
        """Send email with PDF attachment"""
        try:
            print(f"📧 Sending email with attachment to {to_email}")
            
            msg = MIMEMultipart('mixed')
            msg['From'] = FROM_EMAIL
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach HTML body
            html_part = MIMEText(body, 'html')
            msg.attach(html_part)
            
            # Attach PDF
            pdf_part = MIMEBase('application', 'pdf')
            pdf_part.set_payload(attachment_data.read())
            encoders.encode_base64(pdf_part)
            pdf_part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            msg.attach(pdf_part)
            
            # Send
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
            
            print(f"✅ Email with attachment sent successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email with attachment: {str(e)}")
            logger.error(f"Failed to send email with attachment: {str(e)}")
            return False
    
    # ============ NOTIFICATION TRIGGERS ============
    
    @staticmethod
    async def send_notification(
        user_id: str,
        notification_type: str,
        subject: str,
        body: str
    ) -> Optional[Notification]:
        """
        Main method to send notification and log it
        """
        try:
            # Get user
            user = await User.find_one(User.clerk_user_id == user_id)
            if not user:
                logger.error(f"User not found: {user_id}")
                return None
            
            # Check preferences
            prefs = await NotificationPreference.find_one(
                NotificationPreference.user_id == user_id
            )
            
            # Create default preferences if not exists
            if not prefs:
                prefs = NotificationPreference(user_id=user_id)
                await prefs.insert()
            
            # Check if this notification type is enabled
            if not prefs.email_enabled:
                logger.info(f"Email notifications disabled for user {user_id}")
                return None
            
            type_enabled = getattr(prefs, f"{notification_type}_emails", True)
            if not type_enabled:
                logger.info(f"{notification_type} emails disabled for user {user_id}")
                return None
            
            # Create notification record
            notification = Notification(
                user_id=user_id,
                notification_type=notification_type,
                subject=subject,
                message=body,
                status="pending"
            )
            await notification.insert()
            
            # Send email
            success = await NotificationService.send_email(
                to_email=user.email,
                subject=subject,
                body=body
            )
            
            # Update notification status
            notification.status = "sent" if success else "failed"
            notification.sent_at = datetime.utcnow() if success else None
            if not success:
                notification.error_message = "SMTP send failed"
            
            await notification.save()
            
            return notification
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            return None
    
    # ============ PLAN & PAYMENT EMAIL METHODS ============
    
    @staticmethod
    async def send_plan_saved_email(user_id: str, user_name: str, plan_data: Dict[str, Any]):
        """Send email with PDF when plan is saved"""
        try:
            # Generate PDF
            pdf_buffer = PDFService.create_repayment_plan_pdf(plan_data)
            
            # Email template
            subject = f"Your Repayment Plan: {plan_data.get('plan_name')} - FinanceBrews"
            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px; background: linear-gradient(135deg, #FEF3C7 0%, #FED7AA 100%);">
                    <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 15px; padding: 30px;">
                        <div style="text-align: center; margin-bottom: 20px;">
                            <div style="font-size: 48px;">☕</div>
                            <h1 style="color: #92400E; margin: 10px 0;">Plan Saved Successfully!</h1>
                        </div>
                        
                        <p style="color: #78350F; font-size: 16px; line-height: 1.6;">
                            Hi {user_name},
                        </p>
                        
                        <p style="color: #78350F; font-size: 16px; line-height: 1.6;">
                            Great news! Your repayment plan "<strong>{plan_data.get('plan_name')}</strong>" has been saved successfully. 
                            We've attached a detailed PDF with your complete payment schedule.
                        </p>
                        
                        <div style="background: #FEF3C7; border-left: 4px solid #D97706; padding: 20px; margin: 20px 0; border-radius: 5px;">
                            <h3 style="color: #92400E; margin: 0 0 10px 0;">Plan Summary</h3>
                            <ul style="color: #78350F; margin: 0; padding-left: 20px;">
                                <li>Strategy: {plan_data.get('strategy')}</li>
                                <li>Monthly Budget: Rs.{plan_data.get('monthly_budget', 0):,.2f}</li>
                                <li>Time to Debt-Free: {plan_data.get('months_to_debt_free', 0)} months</li>
                                <li>Total Interest: Rs.{plan_data.get('total_interest_paid', 0):,.2f}</li>
                            </ul>
                        </div>
                        
                        <p style="color: #78350F; font-size: 14px;">
                            Your detailed payment schedule is attached as a PDF. Keep it handy for reference!
                        </p>
                        
                        <div style="text-align: center; margin-top: 30px;">
                            <p style="color: #92400E; font-size: 12px;">
                                Keep brewing your financial success!<br>
                                - The FinanceBrews Team
                            </p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            # Get user email
            user = await User.find_one(User.clerk_user_id == user_id)
            if not user:
                return None
            
            # Send email with PDF
            filename = f"repayment_plan_{plan_data.get('plan_name', 'plan').replace(' ', '_')}.pdf"
            success = await NotificationService.send_email_with_attachment(
                to_email=user.email,
                subject=subject,
                body=body,
                attachment_data=pdf_buffer,
                filename=filename
            )
            
            # Create notification record
            notification = Notification(
                user_id=user_id,
                notification_type="plan_saved",
                subject=subject,
                message=body,
                status="sent" if success else "failed",
                sent_at=datetime.utcnow() if success else None
            )
            await notification.insert()
            
            return notification
            
        except Exception as e:
            logger.error(f"Error sending plan saved email: {str(e)}")
            return None
    
    @staticmethod
    async def send_payment_receipt_email(user_id: str, user_name: str, payment_data: Dict[str, Any]):
        """Send email with PDF receipt when payment is marked complete"""
        try:
            # Generate PDF receipt
            pdf_buffer = PDFService.create_payment_receipt_pdf(payment_data)
            
            # Email template
            subject = f"Payment Confirmation - Month {payment_data.get('month_index', 0) + 1} - FinanceBrews"
            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px; background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);">
                    <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 15px; padding: 30px;">
                        <div style="text-align: center; margin-bottom: 20px;">
                            <div style="font-size: 48px;">✅</div>
                            <h1 style="color: #059669; margin: 10px 0;">Payment Recorded!</h1>
                        </div>
                        
                        <p style="color: #065F46; font-size: 16px; line-height: 1.6;">
                            Hi {user_name},
                        </p>
                        
                        <p style="color: #065F46; font-size: 16px; line-height: 1.6;">
                            Excellent progress! Your payment for <strong>Month {payment_data.get('month_index', 0) + 1}</strong> has been recorded successfully.
                        </p>
                        
                        <div style="background: #ECFDF5; border-left: 4px solid #059669; padding: 20px; margin: 20px 0; border-radius: 5px;">
                            <h3 style="color: #059669; margin: 0 0 10px 0;">Payment Details</h3>
                            <ul style="color: #065F46; margin: 0; padding-left: 20px;">
                                <li>Total Payment: Rs.{payment_data.get('total_paid', 0):,.2f}</li>
                                <li>Interest Paid: Rs.{payment_data.get('total_interest', 0):,.2f}</li>
                                <li>Principal Paid: Rs.{payment_data.get('total_paid', 0) - payment_data.get('total_interest', 0):,.2f}</li>
                                <li>Completed Payments: {payment_data.get('completed_months', 0)} / {payment_data.get('total_months', 0)}</li>
                            </ul>
                        </div>
                        
                        <p style="color: #065F46; font-size: 14px;">
                            Your payment receipt is attached as a PDF for your records.
                        </p>
                        
                        <div style="text-align: center; margin-top: 30px; padding: 20px; background: #FEF3C7; border-radius: 10px;">
                            <p style="color: #92400E; font-size: 16px; margin: 0; font-weight: bold;">
                                You're {payment_data.get('progress_percentage', 0):.1f}% of the way to debt freedom!
                            </p>
                        </div>
                        
                        <div style="text-align: center; margin-top: 20px;">
                            <p style="color: #92400E; font-size: 12px;">
                                Keep brewing your financial success!<br>
                                - The FinanceBrews Team
                            </p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            # Get user email
            user = await User.find_one(User.clerk_user_id == user_id)
            if not user:
                return None
            
            # Send email with PDF
            filename = f"payment_receipt_month_{payment_data.get('month_index', 0) + 1}.pdf"
            success = await NotificationService.send_email_with_attachment(
                to_email=user.email,
                subject=subject,
                body=body,
                attachment_data=pdf_buffer,
                filename=filename
            )
            
            # Create notification record
            notification = Notification(
                user_id=user_id,
                notification_type="payment_receipt",
                subject=subject,
                message=body,
                status="sent" if success else "failed",
                sent_at=datetime.utcnow() if success else None
            )
            await notification.insert()
            
            return notification
            
        except Exception as e:
            logger.error(f"Error sending payment receipt email: {str(e)}")
            return None
    
    # ============ CONVENIENCE METHODS ============
    
    @staticmethod
    async def send_welcome_email(user_id: str, user_name: str):
        """Send welcome email when user signs up"""
        print(f"DEBUG: ATTEMPTING TO SEND WELCOME EMAIL")
        print(f"   User ID: {user_id}")
        print(f"   User Name: {user_name}")
        
        template = NotificationService.get_welcome_email(user_name)
        result = await NotificationService.send_notification(
            user_id=user_id,
            notification_type="welcome",
            subject=template["subject"],
            body=template["body"]
        )
        
        print(f"   Result: {result}")
        return result
    
    @staticmethod
    async def send_debt_created_email(user_id: str, user_name: str, debt_name: str, debt_amount: float):
        """Send email when debt is created"""
        template = NotificationService.get_debt_created_email(user_name, debt_name, debt_amount)
        return await NotificationService.send_notification(
            user_id=user_id,
            notification_type="debt_notifications",
            subject=template["subject"],
            body=template["body"]
        )
    
    # ============ PREFERENCE MANAGEMENT ============
    
    @staticmethod
    async def get_preferences(user_id: str) -> Optional[NotificationPreference]:
        """Get user notification preferences"""
        prefs = await NotificationPreference.find_one(
            NotificationPreference.user_id == user_id
        )
        if not prefs:
            # Create default preferences
            prefs = NotificationPreference(user_id=user_id)
            await prefs.insert()
        return prefs
    
    @staticmethod
    async def update_preferences(user_id: str, preferences_data: Dict[str, bool]) -> Optional[NotificationPreference]:
        """Update user notification preferences"""
        prefs = await NotificationService.get_preferences(user_id)
        if not prefs:
            return None
        
        # Update fields
        for key, value in preferences_data.items():
            if hasattr(prefs, key):
                setattr(prefs, key, value)
        
        prefs.updated_at = datetime.utcnow()
        await prefs.save()
        return prefs