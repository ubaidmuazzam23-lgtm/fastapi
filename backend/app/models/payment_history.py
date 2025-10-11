# app/models/payment_history.py
from beanie import Document
from pydantic import Field
from typing import Optional, Dict, Any
from datetime import datetime

class PaymentHistory(Document):
    clerk_user_id: str = Field(..., index=True)
    saved_plan_id: str = Field(..., index=True)
    debt_id: str = Field(..., index=True)
    
    # Payment details
    month_index: int
    payment_amount: float
    interest_amount: float
    principal_amount: float
    remaining_balance: float
    
    # Metadata
    payment_date: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    
    class Settings:
        name = "payment_history"
        indexes = [
            "clerk_user_id",
            "saved_plan_id",
            "debt_id",
            "payment_date"
        ]
    
    def to_dict(self):
        data = self.model_dump()
        data['id'] = str(self.id)
        return data