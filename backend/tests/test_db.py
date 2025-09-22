import asyncio
from app.config.database import init_database
from app.models.user import User

async def test_database():
    await init_database()
    
    # Test user creation
    test_user = User(
        clerk_user_id="test_123",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        monthly_income=50000,
        monthly_expenses=30000,
        extra_payment=2000
    )
    
    await test_user.insert()
    print(f"User created: {test_user.id}")
    
    # Test user retrieval
    found_user = await User.find_one(User.clerk_user_id == "test_123")
    print(f"User found: {found_user.email}")
    
    return found_user

if __name__ == "__main__":
    asyncio.run(test_database())