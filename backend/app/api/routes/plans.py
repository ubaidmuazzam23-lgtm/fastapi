from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, Any
from app.models.user import User
from app.schemas.plan import (
    RepaymentPlanRequest, RepaymentPlanResponse, 
    StrategyComparisonResponse
)
from app.services.plan_service import PlanService
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/plans", tags=["repayment-plans"])

@router.get("/debt-summary")
async def get_debt_summary(
    request: Request,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get user's debt summary for planning interface"""
    try:
        summary = await PlanService.get_user_debt_summary(current_user.clerk_user_id)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get debt summary: {str(e)}"
        )

@router.post("/generate", response_model=RepaymentPlanResponse)
async def generate_repayment_plan(
    request: Request,
    plan_request: RepaymentPlanRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate optimized repayment plan using user's actual debt data"""
    try:
        plan = await PlanService.generate_repayment_plan(
            current_user.clerk_user_id, 
            plan_request
        )
        return plan
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate repayment plan: {str(e)}"
        )

@router.post("/compare", response_model=StrategyComparisonResponse)
async def compare_strategies(
    request: Request,
    monthly_budget: float,
    max_months: int = 60,
    current_user: User = Depends(get_current_user)
):
    """Compare all repayment strategies for user's debts"""
    try:
        if monthly_budget <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Monthly budget must be greater than 0"
            )
        
        comparison = await PlanService.compare_all_strategies(
            current_user.clerk_user_id,
            monthly_budget,
            max_months
        )
        return comparison
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare strategies: {str(e)}"
        )

@router.get("/validate-budget/{monthly_budget}")
async def validate_budget(
    request: Request,
    monthly_budget: float,
    current_user: User = Depends(get_current_user)
):
    """Validate if budget covers minimum payments"""
    try:
        summary = await PlanService.get_user_debt_summary(current_user.clerk_user_id)
        
        is_valid = monthly_budget >= summary["monthly_minimums"]
        excess_budget = monthly_budget - summary["monthly_minimums"] if is_valid else 0
        
        return {
            "is_valid": is_valid,
            "monthly_budget": monthly_budget,
            "minimum_required": summary["monthly_minimums"],
            "excess_budget": excess_budget,
            "message": "Budget covers minimums" if is_valid else f"Budget is ₹{summary['monthly_minimums'] - monthly_budget:,.0f} short"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate budget: {str(e)}"
        )