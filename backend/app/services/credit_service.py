# app/services/credit_service.py (Complete Updated Version)
from typing import Optional, List, Dict, Any
from datetime import datetime
from beanie import PydanticObjectId

from app.models.credit_profile import CreditProfile, PaymentHistoryStatus, CreditAccountType
from app.models.debt import Debt
from app.models.user import User
from app.schemas.credit import (
    CreditProfileCreate, CreditProfileUpdate, CreditProfileResponse,
    CreditFactorsAssessment, ScoreImprovementPrediction, CreditActionPlan,
    CreditRecommendation, QuickWin, CreditUtilizationBreakdown,
    DebtImpactOnCredit, CreditAnalysisResponse, CreditScoreTipRequest
)
from app.services.llm_service import LLMService

class CreditService:
    
    @staticmethod
    async def get_or_create_profile(clerk_user_id: str) -> CreditProfile:
        """Get existing credit profile or create new one with defaults"""
        profile = await CreditProfile.find_one(CreditProfile.clerk_user_id == clerk_user_id)
        
        if not profile:
            profile = CreditProfile(
                clerk_user_id=clerk_user_id,
                current_score=370,  # Start with user's actual score from UI
                target_score=750,
                payment_history=PaymentHistoryStatus.ALWAYS_ON_TIME,
                average_account_age_years=3.0,
                new_accounts_last_2_years=1,
                account_types=[CreditAccountType.CREDIT_CARD]
            )
            await profile.insert()
        
        return profile
    
    @staticmethod
    async def update_profile(clerk_user_id: str, update_data: CreditProfileUpdate) -> Optional[CreditProfile]:
        """Update credit profile"""
        profile = await CreditService.get_or_create_profile(clerk_user_id)
        
        update_dict = update_data.model_dump(exclude_unset=True)
        update_dict["updated_at"] = datetime.utcnow()
        
        await profile.update({"$set": update_dict})
        return await CreditProfile.find_one(CreditProfile.clerk_user_id == clerk_user_id)
    
    @staticmethod
    async def refresh_utilization_from_debts(clerk_user_id: str) -> CreditProfile:
        """Update credit utilization based on current debt data - IMPROVED VERSION"""
        profile = await CreditService.get_or_create_profile(clerk_user_id)
        
        # Fetch user's debts
        debts = await Debt.find(
            Debt.clerk_user_id == clerk_user_id,
            Debt.is_active == True
        ).to_list()
        
        print(f"DEBUG: Found {len(debts)} debts for user {clerk_user_id}")
        
        total_balances = 0
        total_limits = 0
        credit_cards_found = 0
        
        for debt in debts:
            debt_name_lower = debt.name.lower()
            print(f"DEBUG: Processing debt: '{debt.name}' (₹{debt.total_amount:,.0f}, {debt.interest_rate}% APR)")
            
            # Expanded credit card detection logic
            is_credit_card = False
            
            # Method 1: Check for credit card keywords
            credit_card_terms = [
                'credit', 'card', 'mastercard', 'visa', 'amex', 'american express',
                'discover', 'store', 'retail', 'chase', 'citi', 'capital one',
                'hdfc', 'sbi', 'icici', 'axis', 'kotak', 'yes bank', 'rbl',
                'standard chartered', 'hsbc', 'indusind', 'bob', 'pnb',
                'cc', 'credit line', 'revolving'
            ]
            
            if any(term in debt_name_lower for term in credit_card_terms):
                is_credit_card = True
                print(f"DEBUG: '{debt.name}' identified as credit card by keyword match")
            
            # Method 2: High interest rate typically indicates credit card
            elif debt.interest_rate >= 15:
                is_credit_card = True
                print(f"DEBUG: '{debt.name}' identified as credit card by high APR ({debt.interest_rate}%)")
            
            # Method 3: If no other debts detected and this looks revolving
            elif len(debts) <= 2 and debt.interest_rate >= 10:
                is_credit_card = True
                print(f"DEBUG: '{debt.name}' identified as credit card (fallback logic)")
            
            if is_credit_card:
                credit_cards_found += 1
                
                # Smart credit limit estimation
                if debt.total_amount == 0:
                    # If zero balance, assume a reasonable credit limit
                    estimated_limit = 50000  # ₹50,000 default limit
                elif debt.total_amount < 5000:
                    # Low balance - assume higher available credit
                    estimated_limit = debt.total_amount * 10  # Very low utilization
                else:
                    # Normal case - assume current balance is 30-60% of limit
                    estimated_limit = debt.total_amount * 2.0  # Assume 50% utilization
                
                total_balances += debt.total_amount
                total_limits += estimated_limit
                
                utilization_for_this_card = (debt.total_amount / estimated_limit) * 100
                print(f"DEBUG: Card '{debt.name}': Balance=₹{debt.total_amount:,.0f}, "
                     f"Est Limit=₹{estimated_limit:,.0f}, Utilization={utilization_for_this_card:.1f}%")
            else:
                print(f"DEBUG: '{debt.name}' NOT identified as credit card")
        
        print(f"DEBUG: Total credit cards found: {credit_cards_found}")
        print(f"DEBUG: Total balances: ₹{total_balances:,.0f}")
        print(f"DEBUG: Total limits: ₹{total_limits:,.0f}")
        
        # Calculate overall utilization
        if total_limits > 0:
            utilization = (total_balances / total_limits) * 100
            profile.current_utilization_percent = min(100, max(0, utilization))
            profile.total_credit_limits = total_limits
            profile.total_revolving_balances = total_balances
            print(f"DEBUG: Final calculated utilization: {utilization:.2f}%")
        else:
            profile.current_utilization_percent = 0
            profile.total_credit_limits = 0
            profile.total_revolving_balances = 0
            print("DEBUG: No credit cards detected, utilization remains 0%")
            print("DEBUG: Consider adding debts with names containing 'card', 'credit', or bank names")
        
        profile.updated_at = datetime.utcnow()
        await profile.save()
        return profile
    
    @staticmethod
    def _is_credit_card(debt_name: str, interest_rate: float, debt_count: int) -> bool:
        """Helper method to determine if a debt is a credit card"""
        debt_name_lower = debt_name.lower()
        
        # Comprehensive list of credit card indicators
        credit_indicators = [
            # Generic terms
            'credit', 'card', 'cc', 'credit line', 'revolving',
            # Major card networks
            'visa', 'mastercard', 'amex', 'american express', 'discover', 'rupay',
            # Indian banks
            'hdfc', 'sbi', 'icici', 'axis', 'kotak', 'yes bank', 'rbl',
            'standard chartered', 'hsbc', 'indusind', 'bob', 'pnb', 'canara',
            'union bank', 'punjab national', 'bank of india', 'indian bank',
            # International banks
            'chase', 'citi', 'capital one', 'wells fargo', 'bank of america',
            # Store/retail cards
            'store', 'retail', 'shopping', 'amazon', 'flipkart'
        ]
        
        # Check for keyword matches
        if any(term in debt_name_lower for term in credit_indicators):
            return True
            
        # High interest rate suggests credit card
        if interest_rate >= 15:
            return True
            
        # If very few debts and moderate interest, might be credit card
        if debt_count <= 2 and interest_rate >= 10:
            return True
            
        return False
    
    @staticmethod
    async def analyze_debt_impact_on_credit(clerk_user_id: str) -> DebtImpactOnCredit:
        """Analyze how current debts impact credit score"""
        debts = await Debt.find(
            Debt.clerk_user_id == clerk_user_id,
            Debt.is_active == True
        ).to_list()
        
        high_utilization_debts = []
        credit_building_opportunities = []
        consolidation_recommendations = []
        payment_optimization_tips = []
        
        credit_card_count = 0
        high_apr_count = 0
        
        for debt in debts:
            debt_dict = debt.to_dict()
            
            # Use improved credit card detection
            is_credit_card = CreditService._is_credit_card(debt.name, debt.interest_rate, len(debts))
            
            if is_credit_card:
                credit_card_count += 1
                estimated_limit = debt.total_amount * 2.0 if debt.total_amount > 0 else 50000
                estimated_utilization = (debt.total_amount / estimated_limit) * 100
                
                debt_dict.update({
                    "estimated_utilization": estimated_utilization,
                    "estimated_limit": estimated_limit,
                    "is_credit_card": True
                })
                
                if estimated_utilization > 30:
                    high_utilization_debts.append(debt_dict)
                    target_balance = estimated_limit * 0.30
                    payment_optimization_tips.append(
                        f"Pay down {debt.name} to ₹{target_balance:,.0f} (30% utilization target)"
                    )
            
            # Check for high APR debts
            if debt.interest_rate > 20:
                high_apr_count += 1
                consolidation_recommendations.append(
                    f"Consider refinancing {debt.name} (APR: {debt.interest_rate}%) to a lower rate"
                )
        
        # Credit building opportunities
        if credit_card_count == 0:
            credit_building_opportunities.append(
                "Consider getting your first credit card to start building credit history"
            )
        elif credit_card_count == 1:
            credit_building_opportunities.append(
                "Consider adding a second credit card to improve credit mix and lower overall utilization"
            )
        
        if len(debts) > 0:
            payment_optimization_tips.extend([
                "Set up automatic payments for all minimum amounts",
                "Pay credit card balances before statement dates to reduce reported utilization",
                "Focus extra payments on highest APR debts first"
            ])
        
        if high_apr_count > 0:
            consolidation_recommendations.append(
                "Look into debt consolidation loans or balance transfer cards for high-rate debts"
            )
        
        return DebtImpactOnCredit(
            high_utilization_debts=high_utilization_debts,
            credit_building_opportunities=credit_building_opportunities,
            consolidation_recommendations=consolidation_recommendations,
            payment_optimization_tips=payment_optimization_tips
        )
    
    @staticmethod
    async def generate_utilization_breakdown(clerk_user_id: str) -> CreditUtilizationBreakdown:
        """Generate detailed credit utilization breakdown"""
        profile = await CreditService.refresh_utilization_from_debts(clerk_user_id)
        
        debts = await Debt.find(
            Debt.clerk_user_id == clerk_user_id,
            Debt.is_active == True
        ).to_list()
        
        per_card_utilization = []
        target_utilization = 30.0
        
        for debt in debts:
            if CreditService._is_credit_card(debt.name, debt.interest_rate, len(debts)):
                estimated_limit = debt.total_amount * 2.0 if debt.total_amount > 0 else 50000
                current_util = (debt.total_amount / estimated_limit) * 100
                target_balance = estimated_limit * (target_utilization / 100)
                amount_to_pay = max(0, debt.total_amount - target_balance)
                
                per_card_utilization.append({
                    "debt_name": debt.name,
                    "current_balance": debt.total_amount,
                    "estimated_credit_limit": estimated_limit,
                    "current_utilization": current_util,
                    "target_balance": target_balance,
                    "amount_to_pay_down": amount_to_pay,
                    "monthly_interest": debt.calculate_monthly_interest()
                })
        
        amount_to_pay_down = max(0, profile.total_revolving_balances - (profile.total_credit_limits * 0.30))
        
        return CreditUtilizationBreakdown(
            total_balances=profile.total_revolving_balances,
            total_limits=profile.total_credit_limits,
            utilization_percent=profile.current_utilization_percent,
            amount_to_pay_down=amount_to_pay_down,
            per_card_utilization=per_card_utilization
        )
    
    @staticmethod
    async def generate_score_prediction(clerk_user_id: str) -> ScoreImprovementPrediction:
        """Generate score improvement prediction"""
        profile = await CreditService.refresh_utilization_from_debts(clerk_user_id)
        prediction_data = profile.predict_score_improvement()
        
        return ScoreImprovementPrediction(**prediction_data)
    
    @staticmethod
    async def generate_quick_wins(profile: CreditProfile, debts: List[Debt]) -> List[QuickWin]:
        """Generate quick win recommendations (30-90 days)"""
        quick_wins = []
        
        if profile.current_utilization_percent > 30:
            amount_to_pay = profile.total_revolving_balances - (profile.total_credit_limits * 0.30)
            quick_wins.append(QuickWin(
                title="Reduce credit utilization below 30%",
                action=f"Pay down credit card balances by ₹{amount_to_pay:,.0f}",
                impact_description="Could improve score by 20-50 points",
                timeline_days=30
            ))
        
        if profile.payment_history != PaymentHistoryStatus.ALWAYS_ON_TIME:
            quick_wins.append(QuickWin(
                title="Set up automatic payments",
                action="Enable autopay for all minimum payments to ensure on-time payment history",
                impact_description="Prevents future score damage and begins rebuilding payment history",
                timeline_days=1
            ))
        
        if profile.last_checked in ["6+_months", "never_checked"]:
            quick_wins.append(QuickWin(
                title="Check your credit reports",
                action="Get free credit reports from all three bureaus and dispute any errors",
                impact_description="Error removal can improve score by 20-100 points instantly",
                timeline_days=14
            ))
        
        high_apr_debts = [d for d in debts if d.interest_rate > 20]
        if high_apr_debts:
            quick_wins.append(QuickWin(
                title="Research debt consolidation",
                action="Get quotes for personal loans or balance transfers for high-rate debts",
                impact_description="Could lower payments and reduce utilization faster",
                timeline_days=7
            ))
        
        quick_wins.append(QuickWin(
            title="Keep old accounts open",
            action="Don't close your oldest credit cards to maintain credit history length",
            impact_description="Preserves average account age which affects 15% of your score",
            timeline_days=1
        ))
        
        return quick_wins
    
    @staticmethod
    async def generate_ai_action_plan(clerk_user_id: str, request: CreditScoreTipRequest) -> str:
        """Generate AI-powered credit improvement plan"""
        profile = await CreditService.refresh_utilization_from_debts(clerk_user_id)
        
        user = await User.find_one(User.clerk_user_id == clerk_user_id)
        debts = await Debt.find(
            Debt.clerk_user_id == clerk_user_id,
            Debt.is_active == True
        ).to_list()
        
        context = {
            "current_score": profile.current_score or 370,
            "target_score": profile.target_score,
            "payment_history": profile.payment_history.value,
            "utilization_percent": profile.current_utilization_percent,
            "account_age_years": profile.average_account_age_years,
            "new_accounts": profile.new_accounts_last_2_years,
            "account_types": [t.value for t in profile.account_types],
            "last_checked": profile.last_checked,
            "total_debt": sum(d.total_amount for d in debts),
            "debt_count": len(debts),
            "highest_apr": max([d.interest_rate for d in debts], default=0),
            "monthly_income": getattr(user, 'monthly_income', 0) if user else 0,
            "monthly_expenses": getattr(user, 'monthly_expenses', 0) if user else 0,
            "debt_names": [d.name for d in debts[:5]]
        }
        
        prompt = f"""
        As a credit counselor, provide a personalized credit improvement plan for this user:
        
        CREDIT PROFILE:
        - Current Score: {context['current_score']}
        - Target Score: {context['target_score']}
        - Payment History: {context['payment_history']}
        - Credit Utilization: {context['utilization_percent']:.1f}%
        - Average Account Age: {context['account_age_years']} years
        - New Accounts (last 2 years): {context['new_accounts']}
        - Account Types: {', '.join(context['account_types'])}
        - Last Credit Report Check: {context['last_checked']}
        
        DEBT PROFILE:
        - Total Debt: ₹{context['total_debt']:,.0f}
        - Number of Debts: {context['debt_count']}
        - Highest APR: {context['highest_apr']:.1f}%
        - Current Debts: {', '.join(context['debt_names'])}
        - Monthly Income: ₹{context['monthly_income']:,.0f}
        - Monthly Expenses: ₹{context['monthly_expenses']:,.0f}
        
        Please provide:
        1. **Priority Actions** (top 3 most impactful steps)
        2. **Timeline** (Month 1-3, Month 4-6, Month 7-12)
        3. **Expected Impact** (realistic score improvement range)
        4. **Monitoring Strategy** (what to track monthly/quarterly)
        5. **Red Flags to Avoid** (actions that could hurt the score)
        
        Focus on actionable, specific advice with numbers and realistic timelines.
        Be encouraging but realistic about expectations.
        """
        
        ai_response = await LLMService.generate_credit_advice(prompt)
        return ai_response
    
    @staticmethod
    async def get_comprehensive_analysis(
        clerk_user_id: str, 
        request: CreditScoreTipRequest
    ) -> CreditAnalysisResponse:
        """Get comprehensive credit score analysis with AI recommendations"""
        
        profile = await CreditService.refresh_utilization_from_debts(clerk_user_id)
        
        debts = await Debt.find(
            Debt.clerk_user_id == clerk_user_id,
            Debt.is_active == True
        ).to_list()
        
        factors_assessment = CreditFactorsAssessment(
            payment_history=profile.payment_history,
            average_account_age_years=profile.average_account_age_years,
            new_accounts_last_2_years=profile.new_accounts_last_2_years,
            account_types=profile.account_types,
            current_utilization_percent=profile.current_utilization_percent,
            total_credit_limits=profile.total_credit_limits,
            total_revolving_balances=profile.total_revolving_balances
        )
        
        score_prediction = await CreditService.generate_score_prediction(clerk_user_id)
        debt_impact = await CreditService.analyze_debt_impact_on_credit(clerk_user_id)
        utilization_breakdown = await CreditService.generate_utilization_breakdown(clerk_user_id)
        quick_wins = await CreditService.generate_quick_wins(profile, debts)
        
        ai_plan = await CreditService.generate_ai_action_plan(clerk_user_id, request)
        
        profile.last_ai_analysis = {"generated_plan": ai_plan}
        profile.recommendations_generated_at = datetime.utcnow()
        await profile.save()
        
        action_plan = CreditActionPlan(
            priority_actions=[],
            quick_wins=quick_wins,
            timeline_summary={
                "month_1_3": ["Focus on utilization reduction", "Set up autopay", "Check credit reports"],
                "month_4_6": ["Pay down high-APR debt", "Monitor score improvements", "Avoid new credit"],
                "month_7_12": ["Continue monitoring", "Reassess strategy", "Celebrate improvements"]
            },
            expected_impact=score_prediction,
            monitoring_strategy={
                "monthly": "Check payments, balances, utilization",
                "quarterly": "Review full credit report and score",
                "annually": "Reassess overall strategy and goals"
            },
            red_flags_to_avoid=[
                "Don't close old credit cards",
                "Avoid maxing out credit limits", 
                "Don't miss payments",
                "Limit new credit applications",
                "Don't ignore credit report errors"
            ]
        )
        
        profile_response = CreditProfileResponse(
            id=str(profile.id),
            current_score=profile.current_score,
            target_score=profile.target_score,
            last_checked=profile.last_checked,
            factors_assessment=factors_assessment,
            ai_analysis_summary=ai_plan[:500] + "..." if len(ai_plan) > 500 else ai_plan,
            action_plan=action_plan,
            score_prediction=score_prediction,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
            recommendations_generated_at=profile.recommendations_generated_at
        )
        
        personalized_tips = [
            f"Your utilization is {profile.current_utilization_percent:.1f}% - target is under 30%",
            "Payment history is the most important factor (35% of score)",
            f"With consistent effort, you could reach {score_prediction.predicted_score} in {score_prediction.timeline_months} months"
        ]
        
        if debts:
            highest_apr = max(debts, key=lambda x: x.interest_rate)
            personalized_tips.append(f"Focus extra payments on {highest_apr.name} with {highest_apr.interest_rate}% APR")
        
        next_steps = [
            "Review your personalized action plan below",
            "Start with the highest-priority quick wins", 
            "Set up monitoring for monthly progress tracking",
            "Consider setting up automatic payments if not already done"
        ]
        
        return CreditAnalysisResponse(
            profile=profile_response,
            debt_impact=debt_impact,
            utilization_breakdown=utilization_breakdown,
            personalized_tips=personalized_tips,
            ai_generated_plan=ai_plan,
            next_steps=next_steps
        )