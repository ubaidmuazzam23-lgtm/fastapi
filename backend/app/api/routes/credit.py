# app/api/routes/credit.py - UPDATED WITH CREDIT CARD MANAGEMENT
from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Optional

from app.models.user import User
from app.models.credit_profile import CreditCardDetails
from app.schemas.credit import (
    CreditProfileCreate, CreditProfileUpdate, CreditProfileResponse,
    CreditAnalysisResponse, CreditScoreTipRequest, ScoreImprovementPrediction,
    CreditUtilizationBreakdown, DebtImpactOnCredit, CreditCardDetailsCreate,
    CreditCardBalanceUpdate
)
from app.services.credit_service import CreditService
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/credit", tags=["credit-score"])

@router.get("/profile", response_model=CreditProfileResponse)
async def get_credit_profile(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get user's credit profile with current analysis"""
    try:
        profile = await CreditService.get_or_create_profile(current_user.clerk_user_id)
        
        # Recalculate utilization from stored credit card data
        profile.recalculate_utilization()
        await profile.save()
        
        # Get factors assessment
        from app.schemas.credit import CreditFactorsAssessment
        factors_assessment = CreditFactorsAssessment(
            payment_history=profile.payment_history,
            average_account_age_years=profile.average_account_age_years,
            new_accounts_last_2_years=profile.new_accounts_last_2_years,
            account_types=profile.account_types,
            current_utilization_percent=profile.current_utilization_percent,
            total_credit_limits=profile.total_credit_limits,
            total_revolving_balances=profile.total_revolving_balances
        )
        
        return CreditProfileResponse(
            id=str(profile.id),
            current_score=profile.current_score,
            target_score=profile.target_score,
            last_checked=profile.last_checked,
            factors_assessment=factors_assessment,
            ai_analysis_summary=profile.last_ai_analysis.get("generated_plan", "")[:500] if profile.last_ai_analysis else None,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
            recommendations_generated_at=profile.recommendations_generated_at,
            # NEW: Include credit card details
            credit_cards=profile.per_card_utilization
        )
        
    except Exception as e:
        print(f"Error getting credit profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/profile", response_model=CreditProfileResponse)
async def create_or_update_profile(
    request: Request,
    profile_data: CreditProfileCreate,
    current_user: User = Depends(get_current_user)
):
    """Create or update credit profile with credit card details"""
    try:
        profile = await CreditService.get_or_create_profile(current_user.clerk_user_id)
        
        # Update basic profile fields
        if profile_data.current_score is not None:
            profile.current_score = profile_data.current_score
        profile.target_score = profile_data.target_score
        profile.last_checked = profile_data.last_checked
        profile.payment_history = profile_data.payment_history
        profile.average_account_age_years = profile_data.average_account_age_years
        profile.new_accounts_last_2_years = profile_data.new_accounts_last_2_years
        profile.account_types = profile_data.account_types
        
        # Handle credit card details
        if profile_data.credit_cards:
            # Clear existing cards and add new ones
            profile.credit_cards = []
            for card_data in profile_data.credit_cards:
                card_details = CreditCardDetails(**card_data.model_dump())
                profile.add_credit_card(card_details)
        
        await profile.save()
        
        # Return updated profile (reuse get logic)
        return await get_credit_profile(request, current_user)
        
    except Exception as e:
        print(f"Error updating credit profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# NEW: Credit Card Management Endpoints
@router.post("/cards")
async def add_credit_card(
    request: Request,
    card_data: CreditCardDetailsCreate,
    current_user: User = Depends(get_current_user)
):
    """Add a new credit card to the profile"""
    try:
        profile = await CreditService.get_or_create_profile(current_user.clerk_user_id)
        
        card_details = CreditCardDetails(**card_data.model_dump())
        profile.add_credit_card(card_details)
        await profile.save()
        
        return {
            "message": f"Credit card '{card_data.name}' added successfully",
            "card": {
                "name": card_data.name,
                "limit": card_data.credit_limit,
                "balance": card_data.current_balance,
                "utilization": card_details.utilization_percent
            },
            "updated_profile": {
                "total_utilization": profile.current_utilization_percent,
                "total_limits": profile.total_credit_limits,
                "total_balances": profile.total_revolving_balances
            }
        }
        
    except Exception as e:
        print(f"Error adding credit card: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/cards/{card_name}/balance")
async def update_card_balance(
    request: Request,
    card_name: str,
    balance_update: CreditCardBalanceUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update the balance of a specific credit card"""
    try:
        profile = await CreditService.get_or_create_profile(current_user.clerk_user_id)
        
        # Find the card
        card = next((c for c in profile.credit_cards if c.name.lower() == card_name.lower()), None)
        if not card:
            raise HTTPException(status_code=404, detail=f"Credit card '{card_name}' not found")
        
        old_balance = card.current_balance
        profile.update_card_balance(card_name, balance_update.new_balance)
        await profile.save()
        
        return {
            "message": f"Balance updated for '{card_name}'",
            "card": card_name,
            "old_balance": old_balance,
            "new_balance": balance_update.new_balance,
            "utilization_change": {
                "old_utilization": (old_balance / card.credit_limit) * 100 if card.credit_limit > 0 else 0,
                "new_utilization": card.utilization_percent
            },
            "profile_utilization": profile.current_utilization_percent
        }
        
    except Exception as e:
        print(f"Error updating card balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cards/{card_name}")
async def remove_credit_card(
    request: Request,
    card_name: str,
    current_user: User = Depends(get_current_user)
):
    """Remove a credit card from the profile"""
    try:
        profile = await CreditService.get_or_create_profile(current_user.clerk_user_id)
        
        # Check if card exists
        card_exists = any(c.name.lower() == card_name.lower() for c in profile.credit_cards)
        if not card_exists:
            raise HTTPException(status_code=404, detail=f"Credit card '{card_name}' not found")
        
        profile.remove_credit_card(card_name)
        await profile.save()
        
        return {
            "message": f"Credit card '{card_name}' removed successfully",
            "remaining_cards": len(profile.credit_cards),
            "updated_utilization": profile.current_utilization_percent
        }
        
    except Exception as e:
        print(f"Error removing credit card: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cards")
async def get_credit_cards(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get all credit cards with detailed breakdown"""
    try:
        profile = await CreditService.get_or_create_profile(current_user.clerk_user_id)
        
        return {
            "total_cards": len(profile.credit_cards),
            "active_cards": len([c for c in profile.credit_cards if c.is_active]),
            "cards": profile.per_card_utilization,
            "summary": {
                "total_limits": profile.total_credit_limits,
                "total_balances": profile.total_revolving_balances,
                "overall_utilization": profile.current_utilization_percent,
                "available_credit": profile.total_credit_limits - profile.total_revolving_balances
            },
            "recommendations": profile.calculate_paydown_targets()
        }
        
    except Exception as e:
        print(f"Error getting credit cards: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/utilization-breakdown", response_model=CreditUtilizationBreakdown)
async def get_utilization_breakdown(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get enhanced detailed credit utilization breakdown"""
    try:
        profile = await CreditService.get_or_create_profile(current_user.clerk_user_id)
        
        # Recalculate to ensure fresh data
        profile.recalculate_utilization()
        
        cards_above_30 = profile.get_highest_utilization_cards(30.0)
        cards_above_90 = profile.get_highest_utilization_cards(90.0)
        paydown_recommendations = profile.calculate_paydown_targets()
        
        # Calculate monthly savings potential
        monthly_savings = 0
        for card in profile.credit_cards:
            if card.current_balance > 0 and card.interest_rate:
                monthly_interest = (card.current_balance * (card.interest_rate / 100)) / 12
                target_balance = card.credit_limit * 0.30
                if card.current_balance > target_balance:
                    paydown_amount = card.current_balance - target_balance
                    potential_savings = (paydown_amount * (card.interest_rate / 100)) / 12
                    monthly_savings += potential_savings
        
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
        
    except Exception as e:
        print(f"Error generating utilization breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/score-prediction", response_model=ScoreImprovementPrediction)
async def get_score_prediction(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get credit score improvement prediction based on actual credit card data"""
    try:
        profile = await CreditService.get_or_create_profile(current_user.clerk_user_id)
        
        # Ensure utilization is current
        profile.recalculate_utilization()
        prediction_data = profile.predict_score_improvement()
        
        return ScoreImprovementPrediction(**prediction_data)
        
    except Exception as e:
        print(f"Error generating score prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced existing endpoints to work with actual credit card data
@router.post("/generate-tips", response_model=CreditAnalysisResponse)
async def generate_personalized_tips(
    request: Request,
    tip_request: CreditScoreTipRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate comprehensive personalized credit score improvement plan"""
    try:
        analysis = await CreditService.get_comprehensive_analysis(
            current_user.clerk_user_id,
            tip_request
        )
        return analysis
        
    except Exception as e:
        print(f"Error generating credit tips: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk-update-balances")
async def bulk_update_card_balances(
    request: Request,
    balance_updates: List[CreditCardBalanceUpdate],
    current_user: User = Depends(get_current_user)
):
    """Update multiple card balances at once"""
    try:
        profile = await CreditService.get_or_create_profile(current_user.clerk_user_id)
        
        updates_made = []
        errors = []
        
        for update in balance_updates:
            try:
                card = next((c for c in profile.credit_cards if c.name.lower() == update.card_name.lower()), None)
                if card:
                    old_balance = card.current_balance
                    profile.update_card_balance(update.card_name, update.new_balance)
                    updates_made.append({
                        "card": update.card_name,
                        "old_balance": old_balance,
                        "new_balance": update.new_balance
                    })
                else:
                    errors.append(f"Card '{update.card_name}' not found")
            except Exception as e:
                errors.append(f"Error updating {update.card_name}: {str(e)}")
        
        if updates_made:
            await profile.save()
        
        return {
            "message": f"Bulk update completed. {len(updates_made)} cards updated.",
            "updates_made": updates_made,
            "errors": errors,
            "new_overall_utilization": profile.current_utilization_percent
        }
        
    except Exception as e:
        print(f"Error in bulk update: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Debug/test endpoint to verify credit card calculations
@router.get("/test/card-calculations")
async def test_card_calculations(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Test endpoint to verify credit card calculations"""
    try:
        profile = await CreditService.get_or_create_profile(current_user.clerk_user_id)
        
        # Force recalculation
        profile.recalculate_utilization()
        
        card_details = []
        for card in profile.credit_cards:
            card_details.append({
                "name": card.name,
                "limit": card.credit_limit,
                "balance": card.current_balance,
                "utilization": card.utilization_percent,
                "available": card.available_credit,
                "monthly_minimum": card.minimum_payment,
                "apr": card.interest_rate
            })
        
        return {
            "total_cards": len(profile.credit_cards),
            "card_details": card_details,
            "calculations": {
                "total_limits": profile.total_credit_limits,
                "total_balances": profile.total_revolving_balances,
                "overall_utilization": profile.current_utilization_percent,
                "per_card_breakdown": profile.per_card_utilization
            },
            "paydown_targets": profile.calculate_paydown_targets(),
            "high_utilization_cards": profile.get_highest_utilization_cards(30.0),
            "maxed_out_cards": profile.get_highest_utilization_cards(90.0)
        }
        
    except Exception as e:
        return {"error": str(e), "status": "failed"}