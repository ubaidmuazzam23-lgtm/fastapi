# app/schemas/saved_plan.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    SKIPPED = "skipped"

class SavePlanRequest(BaseModel):
    plan_name: str = Field(..., min_length=1, max_length=100)
    plan_data: Dict[str, Any]  # The generated plan response

class MonthlyPaymentResponse(BaseModel):
    month_index: int
    status: PaymentStatus
    due_date: Optional[datetime] = None
    paid_date: Optional[datetime] = None
    total_paid: float
    total_interest: float
    allocations: List[Dict[str, Any]]
    notes: Optional[str] = None

class SavedPlanResponse(BaseModel):
    id: str
    plan_name: str
    strategy: str
    monthly_budget: float
    total_interest_paid: float
    months_to_debt_free: int
    original_total_debt: float
    current_month: int
    completed_months: int
    progress_percentage: float
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    monthly_payments: List[MonthlyPaymentResponse]

class MarkPaymentRequest(BaseModel):
    month_index: int
    payment_date: Optional[datetime] = None
    notes: Optional[str] = None