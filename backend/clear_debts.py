import asyncio
import motor.motor_asyncio
from app.config.settings import settings

async def clear_old_debts():
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
    database = client[settings.DATABASE_NAME]
    
    # Clear all old debt records
    result = await database.debts.delete_many({})
    print(f"Deleted {result.deleted_count} old debt records")
    
    client.close()
    print("Database cleared successfully!")

if __name__ == "__main__":
    asyncio.run(clear_old_debts())