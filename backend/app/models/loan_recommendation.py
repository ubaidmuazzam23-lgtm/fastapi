from beanie import Document
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class LoanRecommendation(Document):
    """Store loan recommendation requests and results"""
    clerk_user_id: str = Field(..., index=True)
    
    # User's loan request
    loan_type: str = Field(..., description="personal, business, home, auto, education")
    requested_amount: float = Field(..., ge=0)
    purpose: Optional[str] = None
    preferred_term_months: Optional[int] = Field(None, ge=6, le=360)
    
    # Financial snapshot at time of request
    user_monthly_income: float = Field(default=0.0, ge=0)
    user_monthly_expenses: float = Field(default=0.0, ge=0)
    total_existing_debt: float = Field(default=0.0, ge=0)
    debt_to_income_ratio: float = Field(default=0.0, ge=0)
    
    # Recommended loans (stored as JSON)
    recommended_loans: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Analysis data
    affordability_score: Optional[float] = Field(None, ge=0, le=100)
    approval_probability: Optional[float] = Field(None, ge=0, le=100)
    max_affordable_monthly: Optional[float] = Field(None, ge=0)
    analysis_notes: Optional[str] = None
    
    # Status
    status: str = Field(default="pending", description="pending, completed, failed")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    class Settings:
        name = "loan_recommendations"
        indexes = [
            "clerk_user_id",
            "created_at",
            "loan_type",
            "status"
        ]
    
    def to_dict(self):
        """Convert to dictionary with proper ID handling"""
        data = self.model_dump()
        data['id'] = str(self.id)
        return data


class LoanData(Document):
    """Cache scraped loan data from various lenders"""
    lender_name: str = Field(..., index=True)
    loan_type: str = Field(..., index=True)
    
    # Loan details
    min_amount: float = Field(..., ge=0)
    max_amount: float = Field(..., ge=0)
    interest_rate_min: float = Field(..., ge=0, le=100)
    interest_rate_max: float = Field(..., ge=0, le=100)
    apr_min: Optional[float] = Field(None, ge=0, le=100)
    apr_max: Optional[float] = Field(None, ge=0, le=100)
    
    # Terms
    term_months_min: int = Field(..., ge=6)
    term_months_max: int = Field(..., le=360)
    
    # Fees
    origination_fee: Optional[float] = Field(None, ge=0)
    processing_fee: Optional[float] = Field(None, ge=0)
    prepayment_penalty: bool = Field(default=False)
    
    # Requirements
    min_credit_score: Optional[int] = Field(None, ge=300, le=850)
    min_income: Optional[float] = Field(None, ge=0)
    max_dti_ratio: Optional[float] = Field(None, ge=0, le=100)
    
    # Additional info
    features: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    
    # Scraping metadata
    source_url: Optional[str] = None
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    class Settings:
        name = "loan_data"
        indexes = [
            "lender_name",
            "loan_type",
            "scraped_at",
            "is_active"
        ]
    
    def to_dict(self):
        data = self.model_dump()
        data['id'] = str(self.id)
        return data