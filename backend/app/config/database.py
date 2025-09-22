# import motor.motor_asyncio
# from beanie import init_beanie
# from app.config.settings import settings
# from app.models.user import User
# from app.models.debt import Debt  # Add Debt import

# client = None
# database = None

# async def init_database():
#     global client, database
    
#     client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
#     database = client[settings.DATABASE_NAME]
    
#     await init_beanie(
#         database=database,
#         document_models=[User, Debt]  # Add Debt model
#     )
    
#     print(f"Database initialized: {settings.DATABASE_NAME}")

# async def close_database():
#     global client
#     if client:
#         client.close()
import motor.motor_asyncio
from beanie import init_beanie
from app.config.settings import settings
from app.models.user import User
from app.models.debt import Debt
from app.models.credit_profile import CreditProfile  # Add this import

client = None
database = None

async def init_database():
    global client, database
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[settings.DATABASE_NAME]
    
    await init_beanie(
        database=database,
        document_models=[User, Debt, CreditProfile]  # Add CreditProfile here
    )
    print(f"Database initialized: {settings.DATABASE_NAME}")

async def close_database():
    global client
    if client:
        client.close()

# import motor.motor_asyncio
# from beanie import init_beanie
# from app.config.settings import settings
# from app.models.user import User
# from app.models.debt import Debt
# from app.models.credit_profile import CreditProfile, CreditAction, CreditMonitoring, CreditRecommendation  # Add these imports

# client = None
# database = None

# async def init_database():
#     global client, database
#     client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
#     database = client[settings.DATABASE_NAME]
    
#     await init_beanie(
#         database=database,
#         document_models=[
#             User, 
#             Debt,
#             CreditProfile,  # Add credit models
#             CreditAction,
#             CreditMonitoring,
#             CreditRecommendation
#         ]
#     )
#     print(f"Database initialized: {settings.DATABASE_NAME}")

# async def close_database():
#     global client
#     if client:
#         client.close()






# async def get_db():
#     if database is None:
#         raise RuntimeError("Database not initialized. Call init_database() first.")
#     return database



# # Add this function for dependency injection
# async def get_database():
#     return database