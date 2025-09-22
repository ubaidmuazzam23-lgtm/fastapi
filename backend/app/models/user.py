from beanie import Document
from pydantic import EmailStr, Field
from typing import Optional
from datetime import datetime

class User(Document):
    clerk_user_id: str = Field(..., unique=True, index=True)
    email: str  # Changed back to str to avoid email validation issues
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_image_url: Optional[str] = None
    
    # Financial profile
    monthly_income: float = Field(default=0.0, ge=0)
    monthly_expenses: float = Field(default=0.0, ge=0) 
    extra_payment: float = Field(default=0.0, ge=0)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    class Settings:
        name = "users"
        indexes = [
            "clerk_user_id",
            "email", 
            "created_at"
        ]

    def to_dict(self):
        """Convert to dictionary with proper ID handling"""
        data = self.model_dump()
        data['id'] = str(self.id)
        return data