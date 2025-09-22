# app/models/plan.py
from beanie import Document
from pydantic import Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class StrategyType(str, Enum):
    AVALANCHE = "avalanche"
    SNOWBALL = "snowball"  
    OPTIMAL = "optimal"

class Plan(Document):
    clerk_user_id: str = Field(..., index=True)
    plan_name: str = Field(..., min_length=1, max_length=100)
    strategy: StrategyType
    monthly_budget: float = Field(..., ge=0)
    max_months: int = Field(default=60, ge=1, le=120)
    
    # Plan results
    total_months: Optional[int] = None
    total_interest: Optional[float] = None
    total_payments: Optional[float] = None
    monthly_schedule: Optional[List[Dict[str, Any]]] = None
    balance_trajectory: Optional[List[float]] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    class Settings:
        name = "plans"
        indexes = [
            "clerk_user_id",
            "strategy",
            "created_at"
        ]
    
    def to_dict(self):
        data = self.model_dump()
        data['id'] = str(self.id)
        return data

# app/schemas/plan.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class StrategyType(str, Enum):
    AVALANCHE = "avalanche"
    SNOWBALL = "snowball"
    OPTIMAL = "optimal"

class PlanCreate(BaseModel):
    plan_name: str = Field(..., min_length=1, max_length=100)
    strategy: StrategyType
    monthly_budget: float = Field(..., ge=0)
    max_months: int = Field(default=60, ge=1, le=120)

class PlanUpdate(BaseModel):
    plan_name: Optional[str] = Field(None, min_length=1, max_length=100)
    strategy: Optional[StrategyType] = None
    monthly_budget: Optional[float] = Field(None, ge=0)
    max_months: Optional[int] = Field(None, ge=1, le=120)

class AllocationData(BaseModel):
    name: str
    payment: float
    interest_accrued: float
    principal_reduction: float

class MonthlyScheduleItem(BaseModel):
    month: int
    total_payment: float
    total_interest: float
    total_principal: float
    allocations: List[AllocationData]
    remaining_balance: float

class PlanResponse(BaseModel):
    id: str
    plan_name: str
    strategy: StrategyType
    monthly_budget: float
    max_months: int
    total_months: Optional[int]
    total_interest: Optional[float]
    total_payments: Optional[float]
    created_at: datetime
    updated_at: datetime
    is_active: bool

class PlanDetailsResponse(PlanResponse):
    monthly_schedule: Optional[List[MonthlyScheduleItem]]
    balance_trajectory: Optional[List[float]]
    summary_metrics: Optional[Dict[str, Any]]

class PlanGenerateRequest(BaseModel):
    strategy: StrategyType
    monthly_budget: float = Field(..., ge=0)
    max_months: int = Field(default=60, ge=1, le=120)
    save_plan: bool = Field(default=False)
    plan_name: Optional[str] = None

class PlanComparisonRequest(BaseModel):
    monthly_budget: float = Field(..., ge=0)
    max_months: int = Field(default=60, ge=1, le=120)
    strategies: List[StrategyType] = Field(default=[StrategyType.AVALANCHE, StrategyType.SNOWBALL, StrategyType.OPTIMAL])

class PlanComparisonResponse(BaseModel):
    comparisons: Dict[str, Dict[str, Any]]
    best_strategy: str
    user_debts_summary: Dict[str, Any]