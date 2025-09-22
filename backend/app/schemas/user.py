from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# Base schema matching your Streamlit UserProfile
class UserProfileBase(BaseModel):
    monthly_income: float = Field(default=0.0, ge=0)
    monthly_expenses: float = Field(default=0.0, ge=0) 
    extra_payment: float = Field(default=0.0, ge=0)

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(BaseModel):
    monthly_income: Optional[float] = Field(None, ge=0)
    monthly_expenses: Optional[float] = Field(None, ge=0)
    extra_payment: Optional[float] = Field(None, ge=0)

class UserCreate(BaseModel):
    clerk_user_id: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_image_url: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    clerk_user_id: str
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str] 
    profile_image_url: Optional[str]
    monthly_income: float
    monthly_expenses: float
    extra_payment: float
    created_at: datetime
    updated_at: datetime
    is_active: bool

class UserProfileResponse(UserProfileBase):
    """Response matching your Streamlit UserProfile with calculated fields"""
    available_budget: float = Field(description="Income - Expenses")
    total_debt_budget: float = Field(description="Available + Extra payment")
    
    @classmethod
    def from_user(cls, user) -> "UserProfileResponse":
        available_budget = max(0, user.monthly_income - user.monthly_expenses)
        total_debt_budget = available_budget + user.extra_payment
        
        return cls(
            monthly_income=user.monthly_income,
            monthly_expenses=user.monthly_expenses, 
            extra_payment=user.extra_payment,
            available_budget=available_budget,
            total_debt_budget=total_debt_budget
        )

# Auth-related schemas
class TokenData(BaseModel):
    clerk_user_id: Optional[str] = None

class AuthResponse(BaseModel):
    user: UserResponse
    message: str