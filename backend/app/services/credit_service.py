# app/services/credit_service.py - UPDATED VERSION WITH CREDIT CARD SUPPORT
from typing import Optional, List, Dict, Any
from datetime import datetime
from beanie import PydanticObjectId

from app.models.credit_profile import CreditProfile, PaymentHistoryStatus, CreditAccountType, CreditCardDetails
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
                account_types=[CreditAccountType.CREDIT_CARD],
                credit_cards=[]  # Start with empty list
            )
            await profile.insert()
        
        return profile
    
    @staticmethod
    async def update_profile(clerk_user_id: str, update_data: CreditProfileUpdate) -> Optional[CreditProfile]:
        """Update credit profile with credit card details"""
        profile = await CreditService.get_or_create_profile(clerk_user_id)
        
        # Update basic fields
        update_dict = {}
        if update_data.current_score is not None:
            update_dict["current_score"] = update_data.current_score
        if update_data.target_score is not None:
            update_dict["target_score"] = update_data.target_score
        if update_data.last_checked is not None:
            update_dict["last_checked"] = update_data.last_checked
        if update_data.payment_history is not None:
            update_dict["payment_history"] = update_data.payment_history
        if update_data.average_account_age_years is not None:
            update_dict["average_account_age_years"] = update_data.average_account_age_years
        if update_data.new_accounts_last_2_years is not None:
            update_dict["new_accounts_last_2_years"] = update_data.new_accounts_last_2_years
        if update_data.account_types is not None:
            update_dict["account_types"] = update_data.account_types
        
        update_dict["updated_at"] = datetime.utcnow()
        
        # Handle credit card updates
        if update_data.credit_cards is not None:
            # Clear existing cards and add new ones
            profile.credit_cards = []
            for card_data in update_data.credit_cards:
                card_details = CreditCardDetails(**card_data.model_dump())
                profile.add_credit_card(card_details)
        
        # Apply updates
        if update_dict:
            for key, value in update_dict.items():
                setattr(profile, key, value)
        
        await profile.save()
        return profile
    
    @staticmethod
    async def refresh_utilization_from_debts(clerk_user_id: str) -> CreditProfile:
        """Legacy method: Update from debt data if no credit cards are manually added"""
        profile = await CreditService.get_or_create_profile(clerk_user_id)
        
        # If user has manually added credit cards, use those instead of debt inference
        if len(profile.credit_cards) > 0:
            print(f"DEBUG: Using {len(profile.credit_cards)} manually added credit cards")
            profile.recalculate_utilization()
            await profile.save()
            return profile
        
        # Legacy logic for inferring from debt data
        print(f"DEBUG: No credit cards found, attempting to infer from debt data")
        
        debts = await Debt.find(
            Debt.clerk_user_id == clerk_user_id,
            Debt.is_active == True
        ).to_list()
        
        print(f"DEBUG: Found {len(debts)} debts for user {clerk_user_id}")
        
        inferred_cards = []
        
        for debt in debts:
            if CreditService._is_credit_card_debt(debt):
                # Create inferred credit card
                estimated_limit = CreditService._estimate_credit_limit(debt)
                
                card = CreditCardDetails(
                    name=debt.name,
                    credit_limit=estimated_limit,
                    current_balance=debt.total_amount,
                    interest_rate=debt.interest_rate,
                    is_active=True
                )
                
                inferred_cards.append(card)
                print(f"DEBUG: Inferred card '{debt.name}': Balance=₹{debt.total_amount:,.0f}, "
                     f"Est Limit=₹{estimated_limit:,.0f}, Utilization={card.utilization_percent:.1f}%")
        
        if inferred_cards:
            profile.credit_cards = inferred_cards
            profile.recalculate_utilization()
            await profile.save()
            print(f"DEBUG: Added {len(inferred_cards)} inferred credit cards")
        else:
            print("DEBUG: No credit card debts found")
        
        return profile
    
    @staticmethod
    def _is_credit_card_debt(debt: Debt) -> bool:
        """Enhanced credit card detection from debt data"""
        debt_name_lower = debt.name.lower()
        
        # Comprehensive credit card indicators
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
        
        # Primary: Check for keyword matches
        if any(term in debt_name_lower for term in credit_indicators):
            return True
            
        # Secondary: High interest rate suggests credit card (India: 24-48% APR typical)
        if debt.interest_rate >= 18:
            return True
            
        # Tertiary: Moderate interest rate with small balance might be credit card
        if debt.interest_rate >= 12 and debt.total_amount < 100000:  # Less than ₹1L
            return True
            
        return False
    
    @staticmethod
    def _estimate_credit_limit(debt: Debt) -> float:
        """Estimate credit limit based on current balance and debt characteristics"""
        if debt.total_amount == 0:
            # Zero balance - assume reasonable starting limit
            return 50000  # ₹50,000 default
        
        # Base estimation on current balance with intelligent assumptions
        if debt.total_amount < 5000:
            # Very low balance - likely low utilization
            return debt.total_amount * 8  # Assume 12.5% utilization
        elif debt.total_amount < 25000:
            # Low-medium balance 
            return debt.total_amount * 3  # Assume ~33% utilization
        elif debt.total_amount < 100000:
            # Medium balance
            return debt.total_amount * 2  # Assume 50% utilization
        else:
            # High balance - might be maxed out or high limit card
            return debt.total_amount * 1.5  # Assume 67% utilization
    
    @staticmethod
    async def smart_sync_debts_to_credit_cards(clerk_user_id: str) -> Dict[str, Any]:
        """Intelligent sync between debt data and credit card profiles"""
        profile = await CreditService.get_or_create_profile(clerk_user_id)
        debts = await Debt.find(
            Debt.clerk_user_id == clerk_user_id,
            Debt.is_active == True
        ).to_list()
        
        sync_results = {
            "matched_cards": [],
            "new_cards_from_debts": [],
            "unmatched_debts": [],
            "orphaned_cards": [],
            "updated_balances": []
        }
        
        # Find credit card debts
        credit_card_debts = [debt for debt in debts if CreditService._is_credit_card_debt(debt)]
        
        # Match existing cards with debts (by name similarity)
        for debt in credit_card_debts:
            matched_card = None
            
            for card in profile.credit_cards:
                # Simple name matching (could be enhanced with fuzzy matching)
                if CreditService._cards_match(card.name, debt.name):
                    matched_card = card
                    break
            
            if matched_card:
                # Update existing card balance
                old_balance = matched_card.current_balance
                matched_card.current_balance = debt.total_amount
                if debt.interest_rate and not matched_card.interest_rate:
                    matched_card.interest_rate = debt.interest_rate
                
                sync_results["matched_cards"].append({
                    "card_name": matched_card.name,
                    "old_balance": old_balance,
                    "new_balance": debt.total_amount
                })
                
                if old_balance != debt.total_amount:
                    sync_results["updated_balances"].append(matched_card.name)
            else:
                # Create new card from debt
                estimated_limit = CreditService._estimate_credit_limit(debt)
                new_card = CreditCardDetails(
                    name=debt.name,
                    credit_limit=estimated_limit,
                    current_balance=debt.total_amount,
                    interest_rate=debt.interest_rate,
                    is_active=True
                )
                
                profile.add_credit_card(new_card)
                sync_results["new_cards_from_debts"].append({
                    "card_name": debt.name,
                    "estimated_limit": estimated_limit,
                    "balance": debt.total_amount
                })
        
        # Find non-credit-card debts
        sync_results["unmatched_debts"] = [
            debt.name for debt in debts 
            if not CreditService._is_credit_card_debt(debt)
        ]
        
        # Find cards without matching debts (user manually added)
        debt_names_lower = [debt.name.lower() for debt in credit_card_debts]
        sync_results["orphaned_cards"] = [
            card.name for card in profile.credit_cards
            if not any(CreditService._cards_match(card.name, debt_name) for debt_name in debt_names_lower)
        ]
        
        # Recalculate and save
        profile.recalculate_utilization()
        await profile.save()
        
        sync_results["final_utilization"] = profile.current_utilization_percent
        sync_results["total_cards"] = len(profile.credit_cards)
        
        return sync_results
    
    @staticmethod
    def _cards_match(card_name: str, debt_name: str) -> bool:
        """Check if a credit card name matches a debt name"""
        card_clean = card_name.lower().strip()
        debt_clean = debt_name.lower().strip()
        
        # Exact match
        if card_clean == debt_clean:
            return True
        
        # One contains the other
        if card_clean in debt_clean or debt_clean in card_clean:
            return True
        
        # Extract meaningful words and check overlap
        card_words = set(word for word in card_clean.split() if len(word) > 2)
        debt_words = set(word for word in debt_clean.split() if len(word) > 2)
        
        if card_words and debt_words:
            overlap = len(card_words.intersection(debt_words))
            total_unique = len(card_words.union(debt_words))
            
            # If 60%+ overlap in meaningful words
            if total_unique > 0 and (overlap / total_unique) >= 0.6:
                return True
        
        return False
    
    @staticmethod
    async def generate_utilization_breakdown(clerk_user_id: str) -> CreditUtilizationBreakdown:
        """Generate detailed credit utilization breakdown using actual card data"""
        profile = await CreditService.get_or_create_profile(clerk_user_id)
        
        # Ensure current data
        profile.recalculate_utilization()
        
        target_utilization = 30.0
        cards_above_30 = profile.get_highest_utilization_cards(30.0)
        cards_above_90 = profile.get_highest_utilization_cards(90.0)
        paydown_recommendations = profile.calculate_paydown_targets()
        
        # Calculate monthly interest savings potential
        monthly_savings = 0
        for card in profile.credit_cards:
            if card.current_balance > 0 and card.interest_rate:
                # Current monthly interest
                current_monthly_interest = (card.current_balance * (card.interest_rate / 100)) / 12
                
                # Interest after paying down to 30%
                target_balance = card.credit_limit * 0.30
                if card.current_balance > target_balance:
                    new_monthly_interest = (target_balance * (card.interest_rate / 100)) / 12
                    monthly_savings += (current_monthly_interest - new_monthly_interest)
        
        amount_to_pay_down = max(0, profile.total_revolving_balances - (profile.total_credit_limits * 0.30))
        
        return CreditUtilizationBreakdown(
            total_balances=profile.total_revolving_balances,
            total_limits=profile.total_credit_limits,
            utilization_percent=profile.current_utilization_percent,
            amount_to_pay_down=amount_to_pay_down,
            per_card_utilization=profile.per_card_utilization,
            cards_above_30_percent=cards_above_30,
            cards_above_90_percent=cards_above_90,
            paydown_recommendations=paydown_recommendations,
            monthly_savings_potential=monthly_savings
        )
    
    @staticmethod
    async def analyze_debt_impact_on_credit(clerk_user_id: str) -> DebtImpactOnCredit:
        """Analyze debt impact using both credit card data and debt data"""
        profile = await CreditService.get_or_create_profile(clerk_user_id)
        debts = await Debt.find(
            Debt.clerk_user_id == clerk_user_id,
            Debt.is_active == True
        ).to_list()
        
        high_utilization_debts = []
        credit_building_opportunities = []
        consolidation_recommendations = []
        payment_optimization_tips = []
        
        # Analyze credit cards from profile
        high_util_cards = profile.get_highest_utilization_cards(30.0)
        
        for card_data in high_util_cards:
            high_utilization_debts.append({
                **card_data,
                "is_credit_card": True,
                "type": "credit_card"
            })
            
            target_balance = card_data["limit"] * 0.30
            payment_needed = card_data["balance"] - target_balance
            payment_optimization_tips.append(
                f"Pay down {card_data['name']} by ₹{payment_needed:,.0f} to reach 30% utilization"
            )
        
        # Analyze other debts
        non_credit_debts = [debt for debt in debts if not CreditService._is_credit_card_debt(debt)]
        high_apr_debts = [debt for debt in debts if debt.interest_rate > 20]
        
        # Credit building opportunities
        if len(profile.credit_cards) == 0:
            credit_building_opportunities.append(
                "Add your first credit card to start building credit history"
            )
        elif len(profile.credit_cards) == 1:
            credit_building_opportunities.append(
                "Consider adding a second credit card to improve credit mix and lower overall utilization"
            )
        elif profile.total_credit_limits < 200000:  # Less than ₹2L total limit
            credit_building_opportunities.append(
                "Request credit limit increases on existing cards to improve utilization ratios"
            )
        
        if len([card for card in profile.credit_cards if card.current_balance == 0]) > 0:
            credit_building_opportunities.append(
                "Keep zero-balance cards active and make small purchases occasionally to maintain activity"
            )
        
        # Consolidation recommendations
        for debt in high_apr_debts:
            if CreditService._is_credit_card_debt(debt):
                consolidation_recommendations.append(
                    f"Consider balance transfer for {debt.name} (APR: {debt.interest_rate:.1f}%)"
                )
            else:
                consolidation_recommendations.append(
                    f"Consider refinancing {debt.name} (APR: {debt.interest_rate:.1f}%) with a lower-rate option"
                )
        
        if len(high_apr_debts) > 2:
            consolidation_recommendations.append(
                "Look into debt consolidation loans to combine multiple high-rate debts"
            )
        
        # Payment optimization
        if debts:
            payment_optimization_tips.extend([
                "Set up automatic minimum payments for all accounts",
                "Pay credit card balances before statement dates to reduce reported utilization",
                "Focus extra payments on highest APR debts first (avalanche method)",
                f"Consider the debt snowball method if you have {len(debts)} debts to manage"
            ])
        
        return DebtImpactOnCredit(
            high_utilization_debts=high_utilization_debts,
            credit_building_opportunities=credit_building_opportunities,
            consolidation_recommendations=consolidation_recommendations,
            payment_optimization_tips=payment_optimization_tips
        )
    
    @staticmethod
    async def generate_score_prediction(clerk_user_id: str) -> ScoreImprovementPrediction:
        """Generate score improvement prediction using accurate credit card data"""
        profile = await CreditService.get_or_create_profile(clerk_user_id)
        
        # Ensure calculations are current
        profile.recalculate_utilization()
        prediction_data = profile.predict_score_improvement()
        
        return ScoreImprovementPrediction(**prediction_data)
    
    @staticmethod
    async def generate_quick_wins(profile: CreditProfile, debts: List[Debt]) -> List[QuickWin]:
        """Generate quick win recommendations using credit card data"""
        quick_wins = []
        
        # Utilization-based quick wins (now more accurate)
        if profile.current_utilization_percent > 30:
            paydown_targets = profile.calculate_paydown_targets()
            total_paydown = sum(paydown_targets.values())
            
            quick_wins.append(QuickWin(
                title="Reduce credit utilization below 30%",
                action=f"Pay down credit card balances by ₹{total_paydown:,.0f} total",
                impact_description=f"Could improve score by 20-50 points. Target: {len(paydown_targets)} cards",
                timeline_days=30
            ))
        
        # Individual maxed-out cards
        maxed_cards = profile.get_highest_utilization_cards(90.0)
        if maxed_cards:
            card_name = maxed_cards[0]["name"]
            quick_wins.append(QuickWin(
                title=f"Emergency: Pay down maxed-out {card_name}",
                action=f"Pay at least ₹{maxed_cards[0]['balance'] * 0.2:,.0f} to get below 90% utilization",
                impact_description="Maxed cards severely hurt your score. Even small payments help immediately.",
                timeline_days=7
            ))
        
        # Zero-balance optimization
        zero_balance_cards = [card for card in profile.credit_cards if card.current_balance == 0]
        if zero_balance_cards:
            quick_wins.append(QuickWin(
                title="Optimize zero-balance cards",
                action=f"Keep {len(zero_balance_cards)} zero-balance cards open and make small monthly purchases",
                impact_description="Maintains credit history length and improves utilization ratio",
                timeline_days=1
            ))
        
        # Payment history
        if profile.payment_history != PaymentHistoryStatus.ALWAYS_ON_TIME:
            quick_wins.append(QuickWin(
                title="Set up automatic payments",
                action="Enable autopay for minimum payments on all credit accounts",
                impact_description="Prevents future score damage and begins rebuilding payment history",
                timeline_days=1
            ))
        
        # Credit report check
        if profile.last_checked in ["6+_months", "never_checked"]:
            quick_wins.append(QuickWin(
                title="Check credit reports for errors",
                action="Get free credit reports and dispute any inaccuracies found",
                impact_description="Error removal can improve score by 20-100+ points instantly",
                timeline_days=14
            ))
        
        return quick_wins
    
    # Rest of the methods remain the same as they work with the enhanced profile data
    @staticmethod
    async def generate_ai_action_plan(clerk_user_id: str, request: CreditScoreTipRequest) -> str:
        """Generate AI-powered credit improvement plan with accurate credit card data"""
        profile = await CreditService.get_or_create_profile(clerk_user_id)
        profile.recalculate_utilization()  # Ensure current data
        
        user = await User.find_one(User.clerk_user_id == clerk_user_id)
        debts = await Debt.find(
            Debt.clerk_user_id == clerk_user_id,
            Debt.is_active == True
        ).to_list()
        
        # Enhanced context with actual credit card data
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
            
            # NEW: Detailed credit card context
            "total_credit_cards": len(profile.credit_cards),
            "total_credit_limits": profile.total_credit_limits,
            "total_balances": profile.total_revolving_balances,
            "available_credit": profile.total_credit_limits - profile.total_revolving_balances,
            "highest_utilization_card": max(profile.per_card_utilization, key=lambda x: x["utilization"])["name"] if profile.per_card_utilization else None,
            "cards_over_30_percent": len(profile.get_highest_utilization_cards(30)),
            "maxed_out_cards": len(profile.get_highest_utilization_cards(90)),
            "zero_balance_cards": len([c for c in profile.credit_cards if c.current_balance == 0])
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
        
        DETAILED CREDIT CARD PROFILE:
        - Total Credit Cards: {context['total_credit_cards']}
        - Total Credit Limits: ₹{context['total_credit_limits']:,.0f}
        - Total Balances: ₹{context['total_balances']:,.0f}
        - Available Credit: ₹{context['available_credit']:,.0f}
        - Cards Over 30% Utilization: {context['cards_over_30_percent']}
        - Maxed Out Cards (90%+): {context['maxed_out_cards']}
        - Zero Balance Cards: {context['zero_balance_cards']}
        {f"- Highest Utilization Card: {context['highest_utilization_card']}" if context['highest_utilization_card'] else ""}
        
        DEBT & FINANCIAL PROFILE:
        - Total Debt: ₹{context['total_debt']:,.0f}
        - Number of Debts: {context['debt_count']}
        - Highest APR: {context['highest_apr']:.1f}%
        - Monthly Income: ₹{context['monthly_income']:,.0f}
        - Monthly Expenses: ₹{context['monthly_expenses']:,.0f}
        
        Please provide a comprehensive plan with:
        1. **Immediate Actions** (0-30 days) - focusing on highest impact moves
        2. **Short-term Goals** (1-6 months) - systematic improvements  
        3. **Long-term Strategy** (6+ months) - building excellent credit
        4. **Specific Numbers** - exactly how much to pay down, which cards to focus on
        5. **Monitoring Plan** - what to track and when
        6. **Warning Signs** - what could hurt the score
        
        Be specific about credit card strategies, utilization targets, and realistic timelines.
        Focus on actionable steps with actual rupee amounts and percentages.
        """
        
        ai_response = await LLMService.generate_credit_advice(prompt)
        return ai_response
    
    @staticmethod
    async def get_comprehensive_analysis(
        clerk_user_id: str, 
        request: CreditScoreTipRequest
    ) -> CreditAnalysisResponse:
        """Enhanced comprehensive analysis with actual credit card data"""
        
        profile = await CreditService.get_or_create_profile(clerk_user_id)
        profile.recalculate_utilization()  # Ensure fresh calculations
        
        debts = await Debt.find(
            Debt.clerk_user_id == clerk_user_id,
            Debt.is_active == True
        ).to_list()
        
        # All the analysis components
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
        
        # Update profile with AI analysis
        profile.last_ai_analysis = {"generated_plan": ai_plan}
        profile.recommendations_generated_at = datetime.utcnow()
        await profile.save()
        
        # Build action plan with enhanced credit card insights
        timeline_summary = {
            "month_1_3": [
                "Pay down highest utilization cards below 30%",
                "Set up automatic minimum payments",
                "Check credit reports for errors",
                "Stop using high-utilization cards temporarily"
            ],
            "month_4_6": [
                "Continue systematic debt paydown",
                "Monitor monthly credit score changes",
                "Consider requesting credit limit increases",
                "Maintain low balances on all cards"
            ],
            "month_7_12": [
                "Reassess credit mix and account types",
                "Consider adding new credit strategically",
                "Optimize payment timing and amounts",
                "Celebrate score improvements achieved"
            ]
        }
        
        # Enhanced monitoring strategy
        monitoring_strategy = {
            "weekly": "Track credit card balances and payments",
            "monthly": "Check overall utilization and payment history",
            "quarterly": "Review full credit report and score changes",
            "semi_annually": "Reassess strategy and update goals"
        }
        
        # Credit-card specific red flags
        red_flags_to_avoid = [
            "Never max out credit cards (stay below 90%)",
            "Don't close old credit cards (hurts credit history)",
            "Avoid missing minimum payments (35% of score)",
            "Limit new credit applications to avoid hard inquiries",
            "Don't ignore credit report errors or fraud",
            f"Keep overall utilization below 30% (currently {profile.current_utilization_percent:.1f}%)"
        ]
        
        action_plan = CreditActionPlan(
            priority_actions=[],  # Could be populated with CreditRecommendation objects
            quick_wins=quick_wins,
            timeline_summary=timeline_summary,
            expected_impact=score_prediction,
            monitoring_strategy=monitoring_strategy,
            red_flags_to_avoid=red_flags_to_avoid
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
        
        # Enhanced personalized tips using actual credit card data
        personalized_tips = [
            f"Your overall utilization is {profile.current_utilization_percent:.1f}% - target is under 30%",
            f"You have {len(profile.credit_cards)} credit cards with ₹{profile.total_credit_limits:,.0f} total limits",
            f"Available credit: ₹{profile.total_credit_limits - profile.total_revolving_balances:,.0f}",
            "Payment history is the most important factor (35% of your score)"
        ]
        
        # Add specific card-based tips
        if profile.get_highest_utilization_cards(90.0):
            maxed_card = profile.get_highest_utilization_cards(90.0)[0]
            personalized_tips.append(f"URGENT: {maxed_card['name']} is at {maxed_card['utilization']:.1f}% - pay this down immediately")
        
        if profile.get_highest_utilization_cards(30.0):
            high_util_count = len(profile.get_highest_utilization_cards(30.0))
            personalized_tips.append(f"{high_util_count} cards are above 30% utilization - focus paydown here first")
        
        paydown_targets = profile.calculate_paydown_targets()
        if paydown_targets:
            total_paydown = sum(paydown_targets.values())
            personalized_tips.append(f"Pay down ₹{total_paydown:,.0f} total across {len(paydown_targets)} cards to reach 30% target")
        
        if score_prediction.improvement_points > 0:
            personalized_tips.append(f"Potential improvement: {score_prediction.improvement_points} points in {score_prediction.timeline_months} months")
        
        # Debt-specific tips
        if debts:
            highest_apr = max(debts, key=lambda x: x.interest_rate)
            personalized_tips.append(f"Highest interest debt: {highest_apr.name} at {highest_apr.interest_rate}% - prioritize this")
        
        # Next steps with specific credit card actions
        next_steps = [
            "Review your credit card breakdown in the utilization section",
            "Start with the quick wins listed in your action plan",
            "Set up automatic minimum payments if not already done",
            "Focus extra payments on cards above 30% utilization"
        ]
        
        if len(profile.credit_cards) == 0:
            next_steps.insert(0, "Add your credit card details for more accurate analysis")
        elif profile.current_utilization_percent == 0:
            next_steps.insert(0, "Update your current credit card balances for accurate utilization calculation")
        
        return CreditAnalysisResponse(
            profile=profile_response,
            debt_impact=debt_impact,
            utilization_breakdown=utilization_breakdown,
            personalized_tips=personalized_tips,
            ai_generated_plan=ai_plan,
            next_steps=next_steps
        )