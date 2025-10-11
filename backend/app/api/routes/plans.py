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

@router.get("/debt-summary", response_model=Dict[str, Any])
async def get_debt_summary(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get user's debt summary for planning interface"""
    try:
        summary = await PlanService.get_user_debt_summary(current_user.clerk_user_id)
        return summary
    except Exception as e:
        print(f"ERROR in get_debt_summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get debt summary: {str(e)}"
        )

@router.post("/generate", response_model=RepaymentPlanResponse)
async def generate_repayment_plan(
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
    monthly_budget: float,
    current_user: User = Depends(get_current_user)
):
    """Validate if budget covers minimum payments including tenure requirements"""
    try:
        summary = await PlanService.get_user_debt_summary(current_user.clerk_user_id)
        
        is_valid = monthly_budget >= summary["monthly_minimums"]
        excess_budget = monthly_budget - summary["monthly_minimums"] if is_valid else 0
        shortage = summary["monthly_minimums"] - monthly_budget if not is_valid else 0
        
        # Build detailed message
        message = ""
        if is_valid:
            message = "Budget covers all minimum payments"
            if summary.get("has_tenure_debts"):
                message += " including required EMIs for fixed-term loans"
        else:
            message = f"Budget is ₹{shortage:,.0f} short of minimum requirements"
            if summary.get("has_tenure_debts"):
                message += ". Some debts have fixed tenure requirements that cannot be met with this budget."
        
        return {
            "is_valid": is_valid,
            "monthly_budget": monthly_budget,
            "minimum_required": summary["monthly_minimums"],
            "excess_budget": excess_budget,
            "shortage": shortage,
            "has_tenure_debts": summary.get("has_tenure_debts", False),
            "message": message,
            "warning": "You have fixed-term loans that must be paid within their tenure" if summary.get("has_tenure_debts") else None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate budget: {str(e)}"
        )

@router.get("/tenure-analysis")
async def get_tenure_analysis(
    current_user: User = Depends(get_current_user)
):
    """Get detailed analysis of tenure constraints"""
    try:
        summary = await PlanService.get_user_debt_summary(current_user.clerk_user_id)
        
        tenure_debts = [
            debt for debt in summary["debts"] 
            if debt.get("loan_type") == "fixed_term" and debt.get("remaining_months")
        ]
        
        if not tenure_debts:
            return {
                "has_tenure_debts": False,
                "message": "No fixed-term loans with tenure constraints",
                "tenure_debts": []
            }
        
        total_required_emi = sum(debt.get("required_emi", 0) for debt in tenure_debts)
        
        tenure_analysis = []
        for debt in tenure_debts:
            tenure_analysis.append({
                "name": debt["name"],
                "balance": debt["balance"],
                "remaining_months": debt["remaining_months"],
                "required_emi": debt["required_emi"],
                "total_to_pay": debt["required_emi"] * debt["remaining_months"],
                "apr": debt["apr"]
            })
        
        return {
            "has_tenure_debts": True,
            "tenure_debt_count": len(tenure_debts),
            "total_required_emi": total_required_emi,
            "available_budget": summary["available_budget"],
            "budget_sufficient": summary["available_budget"] >= total_required_emi,
            "tenure_debts": tenure_analysis,
            "message": f"You have {len(tenure_debts)} fixed-term loan(s) requiring ₹{total_required_emi:,.0f}/month minimum"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze tenure: {str(e)}"
        )