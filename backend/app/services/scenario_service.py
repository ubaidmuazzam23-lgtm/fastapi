from typing import List, Dict, Any
from app.models.debt import Debt
from app.models.user import User
from app.core.schemas import Debt as CoreDebt
from app.core.optimization import (
    compute_avalanche_plan,
    compute_snowball_plan,
    one_step_optimal_allocation
)
from app.core.plan_utils import simulate_total_balance_series
from app.schemas.scenario import WhatIfRequest, ScenarioComparison, ScenarioType

class ScenarioService:
    @staticmethod
    def _convert_db_debt_to_core(db_debt: Debt) -> CoreDebt:
        """Convert database debt model to core debt model"""
        min_payment = db_debt.min_payment if db_debt.min_payment > 0 else max(
            db_debt.total_amount * (db_debt.interest_rate / 100) / 12 * 0.02,
            50.0
        )
        
        return CoreDebt(
            name=db_debt.name,
            balance=db_debt.total_amount,
            apr=db_debt.interest_rate / 100,
            min_payment=min_payment
        )

    @staticmethod
    def _generate_plan(debts: List[CoreDebt], budget: float, months: int, strategy: str):
        """Generate plan based on strategy"""
        if strategy == "snowball":
            return compute_snowball_plan(debts, budget, months)
        elif strategy == "optimal":
            return one_step_optimal_allocation(debts, budget)
        else:  # avalanche
            return compute_avalanche_plan(debts, budget, months)

    @staticmethod
    async def run_what_if_analysis(
        clerk_user_id: str,
        what_if_request: WhatIfRequest
    ) -> ScenarioComparison:
        """Run what-if scenario analysis"""
        
        # Get user's debts
        user_debts = await Debt.find(
            Debt.clerk_user_id == clerk_user_id,
            Debt.is_active == True
        ).to_list()
        
        if not user_debts:
            raise ValueError("No active debts found for user")
        
        # Convert to core debt objects
        baseline_debts = [ScenarioService._convert_db_debt_to_core(debt) for debt in user_debts]
        scenario_debts = [ScenarioService._convert_db_debt_to_core(debt) for debt in user_debts]
        
        # Generate baseline plan
        baseline_plan = ScenarioService._generate_plan(
            baseline_debts,
            what_if_request.base_budget,
            what_if_request.analysis_months,
            what_if_request.base_strategy
        )
        
        # Modify scenario based on type
        scenario_budget = what_if_request.base_budget
        
        if what_if_request.scenario_type == ScenarioType.EXTRA_PAYMENT:
            scenario_budget += what_if_request.extra_payment or 0
            
        elif what_if_request.scenario_type == ScenarioType.BUDGET_REDUCTION:
            scenario_budget -= what_if_request.budget_reduction or 0
            scenario_budget = max(scenario_budget, sum(d.min_payment for d in scenario_debts))
            
        elif what_if_request.scenario_type == ScenarioType.INTEREST_RATE_CHANGE:
            rate_change = (what_if_request.rate_change_percent or 0) / 100
            affected = what_if_request.affected_debts or []
            
            for debt in scenario_debts:
                if not affected or debt.name in affected or "All" in affected:
                    debt.apr = max(0, debt.apr + rate_change)
                    
        elif what_if_request.scenario_type == ScenarioType.DEBT_CONSOLIDATION:
            total_balance = sum(d.balance for d in scenario_debts)
            consolidation_balance = total_balance + (what_if_request.consolidation_fee or 0)
            consolidation_rate = (what_if_request.consolidation_rate or 12) / 100
            
            scenario_debts = [CoreDebt(
                name="Consolidated Loan",
                balance=consolidation_balance,
                apr=consolidation_rate,
                min_payment=consolidation_balance * consolidation_rate / 12 * 0.02
            )]
            
        elif what_if_request.scenario_type == ScenarioType.WINDFALL:
            # Apply windfall to highest APR debt
            windfall = what_if_request.windfall_amount or 0
            if windfall > 0 and scenario_debts:
                highest_apr_debt = max(scenario_debts, key=lambda d: d.apr)
                highest_apr_debt.balance = max(0, highest_apr_debt.balance - windfall)
        
        # Generate scenario plan
        scenario_plan = ScenarioService._generate_plan(
            scenario_debts,
            scenario_budget,
            what_if_request.analysis_months,
            what_if_request.base_strategy
        )
        
        # Calculate differences
        baseline_interest = sum(m.total_interest for m in baseline_plan.months)
        scenario_interest = sum(m.total_interest for m in scenario_plan.months)
        baseline_months = len(baseline_plan.months)
        scenario_months = len(scenario_plan.months)
        baseline_total = sum(m.total_paid for m in baseline_plan.months)
        scenario_total = sum(m.total_paid for m in scenario_plan.months)
        
        interest_savings = baseline_interest - scenario_interest
        months_saved = baseline_months - scenario_months
        payment_difference = scenario_total - baseline_total
        
        # Generate insights
        insights = []
        
        if months_saved > 0:
            years_saved = months_saved / 12
            insights.append(f"You could be debt-free {months_saved} months ({years_saved:.1f} years) earlier")
        elif months_saved < 0:
            years_longer = abs(months_saved) / 12
            insights.append(f"This scenario extends debt payoff by {abs(months_saved)} months ({years_longer:.1f} years)")
            
        if interest_savings > 1000:
            insights.append(f"Total interest savings: ₹{interest_savings:,.0f}")
        elif interest_savings < -1000:
            insights.append(f"Additional interest cost: ₹{abs(interest_savings):,.0f}")
            
        if what_if_request.scenario_type == ScenarioType.EXTRA_PAYMENT and interest_savings > 0:
            roi = (interest_savings / ((what_if_request.extra_payment or 1) * scenario_months)) * 100
            insights.append(f"ROI: Every extra ₹1 saves ₹{interest_savings/((what_if_request.extra_payment or 1) * scenario_months):.2f}")
            
        # Prepare response data
        baseline_balance_series = simulate_total_balance_series(baseline_debts, baseline_plan)
        scenario_balance_series = simulate_total_balance_series(scenario_debts, scenario_plan)
        
        return ScenarioComparison(
            baseline={
                "months": baseline_months,
                "total_interest": baseline_interest,
                "total_payments": baseline_total,
                "balance_series": baseline_balance_series,
                "plan": baseline_plan
            },
            scenario={
                "months": scenario_months,
                "total_interest": scenario_interest,
                "total_payments": scenario_total,
                "balance_series": scenario_balance_series,
                "plan": scenario_plan
            },
            interest_savings=interest_savings,
            months_saved=months_saved,
            payment_difference=payment_difference,
            insights=insights
        )