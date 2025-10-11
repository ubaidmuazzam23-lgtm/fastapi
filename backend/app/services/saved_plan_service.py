from typing import List, Optional, Dict, Any
from beanie import PydanticObjectId
from app.models.saved_plan import SavedPlan, MonthlyPayment, PaymentStatus
from app.models.payment_history import PaymentHistory
from app.models.debt import Debt
from app.schemas.saved_plan import SavePlanRequest, MarkPaymentRequest
from datetime import datetime

class SavedPlanService:
    @staticmethod
    async def save_plan(clerk_user_id: str, request: SavePlanRequest) -> SavedPlan:
        """Save a generated repayment plan"""
        print(f"DEBUG: Saving plan for user: {clerk_user_id}")
        
        plan_data = request.plan_data
        
        # Convert monthly data to MonthlyPayment objects
        monthly_payments = []
        for month in plan_data.get('months', []):
            monthly_payments.append(MonthlyPayment(
                month_index=month['month_index'],
                status=PaymentStatus.PENDING,
                allocations=month['allocations'],
                total_paid=month['total_paid'],
                total_interest=month['total_interest']
            ))
        
        # Calculate original total debt
        user_debts = await Debt.find(
            Debt.clerk_user_id == clerk_user_id,
            Debt.is_active == True
        ).to_list()
        original_total_debt = sum(debt.total_amount for debt in user_debts)
        
        saved_plan = SavedPlan(
            clerk_user_id=clerk_user_id,
            plan_name=request.plan_name,
            strategy=plan_data['strategy_name'],
            monthly_budget=plan_data.get('monthly_budget', 0),
            total_interest_paid=plan_data['total_interest_paid'],
            months_to_debt_free=plan_data['months_to_debt_free'],
            original_total_debt=original_total_debt,
            monthly_payments=monthly_payments,
            current_month=0,
            completed_months=0
        )
        
        await saved_plan.insert()
        print(f"DEBUG: Plan saved successfully with ID: {saved_plan.id}")
        print(f"DEBUG: Plan name: {saved_plan.plan_name}, User: {saved_plan.clerk_user_id}")
        
        return saved_plan
    
    @staticmethod
    async def get_user_plans(clerk_user_id: str, active_only: bool = True) -> List[SavedPlan]:
        """Get all saved plans for a user"""
        print(f"DEBUG: Fetching plans for user: {clerk_user_id}")
        print(f"DEBUG: Active only: {active_only}")
        
        if active_only:
            plans = await SavedPlan.find(
                SavedPlan.clerk_user_id == clerk_user_id,
                SavedPlan.is_active == True
            ).to_list()
        else:
            plans = await SavedPlan.find(
                SavedPlan.clerk_user_id == clerk_user_id
            ).to_list()
        
        print(f"DEBUG: Found {len(plans)} plans for user {clerk_user_id}")
        for plan in plans:
            print(f"DEBUG:   - Plan: {plan.plan_name}, ID: {plan.id}, Active: {plan.is_active}, Completed: {plan.is_completed}")
        
        return plans
    
    @staticmethod
    async def get_plan_by_id(plan_id: str, clerk_user_id: str) -> Optional[SavedPlan]:
        """Get a specific saved plan"""
        try:
            plan = await SavedPlan.find_one({
                "_id": PydanticObjectId(plan_id),
                "clerk_user_id": clerk_user_id
            })
            return plan
        except:
            return None
    
    @staticmethod
    async def mark_payment_complete(
        plan_id: str, 
        clerk_user_id: str, 
        request: MarkPaymentRequest
    ) -> Optional[SavedPlan]:
        """Mark a monthly payment as complete and update debt balances"""
        plan = await SavedPlanService.get_plan_by_id(plan_id, clerk_user_id)
        if not plan:
            return None
        
        # Find the payment in the monthly_payments list
        payment_index = next(
            (i for i, p in enumerate(plan.monthly_payments) 
             if p.month_index == request.month_index),
            None
        )
        
        if payment_index is None:
            return None
        
        payment = plan.monthly_payments[payment_index]
        
        # Update payment status
        payment.status = PaymentStatus.PAID
        payment.paid_date = request.payment_date or datetime.utcnow()
        payment.notes = request.notes
        
        # Update plan tracking
        plan.completed_months += 1
        plan.current_month = request.month_index + 1
        
        # Check if plan is completed
        if plan.completed_months >= plan.months_to_debt_free:
            plan.is_completed = True
        
        plan.updated_at = datetime.utcnow()
        await plan.save()
        
        # Update actual debt balances and create payment history
        for allocation in payment.allocations:
            debt_name = allocation['name']
            principal_reduction = allocation['principal_reduction']
            
            # Find the debt by name
            debt = await Debt.find_one({
                "clerk_user_id": clerk_user_id,
                "name": debt_name,
                "is_active": True
            })
            
            if debt:
                # Reduce debt balance
                debt.total_amount = max(0, debt.total_amount - principal_reduction)
                debt.updated_at = datetime.utcnow()
                
                # Mark debt as inactive if fully paid
                if debt.total_amount <= 0.01:  # Allow for rounding errors
                    debt.is_active = False
                
                await debt.save()
                
                # Create payment history record
                history = PaymentHistory(
                    clerk_user_id=clerk_user_id,
                    saved_plan_id=str(plan.id),
                    debt_id=str(debt.id),
                    month_index=request.month_index,
                    payment_amount=allocation['payment'],
                    interest_amount=allocation['interest_accrued'],
                    principal_amount=principal_reduction,
                    remaining_balance=debt.total_amount,
                    payment_date=payment.paid_date,
                    notes=request.notes
                )
                await history.insert()
        
        return plan
    
    @staticmethod
    async def get_payment_history(
        clerk_user_id: str, 
        debt_id: Optional[str] = None
    ) -> List[PaymentHistory]:
        """Get payment history for a user or specific debt"""
        query = {"clerk_user_id": clerk_user_id}
        if debt_id:
            query["debt_id"] = debt_id
        
        history = await PaymentHistory.find(query).sort("-payment_date").to_list()
        return history
    
    @staticmethod
    async def delete_plan(plan_id: str, clerk_user_id: str) -> bool:
        """Soft delete a saved plan"""
        plan = await SavedPlanService.get_plan_by_id(plan_id, clerk_user_id)
        if not plan:
            return False
        
        plan.is_active = False
        plan.updated_at = datetime.utcnow()
        await plan.save()
        return True