"""
Core loan analysis and matching logic
"""
from typing import List, Dict, Any, Tuple
import math


class LoanAnalyzer:
    """Analyze user's financial situation and match with loans"""
    
    @staticmethod
    def calculate_monthly_payment(principal: float, annual_rate: float, term_months: int) -> float:
        """Calculate monthly payment using amortization formula"""
        if annual_rate == 0:
            return principal / term_months
        
        monthly_rate = annual_rate / 100 / 12
        payment = principal * (monthly_rate * math.pow(1 + monthly_rate, term_months)) / \
                  (math.pow(1 + monthly_rate, term_months) - 1)
        return round(payment, 2)
    
    @staticmethod
    def calculate_total_interest(principal: float, monthly_payment: float, term_months: int) -> float:
        """Calculate total interest paid over loan term"""
        total_paid = monthly_payment * term_months
        total_interest = total_paid - principal
        return round(total_interest, 2)
    
    @staticmethod
    def calculate_apr(interest_rate: float, origination_fee: float = 0, processing_fee: float = 0) -> float:
        """Calculate APR including fees"""
        # Simplified APR calculation
        apr = interest_rate + (origination_fee + processing_fee)
        return round(apr, 2)
    
    @staticmethod
    def analyze_affordability(
        requested_amount: float,
        monthly_income: float,
        monthly_expenses: float,
        total_existing_debt: float,
        existing_monthly_debt_payments: float,
        estimated_rate: float = 10.0,
        term_months: int = 36
    ) -> Dict[str, Any]:
        """Analyze if user can afford the requested loan"""
        
        # Calculate available budget
        available_budget = monthly_income - monthly_expenses
        
        # Calculate debt-to-income ratio (existing)
        current_dti = (existing_monthly_debt_payments / monthly_income * 100) if monthly_income > 0 else 0
        
        # Estimate monthly payment for requested loan
        estimated_monthly = LoanAnalyzer.calculate_monthly_payment(
            requested_amount, estimated_rate, term_months
        )
        
        # Calculate new DTI with this loan
        new_monthly_debt = existing_monthly_debt_payments + estimated_monthly
        new_dti = (new_monthly_debt / monthly_income * 100) if monthly_income > 0 else 0
        
        # Maximum affordable monthly payment (keep DTI under 43%)
        max_dti_threshold = 43.0
        max_affordable_debt_payment = (monthly_income * max_dti_threshold / 100)
        max_affordable_monthly = max(0, max_affordable_debt_payment - existing_monthly_debt_payments)
        
        # Calculate max affordable loan amount
        if estimated_rate > 0:
            monthly_rate = estimated_rate / 100 / 12
            max_affordable_loan = max_affordable_monthly * \
                (math.pow(1 + monthly_rate, term_months) - 1) / \
                (monthly_rate * math.pow(1 + monthly_rate, term_months))
        else:
            max_affordable_loan = max_affordable_monthly * term_months
        max_affordable_loan = round(max_affordable_loan, 2)
        
        # Affordability check
        is_affordable = estimated_monthly <= max_affordable_monthly and new_dti <= max_dti_threshold
        
        # Affordability score (0-100)
        if new_dti >= 50:
            affordability_score = 0
        elif new_dti >= max_dti_threshold:
            affordability_score = 20
        elif new_dti >= 36:
            affordability_score = 50
        elif new_dti >= 28:
            affordability_score = 75
        else:
            affordability_score = 100
        
        # Risk assessment
        if new_dti >= 50:
            risk_level = "high"
        elif new_dti >= max_dti_threshold:
            risk_level = "high"
        elif new_dti >= 36:
            risk_level = "moderate"
        else:
            risk_level = "low"
        
        # Recommendations
        recommendations = []
        if not is_affordable:
            recommendations.append(f"Requested amount may strain your budget. Consider ₹{max_affordable_loan:.0f} or less.")
        if new_dti > 43:
            recommendations.append("Your debt-to-income ratio would exceed 43%, which may affect approval.")
        if new_dti > 28:
            recommendations.append("Consider paying down existing debt before taking new loan.")
        if available_budget < estimated_monthly * 1.2:
            recommendations.append("Leave buffer room in your budget for unexpected expenses.")
        if current_dti < 20 and is_affordable:
            recommendations.append("Your financial profile is strong for this loan amount.")
        
        return {
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "available_budget": available_budget,
            "total_existing_debt": total_existing_debt,
            "existing_monthly_debt_payments": existing_monthly_debt_payments,
            "debt_to_income_ratio": round(current_dti, 2),
            "debt_to_income_with_loan": round(new_dti, 2),
            "max_affordable_monthly": round(max_affordable_monthly, 2),
            "max_affordable_loan_amount": max_affordable_loan,
            "is_affordable": is_affordable,
            "affordability_score": affordability_score,
            "risk_level": risk_level,
            "recommendations": recommendations
        }
    
    @staticmethod
    def calculate_suitability_score(
        loan_data: Dict[str, Any],
        user_profile: Dict[str, Any],
        requested_amount: float,
        preferred_term: int = None
    ) -> float:
        """Calculate how well a loan matches user's profile (0-100)"""
        score = 100.0
        
        # Check loan amount range
        if requested_amount < loan_data.get("min_amount", 0):
            score -= 30
        elif requested_amount > loan_data.get("max_amount", float('inf')):
            score -= 30
        
        # Check income requirement
        min_income = loan_data.get("min_income")
        if min_income and user_profile.get("monthly_income", 0) < min_income:
            score -= 25
        
        # Check DTI requirement
        max_dti = loan_data.get("max_dti_ratio")
        user_dti = user_profile.get("debt_to_income_with_loan", 0)
        if max_dti and user_dti > max_dti:
            score -= 25
        
        # Term preference match
        if preferred_term:
            loan_term_min = loan_data.get("term_months_min", 0)
            loan_term_max = loan_data.get("term_months_max", 360)
            if not (loan_term_min <= preferred_term <= loan_term_max):
                score -= 10
        
        # Interest rate (lower is better)
        interest_rate = loan_data.get("interest_rate_min", 0)
        if interest_rate > 20:
            score -= 15
        elif interest_rate > 15:
            score -= 10
        elif interest_rate > 10:
            score -= 5
        
        return max(0, min(100, score))
    
    @staticmethod
    def calculate_approval_probability(
        loan_data: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> float:
        """Estimate approval probability (0-100)"""
        probability = 100.0
        
        # DTI check
        max_dti = loan_data.get("max_dti_ratio", 43)
        user_dti = user_profile.get("debt_to_income_with_loan", 0)
        if user_dti > max_dti:
            probability -= 40
        elif user_dti > max_dti * 0.9:
            probability -= 20
        elif user_dti > max_dti * 0.8:
            probability -= 10
        
        # Income check
        min_income = loan_data.get("min_income")
        if min_income:
            user_income = user_profile.get("monthly_income", 0)
            if user_income < min_income:
                probability -= 30
            elif user_income < min_income * 1.2:
                probability -= 15
        
        # Affordability
        if not user_profile.get("is_affordable", True):
            probability -= 25
        
        return max(0, min(100, probability))