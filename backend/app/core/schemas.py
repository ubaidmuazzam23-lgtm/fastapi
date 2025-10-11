


from pydantic import BaseModel, Field
from typing import List, Optional

class Debt(BaseModel):
    name: str
    balance: float
    apr: float
    min_payment: float
    
    # NEW FIELDS FOR TENURE TRACKING
    loan_type: str = "revolving"  # "revolving" or "fixed_term"
    original_tenure_months: Optional[int] = None
    remaining_months: Optional[int] = None
    fixed_emi: Optional[float] = None

class Allocation(BaseModel):
    name: str
    payment: float
    interest_accrued: float
    principal_reduction: float

class RepaymentMonth(BaseModel):
    month_index: int
    allocations: List[Allocation]
    total_interest: float
    total_paid: float

class RepaymentPlan(BaseModel):
    strategy: str
    months: List[RepaymentMonth]
    total_interest_paid: float
    months_to_debt_free: int
    error: Optional[str] = None  # For reporting tenure constraint violations
