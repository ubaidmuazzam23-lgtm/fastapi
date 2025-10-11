from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List

from app.models.user import User
from app.schemas.user import (
    UserCreate, UserResponse, UserProfileUpdate, 
    UserProfileResponse, AuthResponse
)
from app.services.user_service import UserService
from app.services.notification_service import NotificationService
from app.api.dependencies import get_current_user, verify_clerk_token

router = APIRouter(prefix="/auth", tags=["authentication"])

# Test routes (no auth required)
@router.post("/test-register", response_model=AuthResponse)
async def test_register_user(user_data: UserCreate):
    """Test endpoint - create user without auth"""
    # Check if user already exists
    existing_user = await UserService.get_user_by_clerk_id(user_data.clerk_user_id)
    is_new_user = existing_user is None
    
    user = await UserService.get_or_create_user(
        clerk_user_id=user_data.clerk_user_id,
        user_data=user_data
    )
    
    # Send welcome email only for new users
    if is_new_user:
        await NotificationService.send_welcome_email(
            user_id=user.clerk_user_id,
            user_name=user.first_name or "User"
        )
    
    return AuthResponse(
        user=UserResponse(**user.to_dict()),
        message="Test user created successfully"
    )

@router.get("/test-users", response_model=List[UserResponse])
async def test_get_all_users():
    """Test endpoint - get all users from database"""
    users = await User.find_all().to_list()
    return [UserResponse(**user.to_dict()) for user in users]

@router.get("/test-profile/{clerk_user_id}", response_model=UserProfileResponse)
async def test_get_profile(clerk_user_id: str):
    """Test endpoint - get profile without auth"""
    user = await UserService.get_user_by_clerk_id(clerk_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserProfileResponse.from_user(user)

@router.put("/test-profile/{clerk_user_id}", response_model=UserProfileResponse)
async def test_update_profile(clerk_user_id: str, profile_data: UserProfileUpdate):
    """Test endpoint to update profile without auth"""
    updated_user = await UserService.update_user_profile(
        clerk_user_id=clerk_user_id,
        profile_data=profile_data
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserProfileResponse.from_user(updated_user)

# Real Clerk auth routes (updated with Request parameter)
@router.post("/register", response_model=AuthResponse)
async def register_user(
    request: Request,
    user_data: UserCreate,
    current_user: User = Depends(get_current_user)
):
    """Register/sync user with Clerk token"""
    # Check if this is a new user (first time registration)
    # The get_current_user dependency already created/fetched the user
    # We can check if user was just created by checking if they have any debts or data
    
    # Send welcome email (only sent once due to notification preferences)
    await NotificationService.send_welcome_email(
        user_id=current_user.clerk_user_id,
        user_name=current_user.first_name or "User"
    )
    
    return AuthResponse(
        user=UserResponse(**current_user.to_dict()),
        message="User authenticated successfully"
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    # Check if this is a brand new user (created within last 5 minutes)
    from datetime import datetime, timedelta
    time_since_creation = datetime.utcnow() - current_user.created_at
    
    # If user was created less than 1 minute ago, send welcome email
    if time_since_creation < timedelta(minutes=1):
        await NotificationService.send_welcome_email(
            user_id=current_user.clerk_user_id,
            user_name=current_user.first_name or "User"
        )
    
    return UserResponse(**current_user.to_dict())

@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get user financial profile"""
    return UserProfileResponse.from_user(current_user)

@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    request: Request,
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update user financial profile"""
    updated_user = await UserService.update_user_profile(
        clerk_user_id=current_user.clerk_user_id,
        profile_data=profile_data
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserProfileResponse.from_user(updated_user)

@router.delete("/account")
async def delete_user_account(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Soft delete user account"""
    success = await UserService.delete_user(current_user.clerk_user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "Account deleted successfully"}