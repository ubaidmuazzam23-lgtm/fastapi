# from pydantic import BaseModel, Field
# from typing import Optional, List
# from datetime import datetime

# class DebtCreate(BaseModel):
#     name: str = Field(..., min_length=1, max_length=100)
#     total_amount: float = Field(..., ge=0)
#     interest_rate: float = Field(..., ge=0, le=100)

# class DebtUpdate(BaseModel):
#     name: Optional[str] = Field(None, min_length=1, max_length=100)
#     total_amount: Optional[float] = Field(None, ge=0)
#     interest_rate: Optional[float] = Field(None, ge=0, le=100)

# class DebtResponse(BaseModel):
#     id: str
#     name: str
#     total_amount: float
#     interest_rate: float
#     created_at: datetime
#     updated_at: datetime
#     is_active: bool

# class UserFinancialProfile(BaseModel):
#     monthly_income: float = Field(..., ge=0)
#     monthly_expenses: float = Field(..., ge=0)

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DebtCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    total_amount: float = Field(..., ge=0)
    interest_rate: float = Field(..., ge=0, le=100)
    min_payment: float = Field(default=0.0, ge=0)  # Add this field

class DebtUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    total_amount: Optional[float] = Field(None, ge=0)
    interest_rate: Optional[float] = Field(None, ge=0, le=100)
    min_payment: Optional[float] = Field(None, ge=0)  # Add this field

class DebtResponse(BaseModel):
    id: str
    name: str
    total_amount: float
    interest_rate: float
    min_payment: float  # Add this field
    created_at: datetime
    updated_at: datetime
    is_active: bool

class UserFinancialProfile(BaseModel):
    monthly_income: float = Field(..., ge=0)
    monthly_expenses: float = Field(..., ge=0)
