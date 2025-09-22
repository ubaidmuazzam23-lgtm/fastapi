from typing import Optional
from beanie import PydanticObjectId
from datetime import datetime

from app.models.user import User
from app.schemas.user import UserCreate, UserProfileUpdate, UserResponse, UserProfileResponse

class UserService:
    @staticmethod
    async def create_user(user_data: UserCreate) -> User:
        """Create a new user"""
        user = User(**user_data.model_dump())
        await user.insert()
        return user
    
    @staticmethod
    async def get_user_by_clerk_id(clerk_user_id: str) -> Optional[User]:
        """Get user by Clerk user ID"""
        return await User.find_one(User.clerk_user_id == clerk_user_id)
    
    @staticmethod
    async def get_user_by_id(user_id: PydanticObjectId) -> Optional[User]:
        """Get user by MongoDB ObjectID"""
        return await User.get(user_id)
    
    @staticmethod
    async def update_user_profile(clerk_user_id: str, profile_data: UserProfileUpdate) -> Optional[User]:
        """Update user financial profile"""
        user = await UserService.get_user_by_clerk_id(clerk_user_id)
        if not user:
            return None
        
        update_data = profile_data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        await user.update({"$set": update_data})
        return await UserService.get_user_by_clerk_id(clerk_user_id)
    
    @staticmethod
    async def get_or_create_user(clerk_user_id: str, user_data: UserCreate) -> User:
        """Get existing user or create new one"""
        user = await UserService.get_user_by_clerk_id(clerk_user_id)
        if user:
            return user
        return await UserService.create_user(user_data)
    
    @staticmethod
    async def delete_user(clerk_user_id: str) -> bool:
        """Soft delete user"""
        user = await UserService.get_user_by_clerk_id(clerk_user_id)
        if not user:
            return False
        
        await user.update({"$set": {"is_active": False, "updated_at": datetime.utcnow()}})
        return True
    
    @staticmethod
    async def get_user_profile(clerk_user_id: str) -> Optional[UserProfileResponse]:
        """Get user financial profile with calculated fields"""
        user = await UserService.get_user_by_clerk_id(clerk_user_id)
        if not user:
            return None
        return UserProfileResponse.from_user(user)