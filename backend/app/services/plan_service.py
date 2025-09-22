from typing import List, Optional, Dict, Any
from app.models.debt import Debt
from app.models.user import User
from app.core.schemas import Debt as CoreDebt
from app.core.optimization import (
    compute_avalanche_plan,
    compute_snowball_plan,
    one_step_optimal_allocation
)
from app.core.plan_utils import plan_to_dataframe, simulate_total_balance_series
from app.schemas.plan import (
    RepaymentPlanRequest, RepaymentPlanResponse, 
    StrategyComparisonResponse, AllocationResponse,
    RepaymentMonthResponse, StrategyType
)

class PlanService:
    @staticmethod
    def _convert_db_debt_to_core(db_debt: Debt) -> CoreDebt:
        """Convert database debt model to core debt model"""
        return CoreDebt(
            name=db_debt.name,
            balance=db_debt.total_amount,
            apr=db_debt.interest_rate / 100,  # Convert percentage to decimal
            min_payment=db_debt.total_amount * (db_debt.interest_rate / 100) / 12 * 0.02  # Rough estimate
        )

    @staticmethod
    def _convert_core_plan_to_response(plan, strategy_name: str, initial_debts: List[CoreDebt]) -> RepaymentPlanResponse:
        """Convert core repayment plan to API response"""
        # Convert schedule to DataFrame-like structure
        df = plan_to_dataframe(plan)
        schedule_data = df.to_dict('records') if not df.empty else []
        
        # Generate balance series
        balance_series = simulate_total_balance_series(initial_debts, plan)
        
        # Convert months
        months_response = []
        for month in plan.months:
            allocations = [
                AllocationResponse(
                    name=alloc.name,
                    payment=alloc.payment,
                    interest_accrued=alloc.interest_accrued,
                    principal_reduction=alloc.principal_reduction
                )
                for alloc in month.allocations
            ]
            
            months_response.append(RepaymentMonthResponse(
                month_index=month.month_index,
                allocations=allocations,
                total_interest=month.total_interest,
                total_paid=month.total_paid
            ))
        
        return RepaymentPlanResponse(
            strategy_name=strategy_name,
            months=months_response,
            total_interest_paid=plan.total_interest_paid,
            months_to_debt_free=plan.months_to_debt_free,
            schedule_df=schedule_data,
            balance_series=balance_series
        )

    @staticmethod
    async def generate_repayment_plan(
        clerk_user_id: str, 
        plan_request: RepaymentPlanRequest
    ) -> RepaymentPlanResponse:
        """Generate repayment plan for user's actual debts"""
        # Get user's debts
        user_debts = await Debt.find(
            Debt.clerk_user_id == clerk_user_id,
            Debt.is_active == True
        ).to_list()
        
        if not user_debts:
            raise ValueError("No active debts found for user")
        
        # Convert to core debt objects
        core_debts = [PlanService._convert_db_debt_to_core(debt) for debt in user_debts]
        
        # Generate plan based on strategy
        if plan_request.strategy == StrategyType.AVALANCHE:
            plan = compute_avalanche_plan(core_debts, plan_request.monthly_budget, plan_request.max_months)
            strategy_name = "Debt Avalanche"
        elif plan_request.strategy == StrategyType.SNOWBALL:
            plan = compute_snowball_plan(core_debts, plan_request.monthly_budget, plan_request.max_months)
            strategy_name = "Debt Snowball"
        else:  # OPTIMAL
            plan = one_step_optimal_allocation(core_debts, plan_request.monthly_budget)
            strategy_name = "Mathematical Optimal"
        
        return PlanService._convert_core_plan_to_response(plan, strategy_name, core_debts)

    @staticmethod
    async def compare_all_strategies(
        clerk_user_id: str, 
        monthly_budget: float, 
        max_months: int = 60
    ) -> StrategyComparisonResponse:
        """Generate all three strategies and compare them"""
        # Get user's debts
        user_debts = await Debt.find(
            Debt.clerk_user_id == clerk_user_id,
            Debt.is_active == True
        ).to_list()
        
        if not user_debts:
            raise ValueError("No active debts found for user")
        
        # Convert to core debt objects
        core_debts = [PlanService._convert_db_debt_to_core(debt) for debt in user_debts]
        
        # Generate all plans
        avalanche_plan = compute_avalanche_plan(core_debts, monthly_budget, max_months)
        snowball_plan = compute_snowball_plan(core_debts, monthly_budget, max_months)
        optimal_plan = one_step_optimal_allocation(core_debts, monthly_budget)
        
        # Convert to responses
        avalanche_response = PlanService._convert_core_plan_to_response(avalanche_plan, "Debt Avalanche", core_debts)
        snowball_response = PlanService._convert_core_plan_to_response(snowball_plan, "Debt Snowball", core_debts)
        optimal_response = PlanService._convert_core_plan_to_response(optimal_plan, "Mathematical Optimal", core_debts)
        
        # Determine best strategy (lowest total interest)
        strategies = [
            ("avalanche", avalanche_response.total_interest_paid),
            ("snowball", snowball_response.total_interest_paid),
            ("optimal", optimal_response.total_interest_paid)
        ]
        best_strategy = min(strategies, key=lambda x: x[1])[0]
        
        return StrategyComparisonResponse(
            avalanche=avalanche_response,
            snowball=snowball_response,
            optimal=optimal_response,
            best_strategy=best_strategy
        )

    @staticmethod
    async def get_user_debt_summary(clerk_user_id: str) -> Dict[str, Any]:
        """Get debt summary for planning interface"""
        user_debts = await Debt.find(
            Debt.clerk_user_id == clerk_user_id,
            Debt.is_active == True
        ).to_list()
        
        user = await User.find_one(User.clerk_user_id == clerk_user_id)
        
        if not user_debts:
            return {
                "total_debt": 0,
                "monthly_minimums": 0,
                "weighted_apr": 0,
                "debt_count": 0,
                "available_budget": getattr(user, 'monthly_income', 0) - getattr(user, 'monthly_expenses', 0),
                "debts": []
            }
        
        total_debt = sum(debt.total_amount for debt in user_debts)
        monthly_minimums = sum(debt.total_amount * (debt.interest_rate / 100) / 12 * 0.02 for debt in user_debts)
        weighted_apr = sum(debt.interest_rate * debt.total_amount for debt in user_debts) / total_debt if total_debt > 0 else 0
        available_budget = getattr(user, 'monthly_income', 0) - getattr(user, 'monthly_expenses', 0)
        
        debt_summaries = []
        for debt in user_debts:
            debt_summaries.append({
                "id": str(debt.id),
                "name": debt.name,
                "balance": debt.total_amount,
                "apr": debt.interest_rate,
                "monthly_interest": debt.total_amount * (debt.interest_rate / 100) / 12
            })
        
        return {
            "total_debt": total_debt,
            "monthly_minimums": monthly_minimums,
            "weighted_apr": weighted_apr,
            "debt_count": len(user_debts),
            "available_budget": available_budget,
            "debts": debt_summaries
        }