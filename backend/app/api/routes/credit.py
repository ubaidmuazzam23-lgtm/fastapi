# app/api/routes/credit.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Optional

from app.models.user import User
from app.schemas.credit import (
    CreditProfileCreate, CreditProfileUpdate, CreditProfileResponse,
    CreditAnalysisResponse, CreditScoreTipRequest, ScoreImprovementPrediction,
    CreditUtilizationBreakdown, DebtImpactOnCredit
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
        
        # Refresh utilization from latest debt data
        await CreditService.refresh_utilization_from_debts(current_user.clerk_user_id)
        
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
            recommendations_generated_at=profile.recommendations_generated_at
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
    """Create or update credit profile"""
    try:
        # Convert create to update schema
        from app.schemas.credit import CreditProfileUpdate
        update_data = CreditProfileUpdate(**profile_data.model_dump())
        
        updated_profile = await CreditService.update_profile(
            current_user.clerk_user_id, 
            update_data
        )
        
        if not updated_profile:
            raise HTTPException(status_code=404, detail="Failed to create/update profile")
        
        # Return updated profile (reuse get logic)
        return await get_credit_profile(request, current_user)
        
    except Exception as e:
        print(f"Error updating credit profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/score-prediction", response_model=ScoreImprovementPrediction)
async def get_score_prediction(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get credit score improvement prediction"""
    try:
        prediction = await CreditService.generate_score_prediction(current_user.clerk_user_id)
        return prediction
    except Exception as e:
        print(f"Error generating score prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/utilization-breakdown", response_model=CreditUtilizationBreakdown)
async def get_utilization_breakdown(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get detailed credit utilization breakdown"""
    try:
        breakdown = await CreditService.generate_utilization_breakdown(current_user.clerk_user_id)
        return breakdown
    except Exception as e:
        print(f"Error generating utilization breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debt-impact", response_model=DebtImpactOnCredit)
async def get_debt_impact_analysis(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Analyze how current debts impact credit score"""
    try:
        impact = await CreditService.analyze_debt_impact_on_credit(current_user.clerk_user_id)
        return impact
    except Exception as e:
        print(f"Error analyzing debt impact: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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

@router.post("/refresh-utilization")
async def refresh_credit_utilization(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Refresh credit utilization from current debt data"""
    try:
        profile = await CreditService.refresh_utilization_from_debts(current_user.clerk_user_id)
        
        return {
            "message": "Credit utilization refreshed successfully",
            "current_utilization_percent": profile.current_utilization_percent,
            "total_balances": profile.total_revolving_balances,
            "total_limits": profile.total_credit_limits,
            "updated_at": profile.updated_at
        }
        
    except Exception as e:
        print(f"Error refreshing utilization: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Test routes for development (remove in production)
@router.get("/test/quick-analysis")
async def test_quick_analysis(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Quick test endpoint for development"""
    try:
        profile = await CreditService.get_or_create_profile(current_user.clerk_user_id)
        prediction = await CreditService.generate_score_prediction(current_user.clerk_user_id)
        
        return {
            "profile_id": str(profile.id),
            "current_score": profile.current_score,
            "utilization": profile.current_utilization_percent,
            "prediction": prediction.model_dump(),
            "status": "success"
        }
        
    except Exception as e:
        return {"error": str(e), "status": "failed"}

@router.get("/factors-assessment")
async def get_credit_factors_assessment(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get current credit factors assessment"""
    try:
        profile = await CreditService.refresh_utilization_from_debts(current_user.clerk_user_id)
        
        from app.schemas.credit import CreditFactorsAssessment
        factors = CreditFactorsAssessment(
            payment_history=profile.payment_history,
            average_account_age_years=profile.average_account_age_years,
            new_accounts_last_2_years=profile.new_accounts_last_2_years,
            account_types=profile.account_types,
            current_utilization_percent=profile.current_utilization_percent,
            total_credit_limits=profile.total_credit_limits,
            total_revolving_balances=profile.total_revolving_balances
        )
        
        return factors
        
    except Exception as e:
        print(f"Error getting factors assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))