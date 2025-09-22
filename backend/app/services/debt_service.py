from typing import List, Optional
from beanie import PydanticObjectId
from app.models.debt import Debt
from app.models.user import User
from app.schemas.debt import DebtCreate, DebtUpdate
from datetime import datetime

class DebtService:
    
    @staticmethod
    async def create_debt(clerk_user_id: str, debt_data: DebtCreate) -> Debt:
        """Create a new debt for a user"""
        debt = Debt(
            clerk_user_id=clerk_user_id,
            **debt_data.model_dump()
        )
        await debt.insert()
        return debt
    
    @staticmethod
    async def get_user_debts(clerk_user_id: str, active_only: bool = True) -> List[Debt]:
        """Get all debts for a user"""
        query = {"clerk_user_id": clerk_user_id}
        if active_only:
            query["is_active"] = True
        
        debts = await Debt.find(query).to_list()
        return debts
    
    @staticmethod
    async def get_debt_by_id(debt_id: str, clerk_user_id: str) -> Optional[Debt]:
        """Get a specific debt by ID for a user"""
        try:
            debt = await Debt.find_one({
                "_id": PydanticObjectId(debt_id),
                "clerk_user_id": clerk_user_id,
                "is_active": True
            })
            return debt
        except:
            return None
    
    @staticmethod
    async def update_debt(debt_id: str, clerk_user_id: str, debt_data: DebtUpdate) -> Optional[Debt]:
        """Update a debt"""
        debt = await DebtService.get_debt_by_id(debt_id, clerk_user_id)
        if not debt:
            return None
        
        update_data = debt_data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(debt, field, value)
        
        await debt.save()
        return debt
    
    @staticmethod
    async def delete_debt(debt_id: str, clerk_user_id: str) -> bool:
        """Soft delete a debt"""
        debt = await DebtService.get_debt_by_id(debt_id, clerk_user_id)
        if not debt:
            return False
        
        debt.is_active = False
        debt.updated_at = datetime.utcnow()
        await debt.save()
        return True
    
    @staticmethod
    async def get_debt_summary_with_profile(clerk_user_id: str) -> dict:
        """Get debt summary combined with user's financial profile"""
        # Get user's financial profile
        user = await User.find_one({"clerk_user_id": clerk_user_id})
        if not user:
            return {"error": "User not found"}
        
        # Get user's debts
        debts = await DebtService.get_user_debts(clerk_user_id)
        
        # Calculate debt metrics
        total_debt_amount = sum(debt.total_amount for debt in debts)
        total_monthly_interest = sum(debt.calculate_monthly_interest() for debt in debts)
        
        # Calculate available budget
        available_budget = user.monthly_income - user.monthly_expenses
        debt_to_income_ratio = (total_monthly_interest / user.monthly_income * 100) if user.monthly_income > 0 else 0
        
        return {
            "user_profile": {
                "monthly_income": user.monthly_income,
                "monthly_expenses": user.monthly_expenses,
                "available_budget": available_budget
            },
            "debt_summary": {
                "total_debt_amount": total_debt_amount,
                "total_monthly_interest": total_monthly_interest,
                "debt_count": len(debts),
                "debt_to_income_ratio": debt_to_income_ratio,
                "average_interest_rate": sum(debt.interest_rate for debt in debts) / len(debts) if debts else 0
            },
            "debts": [debt.to_dict() for debt in debts]
        }