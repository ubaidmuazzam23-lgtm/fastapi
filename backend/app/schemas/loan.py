from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Request schemas
class LoanRecommendationRequest(BaseModel):
    """User's loan request"""
    loan_type: str = Field(..., description="personal, business, home, auto, education")
    requested_amount: float = Field(..., ge=0, description="Loan amount needed")
    purpose: Optional[str] = Field(None, description="Purpose of loan")
    preferred_term_months: Optional[int] = Field(None, ge=6, le=360, description="Preferred repayment term")
    max_monthly_payment: Optional[float] = Field(None, ge=0, description="Maximum affordable monthly payment")


# Response schemas
class LoanOption(BaseModel):
    """Individual loan option details"""
    lender_name: str
    loan_type: str
    interest_rate: float
    apr: float
    monthly_payment: float
    total_interest: float
    total_cost: float
    term_months: int
    
    # Fees
    origination_fee: Optional[float] = 0.0
    processing_fee: Optional[float] = 0.0
    prepayment_penalty: bool = False
    
    # Requirements
    min_credit_score: Optional[int] = None
    min_income: Optional[float] = None
    max_dti_ratio: Optional[float] = None
    
    # Match score
    suitability_score: float = Field(..., ge=0, le=100, description="How well this loan matches user's profile")
    approval_probability: float = Field(..., ge=0, le=100, description="Estimated approval probability")
    
    # Additional info
    features: List[str] = Field(default_factory=list)
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    
    source_url: Optional[str] = None


class AffordabilityAnalysis(BaseModel):
    """User's affordability analysis"""
    monthly_income: float
    monthly_expenses: float
    available_budget: float
    total_existing_debt: float
    existing_monthly_debt_payments: float
    
    # Ratios
    debt_to_income_ratio: float
    debt_to_income_with_loan: float
    
    # Affordability
    max_affordable_monthly: float
    max_affordable_loan_amount: float
    is_affordable: bool
    affordability_score: float = Field(..., ge=0, le=100)
    
    # Risk assessment
    risk_level: str = Field(..., description="low, moderate, high")
    recommendations: List[str] = Field(default_factory=list)


class LoanComparisonData(BaseModel):
    """Data for visual comparison"""
    loan_id: str
    lender_name: str
    monthly_payment: float
    total_interest: float
    total_cost: float
    term_months: int
    monthly_savings_vs_highest: float
    total_savings_vs_highest: float


class LoanRecommendationResponse(BaseModel):
    """Complete loan recommendation response"""
    id: str
    clerk_user_id: str
    loan_type: str
    requested_amount: float
    
    # Analysis
    affordability_analysis: AffordabilityAnalysis
    
    # Recommendations
    recommended_loans: List[LoanOption]
    comparison_data: List[LoanComparisonData]
    
    # Summary
    best_overall: Optional[str] = None  # lender name
    lowest_rate: Optional[str] = None
    lowest_payment: Optional[str] = None
    lowest_total_cost: Optional[str] = None
    
    status: str
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "loan_type": "personal",
                "requested_amount": 10000,
                "recommended_loans": [],
                "affordability_analysis": {}
            }
        }


class LoanRecommendationListResponse(BaseModel):
    """List of past recommendations"""
    recommendations: List[Dict[str, Any]]
    total: int


class RefreshLoanDataRequest(BaseModel):
    """Request to refresh loan data from sources"""
    loan_type: Optional[str] = None
    force_refresh: bool = Field(default=False, description="Force refresh even if data is recent")