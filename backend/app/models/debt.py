from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class Debt(Document):
    clerk_user_id: str = Field(..., index=True)
    name: str = Field(..., min_length=1, max_length=100)
    total_amount: float = Field(..., ge=0)
    interest_rate: float = Field(..., ge=0, le=100)
    min_payment: float = Field(default=0.0, ge=0)
    
    # NEW FIELDS FOR TENURE
    loan_type: str = Field(default="revolving")  # "revolving" or "fixed_term"
    original_tenure_months: Optional[int] = Field(default=None, ge=1)
    remaining_months: Optional[int] = Field(default=None, ge=0)
    fixed_emi: Optional[float] = Field(default=None, ge=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    class Settings:
        name = "debts"
        indexes = [
            "clerk_user_id",
            "created_at"
        ]
    
    def to_dict(self):
        data = self.model_dump()
        data['id'] = str(self.id)
        # Ensure all fields exist with defaults
        data.setdefault('loan_type', 'revolving')
        data.setdefault('original_tenure_months', None)
        data.setdefault('remaining_months', None)
        data.setdefault('fixed_emi', None)
        data.setdefault('min_payment', 0.0)
        return data
    
    def calculate_monthly_interest(self):
        return self.total_amount * (self.interest_rate / 100 / 12)
    
    def calculate_required_emi(self) -> float:
        """Calculate EMI needed to pay off in remaining tenure"""
        if not self.remaining_months or self.remaining_months == 0:
            return getattr(self, 'min_payment', self.total_amount * (self.interest_rate / 100) / 12 * 0.02)
        
        P = self.total_amount
        r = (self.interest_rate / 100) / 12
        n = self.remaining_months
        
        if r > 0:
            # Standard EMI formula
            emi = P * r * (1 + r)**n / ((1 + r)**n - 1)
        else:
            # No interest case
            emi = P / n
        
        return max(emi, getattr(self, 'min_payment', 0))