# app/models/credit_profile.py
from beanie import Document
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class PaymentHistoryStatus(str, Enum):
    ALWAYS_ON_TIME = "always_on_time"
    OCCASIONAL_LATE = "occasional_late"
    SEVERAL_LATE = "several_late"
    MISSED_RECENT = "missed_recent"

class CreditAccountType(str, Enum):
    CREDIT_CARD = "credit_card"
    AUTO_LOAN = "auto_loan"
    MORTGAGE = "mortgage"
    STUDENT_LOAN = "student_loan"
    PERSONAL_LOAN = "personal_loan"
    STORE_CARD = "store_card"

class CreditProfile(Document):
    """User's credit profile and scoring factors"""
    
    clerk_user_id: str = Field(..., index=True)
    
    # Credit Score Information
    current_score: Optional[int] = Field(None, ge=300, le=850)
    target_score: int = Field(750, ge=300, le=850)
    last_checked: str = Field(default="never_checked")  # Options: this_month, 1-3_months, 6+_months, never_checked
    
    # Credit Factors (matching Streamlit interface)
    payment_history: PaymentHistoryStatus = Field(default=PaymentHistoryStatus.ALWAYS_ON_TIME)
    average_account_age_years: float = Field(default=3.0, ge=0, le=50)
    new_accounts_last_2_years: int = Field(default=0, ge=0, le=20)
    account_types: List[CreditAccountType] = Field(default=[CreditAccountType.CREDIT_CARD])
    
    # Calculated fields (auto-updated from debt data)
    current_utilization_percent: float = Field(default=0.0, ge=0, le=100)
    total_credit_limits: float = Field(default=0.0, ge=0)
    total_revolving_balances: float = Field(default=0.0, ge=0)
    
    # AI-generated recommendations
    last_ai_analysis: Optional[Dict[str, Any]] = None
    recommendations_generated_at: Optional[datetime] = None
    
    # Score prediction
    predicted_score: Optional[int] = None
    predicted_timeline_months: Optional[int] = None
    improvement_factors: Optional[Dict[str, float]] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    class Settings:
        name = "credit_profiles"
        indexes = [
            "clerk_user_id",
            "created_at",
            "updated_at"
        ]
    
    def to_dict(self):
        """Convert to dictionary with proper ID handling"""
        data = self.model_dump()
        data['id'] = str(self.id)
        return data
    
    def calculate_utilization_from_debts(self, debts_with_limits):
        """Calculate credit utilization from debt data"""
        total_balances = 0
        total_limits = 0
        
        for debt in debts_with_limits:
            if hasattr(debt, 'limit') and debt.limit and debt.limit > 0:
                total_balances += debt.total_amount or 0
                total_limits += debt.limit
        
        if total_limits > 0:
            utilization = (total_balances / total_limits) * 100
            self.current_utilization_percent = min(100, max(0, utilization))
            self.total_credit_limits = total_limits
            self.total_revolving_balances = total_balances
        else:
            self.current_utilization_percent = 0
            self.total_credit_limits = 0
            self.total_revolving_balances = 0
    
    def predict_score_improvement(self) -> Dict[str, Any]:
        """Predict score improvement based on current factors"""
        improvement_factors = {}
        
        # Utilization improvement potential
        if self.current_utilization_percent > 30:
            improvement_factors["utilization_reduction"] = min(50, (self.current_utilization_percent - 25) * 2)
        elif self.current_utilization_percent > 10:
            improvement_factors["utilization_optimization"] = min(20, (self.current_utilization_percent - 5) * 1)
        
        # Payment history improvement
        if self.payment_history != PaymentHistoryStatus.ALWAYS_ON_TIME:
            improvement_factors["payment_history"] = 30 if self.payment_history == PaymentHistoryStatus.MISSED_RECENT else 15
        
        # Account age factor
        if self.average_account_age_years < 2:
            improvement_factors["account_age"] = min(25, (2 - self.average_account_age_years) * 10)
        
        # New accounts factor
        if self.new_accounts_last_2_years > 3:
            improvement_factors["reduce_new_inquiries"] = min(15, (self.new_accounts_last_2_years - 3) * 5)
        
        # Credit mix
        if len(self.account_types) < 2:
            improvement_factors["credit_mix"] = 10
        
        total_potential = sum(improvement_factors.values())
        
        # Conservative estimate - achieve 60-80% of potential
        realistic_improvement = int(total_potential * 0.7)
        
        current_base = self.current_score if self.current_score else 650
        predicted_score = min(850, current_base + realistic_improvement)
        
        # Timeline estimation
        timeline_months = 3 if realistic_improvement < 30 else (6 if realistic_improvement < 60 else 12)
        
        self.improvement_factors = improvement_factors
        self.predicted_score = predicted_score
        self.predicted_timeline_months = timeline_months
        
        return {
            "current_score": current_base,
            "predicted_score": predicted_score,
            "improvement_points": realistic_improvement,
            "timeline_months": timeline_months,
            "factors": improvement_factors
        }