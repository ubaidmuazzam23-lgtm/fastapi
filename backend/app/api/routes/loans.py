"""
API routes for loan recommendations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.loan import (
    LoanRecommendationRequest,
    LoanRecommendationResponse,
    LoanRecommendationListResponse
)
from app.services.loan_service import LoanService

router = APIRouter(prefix="/loans", tags=["loans"])


@router.post("/recommend", response_model=LoanRecommendationResponse, status_code=status.HTTP_201_CREATED)
async def create_loan_recommendation(
    request: LoanRecommendationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new loan recommendation based on user's financial profile
    
    - Analyzes user's current debt and income situation
    - Fetches available loan options from top 10 Indian banks
    - Ranks loans by suitability
    - Returns detailed recommendations with comparison data
    """
    try:
        recommendation = await LoanService.create_loan_recommendation(
            clerk_user_id=current_user.clerk_user_id,
            request=request
        )
        return recommendation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.post("/chat")
async def chat_with_ai(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Chat with AI loan advisor
    
    - Ask questions about loan types
    - Get explanations about interest rates
    - Understand eligibility requirements
    - Compare different loan options
    """
    try:
        message = request.get("message", "")
        conversation_history = request.get("conversation_history", [])
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message is required"
            )
        
        response = await LoanService.chat_with_ai(message, conversation_history)
        
        return {"response": response}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )


@router.get("/history", response_model=LoanRecommendationListResponse)
async def get_recommendation_history(
    current_user: User = Depends(get_current_user)
):
    """
    Get user's past loan recommendations
    """
    try:
        recommendations = await LoanService.get_recommendation_history(
            clerk_user_id=current_user.clerk_user_id
        )
        return {
            "recommendations": recommendations,
            "total": len(recommendations)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch history: {str(e)}"
        )


@router.get("/{recommendation_id}", response_model=dict)
async def get_recommendation_by_id(
    recommendation_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific recommendation by ID
    """
    recommendation = await LoanService.get_recommendation_by_id(
        recommendation_id=recommendation_id,
        clerk_user_id=current_user.clerk_user_id
    )
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    return recommendation.to_dict()


@router.get("/analyze/affordability")
async def analyze_affordability(
    amount: float,
    term_months: int = 36,
    current_user: User = Depends(get_current_user)
):
    """
    Quick affordability check without creating a full recommendation
    
    - Check if you can afford a specific loan amount
    - See your DTI ratio impact
    - Get instant affordability score
    """
    try:
        from app.core.loan_analyzer import LoanAnalyzer
        
        # Get user's financial snapshot
        financial_snapshot = await LoanService.get_user_financial_snapshot(
            clerk_user_id=current_user.clerk_user_id
        )
        
        # Analyze affordability
        affordability = LoanAnalyzer.analyze_affordability(
            requested_amount=amount,
            monthly_income=financial_snapshot["monthly_income"],
            monthly_expenses=financial_snapshot["monthly_expenses"],
            total_existing_debt=financial_snapshot["total_existing_debt"],
            existing_monthly_debt_payments=financial_snapshot["existing_monthly_debt_payments"],
            term_months=term_months
        )
        
        return affordability
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze affordability: {str(e)}"
        )


@router.get("/types/available")
async def get_available_loan_types():
    """
    Get list of available loan types with descriptions
    """
    loan_types = [
        {
            "value": "personal",
            "label": "Personal Loan",
            "description": "For personal expenses, debt consolidation, medical emergencies",
            "typical_rate_range": "9.6% - 23%",
            "typical_amount_range": "₹50,000 - ₹50,00,000"
        },
        {
            "value": "home",
            "label": "Home Loan",
            "description": "For purchasing or constructing residential property",
            "typical_rate_range": "8.5% - 10.15%",
            "typical_amount_range": "₹10,00,000 - ₹10,00,00,000"
        },
        {
            "value": "car",
            "label": "Car Loan",
            "description": "For purchasing new or used vehicles",
            "typical_rate_range": "8.7% - 13%",
            "typical_amount_range": "₹1,00,000 - ₹50,00,000"
        },
        {
            "value": "education",
            "label": "Education Loan",
            "description": "For higher education in India or abroad",
            "typical_rate_range": "7.95% - 15.2%",
            "typical_amount_range": "₹1,00,000 - ₹2,00,00,000"
        },
        {
            "value": "gold",
            "label": "Gold Loan",
            "description": "Loan against gold jewelry or ornaments",
            "typical_rate_range": "7.5% - 29%",
            "typical_amount_range": "₹25,000 - ₹2,00,00,000"
        },
        {
            "value": "business",
            "label": "Business Loan",
            "description": "For business needs, working capital, expansion",
            "typical_rate_range": "8% - 15%",
            "typical_amount_range": "₹1,00,000 - ₹10,00,00,000"
        }
    ]
    return {"loan_types": loan_types}


@router.get("/banks/list")
async def get_available_banks():
    """
    Get list of banks available for loan comparison
    """
    banks = [
        {"name": "State Bank of India (SBI)", "code": "SBI"},
        {"name": "HDFC Bank", "code": "HDFC"},
        {"name": "ICICI Bank", "code": "ICICI"},
        {"name": "Axis Bank", "code": "AXIS"},
        {"name": "Kotak Mahindra Bank", "code": "KOTAK"},
        {"name": "Punjab National Bank", "code": "PNB"},
        {"name": "Bank of Baroda", "code": "BOB"},
        {"name": "Canara Bank", "code": "CANARA"},
        {"name": "Union Bank of India", "code": "UNION"},
        {"name": "IDFC First Bank", "code": "IDFC"}
    ]
    return {"banks": banks, "total": len(banks)}