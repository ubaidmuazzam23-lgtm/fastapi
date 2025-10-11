from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
from app.models.user import User
from app.schemas.saved_plan import (
    SavePlanRequest, SavedPlanResponse, MarkPaymentRequest,
    MonthlyPaymentResponse, PaymentStatus
)
from app.services.saved_plan_service import SavedPlanService
from app.api.dependencies import get_current_user
from datetime import datetime
import asyncio

router = APIRouter(prefix="/saved-plans", tags=["saved-plans"])

@router.post("/", response_model=SavedPlanResponse)
async def save_repayment_plan(
    request: Request,
    save_request: SavePlanRequest,
    current_user: User = Depends(get_current_user)
):
    """Save a generated repayment plan"""
    print(f"DEBUG: POST /saved-plans/ called by user: {current_user.clerk_user_id}")
    
    try:
        plan = await SavedPlanService.save_plan(
            current_user.clerk_user_id, 
            save_request
        )
        
        # Calculate progress percentage
        progress = (plan.completed_months / plan.months_to_debt_free * 100) if plan.months_to_debt_free > 0 else 0
        
        # Prepare plan data for PDF and email
        plan_data_for_email = {
            'plan_name': plan.plan_name,
            'strategy': plan.strategy,
            'monthly_budget': plan.monthly_budget,
            'total_interest_paid': plan.total_interest_paid,
            'months_to_debt_free': plan.months_to_debt_free,
            'original_total_debt': plan.original_total_debt,
            'monthly_payments': [
                {
                    'month_index': p.month_index,
                    'total_paid': p.total_paid,
                    'total_interest': p.total_interest,
                    'allocations': p.allocations
                }
                for p in plan.monthly_payments
            ]
        }
        
        # Send email with PDF (background task)
        from app.services.notification_service import NotificationService
        asyncio.create_task(NotificationService.send_plan_saved_email(
            user_id=current_user.clerk_user_id,
            user_name=current_user.first_name or "User",
            plan_data=plan_data_for_email
        ))
        
        return SavedPlanResponse(
            id=str(plan.id),
            plan_name=plan.plan_name,
            strategy=plan.strategy,
            monthly_budget=plan.monthly_budget,
            total_interest_paid=plan.total_interest_paid,
            months_to_debt_free=plan.months_to_debt_free,
            original_total_debt=plan.original_total_debt,
            current_month=plan.current_month,
            completed_months=plan.completed_months,
            progress_percentage=progress,
            is_completed=plan.is_completed,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
            monthly_payments=[
                MonthlyPaymentResponse(
                    month_index=p.month_index,
                    status=p.status,
                    due_date=p.due_date,
                    paid_date=p.paid_date,
                    total_paid=p.total_paid,
                    total_interest=p.total_interest,
                    allocations=p.allocations,
                    notes=p.notes
                )
                for p in plan.monthly_payments
            ]
        )
    except Exception as e:
        print(f"DEBUG ERROR: Failed to save plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save plan: {str(e)}"
        )

@router.get("/", response_model=List[SavedPlanResponse])
async def get_saved_plans(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get all saved plans for the user"""
    print(f"DEBUG: GET /saved-plans/ called by user: {current_user.clerk_user_id}")
    
    try:
        plans = await SavedPlanService.get_user_plans(current_user.clerk_user_id)
        
        print(f"DEBUG: Returning {len(plans)} plans")
        
        result = []
        for plan in plans:
            result.append(SavedPlanResponse(
                id=str(plan.id),
                plan_name=plan.plan_name,
                strategy=plan.strategy,
                monthly_budget=plan.monthly_budget,
                total_interest_paid=plan.total_interest_paid,
                months_to_debt_free=plan.months_to_debt_free,
                original_total_debt=plan.original_total_debt,
                current_month=plan.current_month,
                completed_months=plan.completed_months,
                progress_percentage=(plan.completed_months / plan.months_to_debt_free * 100) if plan.months_to_debt_free > 0 else 0,
                is_completed=plan.is_completed,
                created_at=plan.created_at,
                updated_at=plan.updated_at,
                monthly_payments=[
                    MonthlyPaymentResponse(
                        month_index=p.month_index,
                        status=p.status,
                        due_date=p.due_date,
                        paid_date=p.paid_date,
                        total_paid=p.total_paid,
                        total_interest=p.total_interest,
                        allocations=p.allocations,
                        notes=p.notes
                    )
                    for p in plan.monthly_payments
                ]
            ))
        
        return result
    except Exception as e:
        print(f"DEBUG ERROR: Failed to get saved plans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get saved plans: {str(e)}"
        )

@router.get("/{plan_id}", response_model=SavedPlanResponse)
async def get_saved_plan(
    plan_id: str,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get a specific saved plan"""
    plan = await SavedPlanService.get_plan_by_id(plan_id, current_user.clerk_user_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    return SavedPlanResponse(
        id=str(plan.id),
        plan_name=plan.plan_name,
        strategy=plan.strategy,
        monthly_budget=plan.monthly_budget,
        total_interest_paid=plan.total_interest_paid,
        months_to_debt_free=plan.months_to_debt_free,
        original_total_debt=plan.original_total_debt,
        current_month=plan.current_month,
        completed_months=plan.completed_months,
        progress_percentage=(plan.completed_months / plan.months_to_debt_free * 100) if plan.months_to_debt_free > 0 else 0,
        is_completed=plan.is_completed,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
        monthly_payments=[
            MonthlyPaymentResponse(
                month_index=p.month_index,
                status=p.status,
                due_date=p.due_date,
                paid_date=p.paid_date,
                total_paid=p.total_paid,
                total_interest=p.total_interest,
                allocations=p.allocations,
                notes=p.notes
            )
            for p in plan.monthly_payments
        ]
    )

@router.post("/{plan_id}/mark-payment", response_model=SavedPlanResponse)
async def mark_payment_complete(
    plan_id: str,
    mark_request: MarkPaymentRequest,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Mark a monthly payment as complete"""
    print(f"DEBUG: Marking payment complete - Plan: {plan_id}, Month: {mark_request.month_index}")
    
    try:
        plan = await SavedPlanService.mark_payment_complete(
            plan_id,
            current_user.clerk_user_id,
            mark_request
        )
        
        if not plan:
            raise HTTPException(status_code=404, detail="Plan or payment not found")
        
        # Prepare payment data for email
        completed_payment = plan.monthly_payments[mark_request.month_index]
        payment_data_for_email = {
            'plan_name': plan.plan_name,
            'month_index': mark_request.month_index,
            'payment_date': completed_payment.paid_date.strftime('%B %d, %Y') if completed_payment.paid_date else datetime.now().strftime('%B %d, %Y'),
            'total_paid': completed_payment.total_paid,
            'total_interest': completed_payment.total_interest,
            'allocations': completed_payment.allocations,
            'completed_months': plan.completed_months,
            'total_months': plan.months_to_debt_free,
            'progress_percentage': (plan.completed_months / plan.months_to_debt_free * 100) if plan.months_to_debt_free > 0 else 0
        }
        
        # Send receipt email with PDF (background task)
        from app.services.notification_service import NotificationService
        asyncio.create_task(NotificationService.send_payment_receipt_email(
            user_id=current_user.clerk_user_id,
            user_name=current_user.first_name or "User",
            payment_data=payment_data_for_email
        ))
        
        return SavedPlanResponse(
            id=str(plan.id),
            plan_name=plan.plan_name,
            strategy=plan.strategy,
            monthly_budget=plan.monthly_budget,
            total_interest_paid=plan.total_interest_paid,
            months_to_debt_free=plan.months_to_debt_free,
            original_total_debt=plan.original_total_debt,
            current_month=plan.current_month,
            completed_months=plan.completed_months,
            progress_percentage=(plan.completed_months / plan.months_to_debt_free * 100) if plan.months_to_debt_free > 0 else 0,
            is_completed=plan.is_completed,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
            monthly_payments=[
                MonthlyPaymentResponse(
                    month_index=p.month_index,
                    status=p.status,
                    due_date=p.due_date,
                    paid_date=p.paid_date,
                    total_paid=p.total_paid,
                    total_interest=p.total_interest,
                    allocations=p.allocations,
                    notes=p.notes
                )
                for p in plan.monthly_payments
            ]
        )
    except Exception as e:
        print(f"DEBUG ERROR: Failed to mark payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark payment: {str(e)}"
        )

@router.delete("/{plan_id}")
async def delete_saved_plan(
    plan_id: str,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Delete a saved plan"""
    success = await SavedPlanService.delete_plan(plan_id, current_user.clerk_user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"message": "Plan deleted successfully"}