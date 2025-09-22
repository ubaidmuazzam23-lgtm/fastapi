from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List

from app.models.user import User
from app.models.debt import Debt
from app.schemas.debt import DebtCreate, DebtUpdate, DebtResponse, UserFinancialProfile
from app.services.debt_service import DebtService
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/debt", tags=["debt-management"])

@router.post("/financial-profile")
async def update_financial_profile(
    request: Request,
    profile_data: UserFinancialProfile,
    current_user: User = Depends(get_current_user)
):
    """Update user's financial profile"""
    try:
        current_user.monthly_income = profile_data.monthly_income
        current_user.monthly_expenses = profile_data.monthly_expenses
        await current_user.save()
        return {"message": "Financial profile updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/financial-profile")
async def get_financial_profile(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get user's financial profile"""
    # Handle case where user doesn't have these fields set
    monthly_income = getattr(current_user, 'monthly_income', 0.0)
    monthly_expenses = getattr(current_user, 'monthly_expenses', 0.0)
    
    print(f"Getting financial profile for user {current_user.clerk_user_id}")
    print(f"Monthly income: {monthly_income}, Monthly expenses: {monthly_expenses}")
    
    return {
        "monthly_income": float(monthly_income),
        "monthly_expenses": float(monthly_expenses)
    }

@router.post("/", response_model=DebtResponse)
async def create_debt(
    request: Request,
    debt_data: DebtCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new debt"""
    try:
        debt = await DebtService.create_debt(current_user.clerk_user_id, debt_data)
        return DebtResponse(**debt.to_dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[DebtResponse])
async def get_user_debts(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get all user debts"""
    debts = await DebtService.get_user_debts(current_user.clerk_user_id)
    return [DebtResponse(**debt.to_dict()) for debt in debts]

@router.get("/summary")
async def get_debt_summary(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive debt summary with user profile"""
    try:
        summary = await DebtService.get_debt_summary_with_profile(current_user.clerk_user_id)
        print(f"Debt summary for user {current_user.clerk_user_id}: {summary}")
        return summary
    except Exception as e:
        print(f"Error getting debt summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{debt_id}", response_model=DebtResponse)
async def update_debt(
    debt_id: str,
    debt_data: DebtUpdate,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Update a debt"""
    debt = await DebtService.update_debt(debt_id, current_user.clerk_user_id, debt_data)
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    return DebtResponse(**debt.to_dict())

@router.delete("/{debt_id}")
async def delete_debt(
    debt_id: str,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Delete a debt"""
    success = await DebtService.delete_debt(debt_id, current_user.clerk_user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Debt not found")
    return {"message": "Debt deleted successfully"}