from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class ScenarioType(str, Enum):
    EXTRA_PAYMENT = "extra_payment"
    BUDGET_REDUCTION = "budget_reduction"
    INTEREST_RATE_CHANGE = "interest_rate_change"
    DEBT_CONSOLIDATION = "debt_consolidation"
    WINDFALL = "windfall"

class WhatIfRequest(BaseModel):
    scenario_type: ScenarioType
    base_budget: float = Field(..., gt=0)
    base_strategy: str = Field(default="avalanche")
    analysis_months: int = Field(default=60, ge=12, le=120)
    
    # Scenario-specific parameters
    extra_payment: Optional[float] = Field(default=0.0, ge=0)
    budget_reduction: Optional[float] = Field(default=0.0, ge=0)
    rate_change_percent: Optional[float] = Field(default=0.0)
    affected_debts: Optional[List[str]] = Field(default=[])
    consolidation_rate: Optional[float] = Field(default=0.0, ge=0, le=100)
    consolidation_fee: Optional[float] = Field(default=0.0, ge=0)
    windfall_amount: Optional[float] = Field(default=0.0, ge=0)
    windfall_month: Optional[int] = Field(default=1, ge=1)

class ScenarioComparison(BaseModel):
    baseline: Dict[str, Any]
    scenario: Dict[str, Any]
    interest_savings: float
    months_saved: int
    payment_difference: float
    insights: List[str]