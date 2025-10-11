from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# ============================================
# SHARED ENUM
# ============================================
class StrategyType(str, Enum):
    AVALANCHE = "avalanche"
    SNOWBALL = "snowball"
    OPTIMAL = "optimal"

# ============================================
# REPAYMENT PLAN SCHEMAS (for /plans/generate, /plans/compare)
# Used by plan_service.py
# ============================================
class RepaymentPlanRequest(BaseModel):
    strategy: StrategyType
    monthly_budget: float = Field(..., gt=0)
    max_months: int = Field(default=60, ge=12, le=120)

class AllocationResponse(BaseModel):
    name: str
    payment: float
    interest_accrued: float
    principal_reduction: float

class RepaymentMonthResponse(BaseModel):
    month_index: int
    allocations: List[AllocationResponse]
    total_interest: float
    total_paid: float

class RepaymentPlanResponse(BaseModel):
    strategy_name: str
    months: List[RepaymentMonthResponse]
    total_interest_paid: float
    months_to_debt_free: int
    schedule_df: List[Dict[str, Any]]
    balance_series: List[float]
    error: Optional[str] = None  # For tenure violation errors

class StrategyComparisonResponse(BaseModel):
    avalanche: RepaymentPlanResponse
    snowball: RepaymentPlanResponse
    optimal: RepaymentPlanResponse
    best_strategy: str

# ============================================
# SAVED PLAN SCHEMAS (for /saved-plans)
# Used by saved_plans routes
# ============================================
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
    strategies: List[StrategyType] = Field(
        default=[StrategyType.AVALANCHE, StrategyType.SNOWBALL, StrategyType.OPTIMAL]
    )

class PlanComparisonResponse(BaseModel):
    comparisons: Dict[str, Dict[str, Any]]
    best_strategy: str
    user_debts_summary: Dict[str, Any]