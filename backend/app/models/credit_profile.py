# app/models/credit_profile.py - FIXED CIRCULAR IMPORT
from beanie import Document
from pydantic import BaseModel, Field
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

class CreditCardDetails(BaseModel):
    """Individual credit card details"""
    name: str = Field(..., description="Credit card name/bank")
    credit_limit: float = Field(..., ge=0, description="Total credit limit")
    current_balance: float = Field(default=0, ge=0, description="Current outstanding balance")
    minimum_payment: Optional[float] = Field(None, ge=0, description="Monthly minimum payment")
    interest_rate: Optional[float] = Field(None, ge=0, le=50, description="Annual interest rate %")
    statement_date: Optional[int] = Field(None, ge=1, le=31, description="Statement closing date")
    due_date: Optional[int] = Field(None, ge=1, le=31, description="Payment due date")
    is_active: bool = Field(default=True)
    
    @property
    def utilization_percent(self) -> float:
        """Calculate utilization percentage for this card"""
        if self.credit_limit <= 0:
            return 0.0
        return min(100.0, (self.current_balance / self.credit_limit) * 100)
    
    @property
    def available_credit(self) -> float:
        """Calculate available credit"""
        return max(0, self.credit_limit - self.current_balance)

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
    
    # NEW: Credit Card Details
    credit_cards: List[CreditCardDetails] = Field(default=[], description="List of user's credit cards")
    
    # Calculated fields (auto-updated from credit card data)
    current_utilization_percent: float = Field(default=0.0, ge=0, le=100)
    total_credit_limits: float = Field(default=0.0, ge=0)
    total_revolving_balances: float = Field(default=0.0, ge=0)
    
    # Per-card utilization breakdown
    per_card_utilization: List[Dict[str, Any]] = Field(default=[])
    
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
    
    def add_credit_card(self, card_details: CreditCardDetails):
        """Add a new credit card"""
        # Check if card already exists (by name)
        existing_card = next((card for card in self.credit_cards if card.name.lower() == card_details.name.lower()), None)
        
        if existing_card:
            # Update existing card
            existing_card.credit_limit = card_details.credit_limit
            existing_card.current_balance = card_details.current_balance
            existing_card.minimum_payment = card_details.minimum_payment
            existing_card.interest_rate = card_details.interest_rate
            existing_card.statement_date = card_details.statement_date
            existing_card.due_date = card_details.due_date
            existing_card.is_active = card_details.is_active
        else:
            # Add new card
            self.credit_cards.append(card_details)
        
        self.recalculate_utilization()
    
    def remove_credit_card(self, card_name: str):
        """Remove or deactivate a credit card"""
        self.credit_cards = [card for card in self.credit_cards if card.name.lower() != card_name.lower()]
        self.recalculate_utilization()
    
    def update_card_balance(self, card_name: str, new_balance: float):
        """Update the balance of a specific credit card"""
        card = next((card for card in self.credit_cards if card.name.lower() == card_name.lower()), None)
        if card:
            card.current_balance = max(0, new_balance)
            self.recalculate_utilization()
    
    def recalculate_utilization(self):
        """Recalculate utilization from credit card data"""
        active_cards = [card for card in self.credit_cards if card.is_active]
        
        if not active_cards:
            self.current_utilization_percent = 0.0
            self.total_credit_limits = 0.0
            self.total_revolving_balances = 0.0
            self.per_card_utilization = []
            return
        
        total_balances = sum(card.current_balance for card in active_cards)
        total_limits = sum(card.credit_limit for card in active_cards)
        
        if total_limits > 0:
            self.current_utilization_percent = (total_balances / total_limits) * 100
        else:
            self.current_utilization_percent = 0.0
        
        self.total_credit_limits = total_limits
        self.total_revolving_balances = total_balances
        
        # Update per-card utilization breakdown
        self.per_card_utilization = [
            {
                "name": card.name,
                "balance": card.current_balance,
                "limit": card.credit_limit,
                "utilization": card.utilization_percent,
                "available_credit": card.available_credit,
                "interest_rate": card.interest_rate
            }
            for card in active_cards
        ]
        
        self.updated_at = datetime.utcnow()
    
    def get_highest_utilization_cards(self, threshold: float = 30.0) -> List[Dict[str, Any]]:
        """Get cards with utilization above threshold"""
        return [
            card_data for card_data in self.per_card_utilization 
            if card_data["utilization"] > threshold
        ]
    
    def calculate_paydown_targets(self, target_utilization: float = 30.0) -> Dict[str, float]:
        """Calculate how much to pay down each card to reach target utilization"""
        paydown_targets = {}
        
        for card in self.credit_cards:
            if not card.is_active or card.credit_limit <= 0:
                continue
                
            target_balance = card.credit_limit * (target_utilization / 100)
            if card.current_balance > target_balance:
                paydown_targets[card.name] = card.current_balance - target_balance
        
        return paydown_targets
    
    def to_dict(self):
        """Convert to dictionary with proper ID handling"""
        data = self.model_dump()
        data['id'] = str(self.id)
        return data
    
    def predict_score_improvement(self) -> Dict[str, Any]:
        """Predict score improvement based on current factors"""
        improvement_factors = {}
        
        # Utilization improvement potential (enhanced with actual data)
        if self.current_utilization_percent > 30:
            improvement_factors["utilization_reduction"] = min(60, (self.current_utilization_percent - 25) * 2)
        elif self.current_utilization_percent > 10:
            improvement_factors["utilization_optimization"] = min(25, (self.current_utilization_percent - 5) * 1.5)
        
        # Individual card utilization penalties
        high_util_cards = len([card for card in self.per_card_utilization if card["utilization"] > 90])
        if high_util_cards > 0:
            improvement_factors["reduce_maxed_cards"] = high_util_cards * 15
        
        # Payment history improvement
        if self.payment_history != PaymentHistoryStatus.ALWAYS_ON_TIME:
            improvement_factors["payment_history"] = 40 if self.payment_history == PaymentHistoryStatus.MISSED_RECENT else 20
        
        # Account age factor
        if self.average_account_age_years < 2:
            improvement_factors["account_age"] = min(30, (2 - self.average_account_age_years) * 12)
        
        # New accounts factor
        if self.new_accounts_last_2_years > 3:
            improvement_factors["reduce_new_inquiries"] = min(20, (self.new_accounts_last_2_years - 3) * 6)
        
        # Credit mix
        if len(self.account_types) < 2:
            improvement_factors["credit_mix"] = 15
        elif len(self.credit_cards) == 0:
            improvement_factors["establish_credit_cards"] = 25
        
        total_potential = sum(improvement_factors.values())
        
        # Conservative estimate - achieve 65-80% of potential
        realistic_improvement = int(total_potential * 0.72)
        
        current_base = self.current_score if self.current_score else 650
        predicted_score = min(850, current_base + realistic_improvement)
        
        # Timeline estimation (more sophisticated)
        if realistic_improvement < 25:
            timeline_months = 3
        elif realistic_improvement < 50:
            timeline_months = 6
        elif realistic_improvement < 80:
            timeline_months = 9
        else:
            timeline_months = 12
        
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