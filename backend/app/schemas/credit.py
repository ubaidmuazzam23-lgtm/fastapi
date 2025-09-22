# app/schemas/credit.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.credit_profile import PaymentHistoryStatus, CreditAccountType

class CreditProfileCreate(BaseModel):
    """Create credit profile request"""
    current_score: Optional[int] = Field(None, ge=300, le=850)
    target_score: int = Field(750, ge=300, le=850)
    last_checked: str = Field(default="never_checked")
    payment_history: PaymentHistoryStatus = Field(default=PaymentHistoryStatus.ALWAYS_ON_TIME)
    average_account_age_years: float = Field(default=3.0, ge=0, le=50)
    new_accounts_last_2_years: int = Field(default=0, ge=0, le=20)
    account_types: List[CreditAccountType] = Field(default=[CreditAccountType.CREDIT_CARD])

class CreditProfileUpdate(BaseModel):
    """Update credit profile request"""
    current_score: Optional[int] = Field(None, ge=300, le=850)
    target_score: Optional[int] = Field(None, ge=300, le=850)
    last_checked: Optional[str] = None
    payment_history: Optional[PaymentHistoryStatus] = None
    average_account_age_years: Optional[float] = Field(None, ge=0, le=50)
    new_accounts_last_2_years: Optional[int] = Field(None, ge=0, le=20)
    account_types: Optional[List[CreditAccountType]] = None

class CreditFactorsAssessment(BaseModel):
    """Current credit factors for assessment"""
    payment_history: PaymentHistoryStatus
    average_account_age_years: float
    new_accounts_last_2_years: int
    account_types: List[CreditAccountType]
    current_utilization_percent: float
    total_credit_limits: float
    total_revolving_balances: float

class ScoreImprovementPrediction(BaseModel):
    """Score improvement prediction"""
    current_score: int
    predicted_score: int
    improvement_points: int
    timeline_months: int
    factors: Dict[str, float]
    confidence_level: str = "moderate"

class CreditRecommendation(BaseModel):
    """Individual credit improvement recommendation"""
    id: str
    priority: int  # 1=highest, 5=lowest
    category: str  # utilization, payment_history, credit_mix, etc.
    title: str
    action: str
    explanation: str
    expected_impact_points: int
    timeline_weeks: int
    difficulty: str  # easy, moderate, hard

class QuickWin(BaseModel):
    """Quick win recommendation (30-90 days)"""
    title: str
    action: str
    impact_description: str
    timeline_days: int

class CreditActionPlan(BaseModel):
    """Complete credit improvement action plan"""
    priority_actions: List[CreditRecommendation]
    quick_wins: List[QuickWin]
    timeline_summary: Dict[str, List[str]]  # month_1_3, month_4_6, etc.
    expected_impact: ScoreImprovementPrediction
    monitoring_strategy: Dict[str, str]
    red_flags_to_avoid: List[str]

class CreditProfileResponse(BaseModel):
    """Complete credit profile response"""
    id: str
    current_score: Optional[int]
    target_score: int
    last_checked: str
    
    # Current factors
    factors_assessment: CreditFactorsAssessment
    
    # AI-generated insights
    ai_analysis_summary: Optional[str] = None
    action_plan: Optional[CreditActionPlan] = None
    score_prediction: Optional[ScoreImprovementPrediction] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    recommendations_generated_at: Optional[datetime] = None

class CreditUtilizationBreakdown(BaseModel):
    """Detailed credit utilization breakdown"""
    total_balances: float
    total_limits: float
    utilization_percent: float
    target_utilization_percent: float = 30.0
    amount_to_pay_down: float
    per_card_utilization: List[Dict[str, Any]]

class DebtImpactOnCredit(BaseModel):
    """How current debts impact credit score"""
    high_utilization_debts: List[Dict[str, Any]]
    credit_building_opportunities: List[str]
    consolidation_recommendations: List[str]
    payment_optimization_tips: List[str]

class CreditScoreTipRequest(BaseModel):
    """Request for generating personalized credit score tips"""
    include_debt_analysis: bool = True
    focus_areas: Optional[List[str]] = None  # utilization, payment_history, etc.
    urgency: str = "normal"  # fast_track, normal, long_term

class CreditAnalysisResponse(BaseModel):
    """Comprehensive credit analysis response"""
    profile: CreditProfileResponse
    debt_impact: DebtImpactOnCredit
    utilization_breakdown: CreditUtilizationBreakdown
    personalized_tips: List[str]
    ai_generated_plan: str
    next_steps: List[str]