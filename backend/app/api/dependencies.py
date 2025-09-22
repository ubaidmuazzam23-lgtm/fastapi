from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Optional
from app.models.user import User
from app.services.user_service import UserService
from app.config.settings import settings

security = HTTPBearer()

async def verify_clerk_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify Clerk JWT token"""
    token = credentials.credentials
    try:
        # Decode without verification for development
        payload = jwt.decode(token, options={"verify_signature": False})
        if not payload.get("sub"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        return payload
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}"
        )

async def get_current_user(
    token_payload: dict = Depends(verify_clerk_token),
    request: Request = None
) -> User:
    """Get current authenticated user, create if doesn't exist"""
    clerk_user_id = token_payload.get("sub")
    user = await UserService.get_user_by_clerk_id(clerk_user_id)
    
    if not user:
        # Try to get user info from custom headers first (sent from frontend)
        email = None
        first_name = None
        last_name = None
        profile_image_url = None
        
        if request:
            email = request.headers.get('x-user-email')
            first_name = request.headers.get('x-user-first-name')
            last_name = request.headers.get('x-user-last-name')
            profile_image_url = request.headers.get('x-user-image')
        
        # Fall back to token data if headers not available
        if not email:
            email = (
                token_payload.get("email") or
                token_payload.get("email_address") or
                f"{clerk_user_id}@clerk.user"
            )
        if not first_name:
            first_name = token_payload.get("first_name") or token_payload.get("given_name")
        if not last_name:
            last_name = token_payload.get("last_name") or token_payload.get("family_name")
        if not profile_image_url:
            profile_image_url = token_payload.get("picture") or token_payload.get("image_url")
        
        print(f"DEBUG: Creating user with email: {email}")
        
        from app.schemas.user import UserCreate
        user_data = UserCreate(
            clerk_user_id=clerk_user_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            profile_image_url=profile_image_url
        )
        user = await UserService.create_user(user_data)
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    return user

# Additional dependency for credit-specific operations
async def get_current_user_with_debts(
    user: User = Depends(get_current_user)
) -> User:
    """Get current user and ensure they have debt data for credit analysis"""
    # This can be used for endpoints that specifically need debt data
    # You can add additional validation here if needed
    return user

# Dependency for admin-only operations (if needed)
async def get_admin_user(
    user: User = Depends(get_current_user)
) -> User:
    """Get current user and verify admin privileges"""
    if not getattr(user, 'is_admin', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user