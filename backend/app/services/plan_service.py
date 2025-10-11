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
        # Get loan type with backward compatibility
        loan_type = getattr(db_debt, 'loan_type', 'revolving')
        
        # Get tenure fields with backward compatibility
        original_tenure_months = getattr(db_debt, 'original_tenure_months', None)
        remaining_months = getattr(db_debt, 'remaining_months', None)
        fixed_emi = getattr(db_debt, 'fixed_emi', None)
        
        # Calculate proper minimum payment based on loan type
        if loan_type == "fixed_term" and remaining_months and remaining_months > 0:
            # Use the debt's calculate_required_emi method if available
            if hasattr(db_debt, 'calculate_required_emi'):
                min_payment = db_debt.calculate_required_emi()
            else:
                # Fallback EMI calculation
                P = db_debt.total_amount
                r = (db_debt.interest_rate / 100) / 12
                n = remaining_months
                if r > 0:
                    min_payment = P * r * (1 + r)**n / ((1 + r)**n - 1)
                else:
                    min_payment = P / n
        else:
            # Use stored min_payment or calculate rough estimate for revolving credit
            min_payment = getattr(db_debt, 'min_payment', 0)
            if min_payment == 0:
                min_payment = db_debt.total_amount * (db_debt.interest_rate / 100) / 12 * 0.02
        
        return CoreDebt(
            name=db_debt.name,
            balance=db_debt.total_amount,
            apr=db_debt.interest_rate / 100,  # Convert percentage to decimal
            min_payment=min_payment,
            loan_type=loan_type,
            original_tenure_months=original_tenure_months,
            remaining_months=remaining_months,
            fixed_emi=fixed_emi
        )

    @staticmethod
    def _convert_core_plan_to_response(plan, strategy_name: str, initial_debts: List[CoreDebt]) -> RepaymentPlanResponse:
        """Convert core repayment plan to API response"""
        # Check for errors from optimization - use getattr for safety
        plan_error = getattr(plan, 'error', None)
        if plan_error:
            return RepaymentPlanResponse(
                strategy_name=strategy_name,
                months=[],
                total_interest_paid=plan.total_interest_paid,
                months_to_debt_free=plan.months_to_debt_free,
                schedule_df=[],
                balance_series=[],
                error=plan_error
            )
        
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
            balance_series=balance_series,
            error=getattr(plan, 'error', None)  # Use getattr for safety
        )

    @staticmethod
    async def generate_repayment_plan(
        clerk_user_id: str, 
        plan_request: RepaymentPlanRequest
    ) -> RepaymentPlanResponse:
        """Generate repayment plan for user's actual debts"""
        try:
            # Get user's debts
            user_debts = await Debt.find(
                Debt.clerk_user_id == clerk_user_id,
                Debt.is_active == True
            ).to_list()
            
            if not user_debts:
                raise ValueError("No active debts found for user")
            
            # DEBUG: Print what we got from database
            print(f"DEBUG: Found {len(user_debts)} debts")
            for debt in user_debts:
                print(f"  - {debt.name}: has loan_type? {hasattr(debt, 'loan_type')}")
                print(f"    loan_type value: {getattr(debt, 'loan_type', 'NOT FOUND')}")
            
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
        
        except Exception as e:
            print(f"ERROR in generate_repayment_plan: {e}")
            import traceback
            traceback.print_exc()
            raise

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
        
        # Determine best strategy (lowest total interest, no errors)
        strategies = []
        if not avalanche_response.error:
            strategies.append(("avalanche", avalanche_response.total_interest_paid))
        if not snowball_response.error:
            strategies.append(("snowball", snowball_response.total_interest_paid))
        if not optimal_response.error:
            strategies.append(("optimal", optimal_response.total_interest_paid))
        
        best_strategy = min(strategies, key=lambda x: x[1])[0] if strategies else "none"
        
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
        
        # Handle case where user doesn't exist
        if not user:
            return {
                "total_debt": 0,
                "monthly_minimums": 0,
                "weighted_apr": 0,
                "debt_count": 0,
                "available_budget": 0,
                "debts": [],
                "has_tenure_debts": False,
                "budget_sufficient": True
            }
        
        if not user_debts:
            return {
                "total_debt": 0,
                "monthly_minimums": 0,
                "weighted_apr": 0,
                "debt_count": 0,
                "available_budget": getattr(user, 'monthly_income', 0) - getattr(user, 'monthly_expenses', 0),
                "debts": [],
                "has_tenure_debts": False
            }
        
        total_debt = sum(debt.total_amount for debt in user_debts)
        
        # Calculate monthly minimums including tenure requirements
        monthly_minimums = 0.0
        has_tenure_debts = False
        for debt in user_debts:
            # CRITICAL: Use getattr for backward compatibility
            loan_type = getattr(debt, 'loan_type', 'revolving')
            remaining_months = getattr(debt, 'remaining_months', None)
            
            if loan_type == "fixed_term" and remaining_months and remaining_months > 0:
                # Calculate EMI for fixed-term loan
                if hasattr(debt, 'calculate_required_emi'):
                    monthly_minimums += debt.calculate_required_emi()
                else:
                    # Fallback calculation
                    P = debt.total_amount
                    r = (debt.interest_rate / 100) / 12
                    n = remaining_months
                    if r > 0:
                        emi = P * r * (1 + r)**n / ((1 + r)**n - 1)
                    else:
                        emi = P / n
                    monthly_minimums += emi
                has_tenure_debts = True
            else:
                # Revolving credit
                min_pay = getattr(debt, 'min_payment', 0)
                if min_pay == 0:
                    min_pay = debt.total_amount * (debt.interest_rate / 100) / 12 * 0.02
                monthly_minimums += min_pay
        
        weighted_apr = sum(debt.interest_rate * debt.total_amount for debt in user_debts) / total_debt if total_debt > 0 else 0
        available_budget = getattr(user, 'monthly_income', 0) - getattr(user, 'monthly_expenses', 0)
        
        debt_summaries = []
        for debt in user_debts:
            # CRITICAL: Use getattr for all new fields
            loan_type = getattr(debt, 'loan_type', 'revolving')
            remaining_months = getattr(debt, 'remaining_months', None)
            
            required_emi = None
            if loan_type == "fixed_term" and remaining_months:
                if hasattr(debt, 'calculate_required_emi'):
                    required_emi = debt.calculate_required_emi()
                else:
                    # Fallback calculation
                    P = debt.total_amount
                    r = (debt.interest_rate / 100) / 12
                    n = remaining_months
                    if r > 0:
                        required_emi = P * r * (1 + r)**n / ((1 + r)**n - 1)
                    else:
                        required_emi = P / n
            
            debt_summaries.append({
                "id": str(debt.id),
                "name": debt.name,
                "balance": debt.total_amount,
                "apr": debt.interest_rate,
                "monthly_interest": debt.total_amount * (debt.interest_rate / 100) / 12,
                "loan_type": loan_type,
                "remaining_months": remaining_months,
                "required_emi": required_emi
            })
        
        return {
            "total_debt": total_debt,
            "monthly_minimums": monthly_minimums,
            "weighted_apr": weighted_apr,
            "debt_count": len(user_debts),
            "available_budget": available_budget,
            "debts": debt_summaries,
            "has_tenure_debts": has_tenure_debts,
            "budget_sufficient": available_budget >= monthly_minimums
        }