from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class StrategyType(str, Enum):
    AVALANCHE = "avalanche"
    SNOWBALL = "snowball"
    OPTIMAL = "optimal"

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

class StrategyComparisonResponse(BaseModel):
    avalanche: RepaymentPlanResponse
    snowball: RepaymentPlanResponse
    optimal: RepaymentPlanResponse
    best_strategy: str