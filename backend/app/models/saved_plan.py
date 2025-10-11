# app/models/saved_plan.py
from beanie import Document
from pydantic import Field, BaseModel  # Add BaseModel to imports
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    SKIPPED = "skipped"

class MonthlyPayment(BaseModel):
    month_index: int
    due_date: Optional[datetime] = None
    paid_date: Optional[datetime] = None
    status: PaymentStatus = PaymentStatus.PENDING
    allocations: List[Dict[str, Any]]  # Store allocation details
    total_paid: float
    total_interest: float
    notes: Optional[str] = None

class SavedPlan(Document):
    clerk_user_id: str = Field(..., index=True)
    plan_name: str = Field(..., min_length=1, max_length=100)
    strategy: str  # avalanche, snowball, optimal
    monthly_budget: float
    
    # Plan details
    total_interest_paid: float
    months_to_debt_free: int
    original_total_debt: float
    
    # Payment tracking
    monthly_payments: List[MonthlyPayment] = []
    current_month: int = 0
    completed_months: int = 0
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    is_completed: bool = Field(default=False)
    
    class Settings:
        name = "saved_plans"
        indexes = [
            "clerk_user_id",
            "created_at",
            "is_active"
        ]
    
    def to_dict(self):
        data = self.model_dump()
        data['id'] = str(self.id)
        return data