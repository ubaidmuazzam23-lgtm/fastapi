from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

class DebtCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    total_amount: float = Field(..., ge=0)
    interest_rate: float = Field(..., ge=0, le=100)
    min_payment: float = Field(default=0.0, ge=0)
    
    # NEW FIELDS with defaults
    loan_type: str = Field(default="revolving")
    original_tenure_months: Optional[int] = Field(default=None, ge=1)
    remaining_months: Optional[int] = Field(default=None, ge=0)
    fixed_emi: Optional[float] = Field(default=None, ge=0)
    
    @field_validator('loan_type')
    def validate_loan_type(cls, v):
        if v not in ['revolving', 'fixed_term']:
            return 'revolving'
        return v

class DebtUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    total_amount: Optional[float] = Field(None, ge=0)
    interest_rate: Optional[float] = Field(None, ge=0, le=100)
    min_payment: Optional[float] = Field(None, ge=0)
    
    # NEW FIELDS
    loan_type: Optional[str] = Field(default=None)
    original_tenure_months: Optional[int] = Field(default=None, ge=1)
    remaining_months: Optional[int] = Field(default=None, ge=0)
    fixed_emi: Optional[float] = Field(default=None, ge=0)

class DebtResponse(BaseModel):
    id: str
    name: str
    total_amount: float
    interest_rate: float
    min_payment: float = 0.0
    
    # NEW FIELDS with defaults for backward compatibility
    loan_type: str = "revolving"
    original_tenure_months: Optional[int] = None
    remaining_months: Optional[int] = None
    fixed_emi: Optional[float] = None
    
    created_at: datetime
    updated_at: datetime
    is_active: bool

class UserFinancialProfile(BaseModel):
    monthly_income: float = Field(..., ge=0)
    monthly_expenses: float = Field(..., ge=0)