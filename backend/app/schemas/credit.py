# app/schemas/credit.py - FIXED FOR PYDANTIC V2
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from app.models.credit_profile import PaymentHistoryStatus, CreditAccountType

# ==== CREDIT CARD SCHEMAS ====

class CreditCardDetailsCreate(BaseModel):
    """Schema for creating/updating credit card details"""
    name: str = Field(..., description="Credit card name/bank", min_length=2, max_length=100)
    credit_limit: float = Field(..., ge=0, description="Total credit limit in rupees")
    current_balance: float = Field(default=0, ge=0, description="Current outstanding balance")
    minimum_payment: Optional[float] = Field(None, ge=0, description="Monthly minimum payment")
    interest_rate: Optional[float] = Field(None, ge=0, le=50, description="Annual interest rate %")
    statement_date: Optional[int] = Field(None, ge=1, le=31, description="Statement closing date (1-31)")
    due_date: Optional[int] = Field(None, ge=1, le=31, description="Payment due date (1-31)")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Card name cannot be empty')
        return v.strip()
    
    @field_validator('credit_limit')
    @classmethod
    def validate_credit_limit(cls, v):
        if v <= 0:
            raise ValueError('Credit limit must be greater than 0')
        if v > 10000000:  # 1 crore limit seems reasonable max
            raise ValueError('Credit limit seems unreasonably high')
        return v
    
    @field_validator('current_balance')
    @classmethod
    def validate_balance(cls, v, info):
        if 'credit_limit' in info.data and v > info.data['credit_limit'] * 1.1:  # Allow 10% over-limit
            raise ValueError('Current balance cannot exceed credit limit by more than 10%')
        return v

class CreditCardDetailsResponse(BaseModel):
    """Schema for credit card details in responses"""
    name: str
    credit_limit: float = Field(alias="limit")  # Handle both field names
    current_balance: float = Field(alias="balance")  # Handle both field names  
    utilization_percent: float = Field(default=0.0, alias="utilization")
    available_credit: float = Field(default=0.0)
    minimum_payment: Optional[float] = None
    interest_rate: Optional[float] = None
    statement_date: Optional[int] = None
    due_date: Optional[int] = None
    is_active: bool = Field(default=True)
    monthly_interest_cost: Optional[float] = None
    
    class Config:
        populate_by_name = True  # Allow both original and alias names
        
    @field_validator('utilization_percent', mode='before')
    @classmethod
    def calculate_utilization(cls, v, info):
        if v is None or v == 0:
            data = info.data if hasattr(info, 'data') else {}
            balance = data.get('current_balance') or data.get('balance', 0)
            limit = data.get('credit_limit') or data.get('limit', 0)
            if limit > 0:
                return (balance / limit) * 100
            return 0.0
        return v
        
    @field_validator('available_credit', mode='before')
    @classmethod  
    def calculate_available_credit(cls, v, info):
        if v is None or v == 0:
            data = info.data if hasattr(info, 'data') else {}
            balance = data.get('current_balance') or data.get('balance', 0)
            limit = data.get('credit_limit') or data.get('limit', 0)
            return max(0, limit - balance)
        return v

class CreditCardBalanceUpdate(BaseModel):
    """Update credit card balance"""
    card_name: str = Field(..., min_length=1)
    new_balance: float = Field(ge=0)
    
    @field_validator('card_name')
    @classmethod
    def validate_card_name(cls, v):
        return v.strip()

class CreditCardBulkUpdate(BaseModel):
    """Bulk update multiple card balances"""
    updates: List[CreditCardBalanceUpdate] = Field(..., min_length=1, max_length=20)

# ==== CORE PROFILE SCHEMAS ====

class CreditProfileCreate(BaseModel):
    """Create credit profile request - ENHANCED"""
    current_score: Optional[int] = Field(None, ge=300, le=850, description="Current credit score")
    target_score: int = Field(750, ge=300, le=850, description="Target credit score goal")
    last_checked: str = Field(
        default="never_checked", 
        description="When credit was last checked"
    )
    payment_history: PaymentHistoryStatus = Field(
        default=PaymentHistoryStatus.ALWAYS_ON_TIME,
        description="Payment history status"
    )
    average_account_age_years: float = Field(
        default=3.0, 
        ge=0, 
        le=50, 
        description="Average age of credit accounts in years"
    )
    new_accounts_last_2_years: int = Field(
        default=0, 
        ge=0, 
        le=20, 
        description="Number of new accounts opened in last 2 years"
    )
    account_types: List[CreditAccountType] = Field(
        default=[CreditAccountType.CREDIT_CARD],
        description="Types of credit accounts held"
    )
    
    # NEW: Credit card details
    credit_cards: List[CreditCardDetailsCreate] = Field(
        default=[], 
        description="List of credit cards with limits and balances",
        max_length=20
    )
    
    @field_validator('last_checked')
    @classmethod
    def validate_last_checked(cls, v):
        valid_options = ["this_month", "1-3_months", "6+_months", "never_checked"]
        if v not in valid_options:
            raise ValueError(f'last_checked must be one of: {valid_options}')
        return v

class CreditProfileUpdate(BaseModel):
    """Update credit profile request - ENHANCED"""
    current_score: Optional[int] = Field(None, ge=300, le=850)
    target_score: Optional[int] = Field(None, ge=300, le=850)
    last_checked: Optional[str] = None
    payment_history: Optional[PaymentHistoryStatus] = None
    average_account_age_years: Optional[float] = Field(None, ge=0, le=50)
    new_accounts_last_2_years: Optional[int] = Field(None, ge=0, le=20)
    account_types: Optional[List[CreditAccountType]] = None
    
    # NEW: Credit card details
    credit_cards: Optional[List[CreditCardDetailsCreate]] = Field(
        None, 
        description="List of credit cards - replaces existing cards",
        max_length=20
    )
    
    @field_validator('last_checked')
    @classmethod
    def validate_last_checked(cls, v):
        if v is not None:
            valid_options = ["this_month", "1-3_months", "6+_months", "never_checked"]
            if v not in valid_options:
                raise ValueError(f'last_checked must be one of: {valid_options}')
        return v

class CreditFactorsAssessment(BaseModel):
    """Current credit factors for assessment - ENHANCED"""
    payment_history: PaymentHistoryStatus
    average_account_age_years: float
    new_accounts_last_2_years: int
    account_types: List[CreditAccountType]
    current_utilization_percent: float = Field(ge=0, le=100)
    total_credit_limits: float = Field(ge=0)
    total_revolving_balances: float = Field(ge=0)
    
    # NEW: Enhanced metrics
    number_of_credit_cards: int = Field(default=0, ge=0)
    available_credit: float = Field(default=0, ge=0)
    highest_individual_utilization: float = Field(default=0, ge=0, le=100)
    cards_above_30_percent: int = Field(default=0, ge=0)
    cards_above_90_percent: int = Field(default=0, ge=0)

# ==== ANALYSIS & PREDICTION SCHEMAS ====

class ScoreImprovementPrediction(BaseModel):
    """Enhanced score improvement prediction"""
    current_score: int = Field(ge=300, le=850)
    predicted_score: int = Field(ge=300, le=850)
    improvement_points: int = Field(ge=0)
    timeline_months: int = Field(ge=1, le=24)
    factors: Dict[str, float]
    confidence_level: str = Field(default="moderate")
    
    # NEW: Detailed breakdown
    utilization_impact: Optional[int] = Field(None, description="Points from utilization improvement")
    payment_history_impact: Optional[int] = Field(None, description="Points from payment history")
    account_age_impact: Optional[int] = Field(None, description="Points from account age")
    credit_mix_impact: Optional[int] = Field(None, description="Points from credit mix")
    
    @field_validator('confidence_level')
    @classmethod
    def validate_confidence_level(cls, v):
        valid_levels = ["low", "moderate", "high"]
        if v not in valid_levels:
            raise ValueError(f'confidence_level must be one of: {valid_levels}')
        return v
    
    @field_validator('predicted_score')
    @classmethod
    def predicted_score_reasonable(cls, v, info):
        if 'current_score' in info.data and 'improvement_points' in info.data:
            expected = info.data['current_score'] + info.data['improvement_points']
            if abs(v - expected) > 10:  # Allow some variance
                raise ValueError('Predicted score should roughly equal current + improvement')
        return v

class CreditRecommendation(BaseModel):
    """Individual credit improvement recommendation - ENHANCED"""
    id: str
    priority: int = Field(ge=1, le=5, description="1=highest priority, 5=lowest")
    category: str = Field(..., description="utilization, payment_history, credit_mix, etc.")
    title: str = Field(..., min_length=5, max_length=100)
    action: str = Field(..., min_length=10, max_length=300)
    explanation: str = Field(..., min_length=20, max_length=500)
    expected_impact_points: int = Field(ge=0, le=100)
    timeline_weeks: int = Field(ge=1, le=104)
    difficulty: str = Field(...)
    
    # NEW: Enhanced fields
    cost_estimate: Optional[float] = Field(None, ge=0, description="Estimated cost in rupees")
    success_rate: Optional[float] = Field(None, ge=0, le=100, description="Expected success rate %")
    prerequisites: List[str] = Field(default=[], description="What needs to be done first")
    
    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v):
        valid_levels = ["easy", "moderate", "hard"]
        if v not in valid_levels:
            raise ValueError(f'difficulty must be one of: {valid_levels}')
        return v

class QuickWin(BaseModel):
    """Quick win recommendation (enhanced)"""
    title: str = Field(..., min_length=5, max_length=100)
    action: str = Field(..., min_length=10, max_length=300)
    impact_description: str = Field(..., min_length=10, max_length=200)
    timeline_days: int = Field(ge=1, le=90)
    
    # NEW: Enhanced fields
    effort_level: str = Field(default="low")
    cost_estimate: Optional[float] = Field(None, ge=0)
    specific_amount: Optional[float] = Field(None, ge=0, description="Specific rupee amount if applicable")
    
    @field_validator('effort_level')
    @classmethod
    def validate_effort_level(cls, v):
        valid_levels = ["low", "medium", "high"]
        if v not in valid_levels:
            raise ValueError(f'effort_level must be one of: {valid_levels}')
        return v

class CreditActionPlan(BaseModel):
    """Complete credit improvement action plan - ENHANCED"""
    priority_actions: List[CreditRecommendation]
    quick_wins: List[QuickWin]
    timeline_summary: Dict[str, List[str]]
    expected_impact: ScoreImprovementPrediction
    monitoring_strategy: Dict[str, str]
    red_flags_to_avoid: List[str]
    
    # NEW: Enhanced planning
    monthly_budget_needed: Optional[float] = Field(None, ge=0, description="Estimated monthly budget for plan")
    success_milestones: Dict[str, str] = Field(default_factory=dict, description="Key milestones to track")
    risk_factors: List[str] = Field(default=[], description="Potential risks to plan success")

# ==== UTILIZATION & DEBT ANALYSIS ====

class CreditUtilizationBreakdown(BaseModel):
    """Enhanced detailed credit utilization breakdown"""
    total_balances: float = Field(ge=0)
    total_limits: float = Field(ge=0)
    utilization_percent: float = Field(ge=0, le=100)
    target_utilization_percent: float = Field(default=30.0, ge=0, le=100)
    amount_to_pay_down: float = Field(ge=0)
    per_card_utilization: List[Dict[str, Any]]
    
    # NEW: Enhanced breakdown
    cards_above_30_percent: List[Dict[str, Any]]
    cards_above_90_percent: List[Dict[str, Any]]
    paydown_recommendations: Dict[str, float]
    monthly_savings_potential: float = Field(ge=0, description="Monthly interest savings from paydown")
    
    # NEW: Additional insights
    available_credit_total: float = Field(default=0, ge=0)
    lowest_utilization_card: Optional[str] = None
    highest_utilization_card: Optional[str] = None
    optimal_balance_distribution: Optional[Dict[str, float]] = None

class DebtImpactOnCredit(BaseModel):
    """How current debts impact credit score - ENHANCED"""
    high_utilization_debts: List[Dict[str, Any]]
    credit_building_opportunities: List[str]
    consolidation_recommendations: List[str]
    payment_optimization_tips: List[str]
    
    # NEW: Enhanced analysis
    total_monthly_minimums: float = Field(default=0, ge=0)
    total_monthly_interest: float = Field(default=0, ge=0)
    debt_to_credit_ratio: float = Field(default=0, ge=0, le=100)
    consolidation_savings_potential: Optional[float] = Field(None, ge=0)

class CreditScoreTipRequest(BaseModel):
    """Request for generating personalized credit score tips - ENHANCED"""
    include_debt_analysis: bool = Field(default=True)
    focus_areas: Optional[List[str]] = Field(
        None, 
        description="Specific areas to focus on: utilization, payment_history, credit_mix, etc."
    )
    urgency: str = Field(
        default="normal", 
        description="Timeline preference for improvements"
    )
    
    # NEW: Enhanced request options
    budget_available: Optional[float] = Field(None, ge=0, description="Monthly budget for credit improvement")
    risk_tolerance: str = Field(default="moderate")
    primary_goal: Optional[str] = Field(None, description="Primary goal: buy_home, get_loan, general_improvement")
    
    @field_validator('urgency')
    @classmethod
    def validate_urgency(cls, v):
        valid_options = ["fast_track", "normal", "long_term"]
        if v not in valid_options:
            raise ValueError(f'urgency must be one of: {valid_options}')
        return v
    
    @field_validator('risk_tolerance')
    @classmethod
    def validate_risk_tolerance(cls, v):
        valid_options = ["conservative", "moderate", "aggressive"]
        if v not in valid_options:
            raise ValueError(f'risk_tolerance must be one of: {valid_options}')
        return v

# ==== RESPONSE SCHEMAS ====

class CreditProfileResponse(BaseModel):
    """Complete credit profile response - ENHANCED"""
    id: str
    current_score: Optional[int]
    target_score: int
    last_checked: str
    
    # Current factors (enhanced)
    factors_assessment: CreditFactorsAssessment
    
    # NEW: Credit card summary
    credit_cards: List[CreditCardDetailsResponse] = Field(default=[])
    credit_card_summary: Optional[Dict[str, Any]] = None
    
    # AI-generated insights
    ai_analysis_summary: Optional[str] = None
    action_plan: Optional[CreditActionPlan] = None
    score_prediction: Optional[ScoreImprovementPrediction] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    recommendations_generated_at: Optional[datetime] = None
    
    # NEW: Enhanced metadata
    last_sync_with_debts: Optional[datetime] = None
    data_completeness_score: Optional[float] = Field(None, ge=0, le=100, description="How complete the profile data is")

class CreditAnalysisResponse(BaseModel):
    """Comprehensive credit analysis response - ENHANCED"""
    profile: CreditProfileResponse
    debt_impact: DebtImpactOnCredit
    utilization_breakdown: CreditUtilizationBreakdown
    personalized_tips: List[str]
    ai_generated_plan: str
    next_steps: List[str]
    
    # NEW: Enhanced analysis
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: float = Field(default=0.75, ge=0, le=1.0, description="Confidence in analysis accuracy")
    data_quality_notes: List[str] = Field(default=[], description="Notes about data quality issues")
    follow_up_recommended: bool = Field(default=False, description="Whether follow-up analysis is recommended")

# ==== UTILITY SCHEMAS ====

class CreditCardSyncResult(BaseModel):
    """Result of syncing credit cards with debt data"""
    matched_cards: List[Dict[str, Any]]
    new_cards_from_debts: List[Dict[str, Any]]
    unmatched_debts: List[str]
    orphaned_cards: List[str]
    updated_balances: List[str]
    final_utilization: float
    total_cards: int
    sync_timestamp: datetime = Field(default_factory=datetime.utcnow)

class CreditHealthScore(BaseModel):
    """Overall credit health assessment"""
    overall_score: float = Field(ge=0, le=100, description="Overall credit health score")
    utilization_score: float = Field(ge=0, le=100)
    payment_history_score: float = Field(ge=0, le=100)
    credit_mix_score: float = Field(ge=0, le=100)
    account_age_score: float = Field(ge=0, le=100)
    new_credit_score: float = Field(ge=0, le=100)
    
    grade: str = Field(..., description="Letter grade A+ to F")
    key_strengths: List[str]
    improvement_areas: List[str]
    next_milestone: Optional[str] = None
    
    @field_validator('grade')
    @classmethod
    def validate_grade(cls, v):
        import re
        if not re.match(r'^[A-F][+-]?$', v):
            raise ValueError('Grade must be in format A+, A, A-, B+, etc.')
        return v

class CreditGoalTracking(BaseModel):
    """Track progress toward credit goals"""
    goal_type: str = Field(..., description="home_loan, personal_loan, credit_card_approval, etc.")
    target_score: int = Field(ge=300, le=850)
    current_score: int = Field(ge=300, le=850)
    progress_percent: float = Field(ge=0, le=100)
    estimated_timeline_months: int = Field(ge=0)
    milestones_achieved: List[str]
    next_milestone: Optional[str] = None
    on_track: bool
    adjustments_needed: List[str] = Field(default=[])

# ==== ERROR HANDLING ====

class CreditErrorResponse(BaseModel):
    """Standardized error response"""
    error: str
    error_code: str
    details: Optional[Dict[str, Any]] = None
    suggestions: List[str] = Field(default=[])
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# ==== VALIDATION HELPERS ====

class CreditDataValidation(BaseModel):
    """Validation results for credit data"""
    is_valid: bool
    warnings: List[str] = Field(default=[])
    errors: List[str] = Field(default=[])
    completeness_score: float = Field(ge=0, le=100)
    missing_fields: List[str] = Field(default=[])
    data_quality_issues: List[str] = Field(default=[])
    
    @field_validator('completeness_score')
    @classmethod
    def validate_completeness(cls, v, info):
        if 'is_valid' in info.data and info.data['is_valid'] and v < 50:
            raise ValueError('Valid data should have completeness score >= 50%')
        return v