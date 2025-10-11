

import motor.motor_asyncio
from beanie import init_beanie
from app.config.settings import settings
from app.models.user import User
from app.models.debt import Debt
from app.models.credit_profile import CreditProfile
from app.models.loan_recommendation import LoanRecommendation, LoanData
from app.models.notification import Notification, NotificationPreference
from app.models.saved_plan import SavedPlan  # Add this import
from app.models.payment_history import PaymentHistory  # Add this import

client = None
database = None

async def init_database():
    global client, database
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[settings.DATABASE_NAME]
    
    await init_beanie(
        database=database,
        document_models=[
            User, 
            Debt, 
            CreditProfile,
            LoanRecommendation,
            LoanData,
            Notification,
            NotificationPreference,
            SavedPlan,           # Add this
            PaymentHistory       # Add this
        ]
    )
    print(f"Database initialized: {settings.DATABASE_NAME}")

async def close_database():
    global client
    if client:
        client.close()