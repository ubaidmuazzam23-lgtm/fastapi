# # core/optimization.py
# from typing import List, Tuple
# from .schemas import Debt, RepaymentPlan, RepaymentMonth, Allocation
# from math import isclose

# def _monthly_rate(apr: float) -> float:
#     return max(0.0, apr) / 12.0

# def _apply_month(debts: List[Debt], allocations: List[Allocation]) -> None:
#     """Apply monthly payments to debts and update balances"""
#     name_to_alloc = {a.name: a for a in allocations}
#     for d in debts:
#         if d.balance <= 0:
#             continue
        
#         alloc = name_to_alloc.get(d.name)
#         if not alloc:
#             continue
            
#         r = _monthly_rate(d.apr)
#         interest = d.balance * r
#         payment = alloc.payment
        
#         # Update debt balance
#         new_balance = d.balance + interest - payment
#         d.balance = max(0.0, new_balance)

# def _is_all_cleared(debts: List[Debt]) -> bool:
#     return all(d.balance <= 0.01 for d in debts)

# def _clone_debts(debts: List[Debt]) -> List[Debt]:
#     return [Debt(**d.model_dump()) for d in debts]

# def _validate_budget_and_aprs(debts: List[Debt], budget: float) -> Tuple[bool, str]:
#     if budget < 0:
#         return False, "Budget cannot be negative."
#     min_total = sum(d.min_payment for d in debts if d.balance > 0)
#     if min_total > 0 and budget < min_total:
#         return False, f"Budget (₹{budget:,.0f}) is less than total minimum payments (₹{min_total:,.0f})."
#     for d in debts:
#         if d.apr is None or d.apr < 0:
#             return False, f"Invalid APR for '{d.name}'."
#     return True, ""

# def compute_avalanche_plan(debts: List[Debt], budget: float, max_months: int) -> RepaymentPlan:
#     """
#     Debt Avalanche: Pay minimums on all debts, then put ALL extra money toward the HIGHEST APR debt
#     """
#     ok, _ = _validate_budget_and_aprs(debts, budget)
#     if not ok:
#         return RepaymentPlan(strategy="avalanche", months=[], total_interest_paid=0.0, months_to_debt_free=0)

#     ds = _clone_debts(debts)
#     months: List[RepaymentMonth] = []
#     month_index = 0
#     total_interest = 0.0

#     while month_index < max_months and not _is_all_cleared(ds):
#         month_index += 1
        
#         # Calculate total minimum payments needed
#         active_debts = [d for d in ds if d.balance > 0]
#         if not active_debts:
#             break
            
#         total_min_payments = sum(d.min_payment for d in active_debts)
#         extra_budget = max(0.0, budget - total_min_payments)
        
#         # Create allocations - start with minimum payments
#         allocations = []
#         for d in ds:
#             if d.balance <= 0:
#                 allocations.append(Allocation(
#                     name=d.name, 
#                     payment=0, 
#                     interest_accrued=0, 
#                     principal_reduction=0
#                 ))
#             else:
#                 r = _monthly_rate(d.apr)
#                 interest = d.balance * r
#                 min_payment = d.min_payment
#                 allocations.append(Allocation(
#                     name=d.name,
#                     payment=min_payment,
#                     interest_accrued=interest,
#                     principal_reduction=max(0.0, min_payment - interest)
#                 ))
        
#         # AVALANCHE STRATEGY: Put ALL extra money on HIGHEST APR debt
#         if extra_budget > 0 and active_debts:
#             # Find the debt with highest APR
#             highest_apr_debt = max(active_debts, key=lambda x: x.apr)
            
#             # Find the allocation for this debt
#             target_alloc = next(a for a in allocations if a.name == highest_apr_debt.name)
            
#             # Calculate max we can pay toward this debt
#             r = _monthly_rate(highest_apr_debt.apr)
#             total_owed_this_month = highest_apr_debt.balance + (highest_apr_debt.balance * r)
#             max_possible_payment = total_owed_this_month
#             current_payment = target_alloc.payment
#             max_extra = max_possible_payment - current_payment
            
#             # Apply the extra budget (or as much as possible)
#             extra_to_apply = min(extra_budget, max_extra)
#             target_alloc.payment += extra_to_apply
#             target_alloc.principal_reduction = max(0.0, target_alloc.payment - target_alloc.interest_accrued)
        
#         # Calculate month totals
#         month_interest = sum(a.interest_accrued for a in allocations)
#         month_total_paid = sum(a.payment for a in allocations)
#         total_interest += month_interest
        
#         # Create month record
#         month = RepaymentMonth(
#             month_index=month_index,
#             allocations=allocations,
#             total_interest=month_interest,
#             total_paid=month_total_paid
#         )
#         months.append(month)
        
#         # Apply payments to debts
#         _apply_month(ds, allocations)

#     return RepaymentPlan(
#         strategy="avalanche", 
#         months=months, 
#         total_interest_paid=total_interest, 
#         months_to_debt_free=month_index
#     )

# def compute_snowball_plan(debts: List[Debt], budget: float, max_months: int) -> RepaymentPlan:
#     """
#     Debt Snowball: Pay minimums on all debts, then put ALL extra money toward the SMALLEST BALANCE debt
#     """
#     ok, _ = _validate_budget_and_aprs(debts, budget)
#     if not ok:
#         return RepaymentPlan(strategy="snowball", months=[], total_interest_paid=0.0, months_to_debt_free=0)

#     ds = _clone_debts(debts)
#     months: List[RepaymentMonth] = []
#     month_index = 0
#     total_interest = 0.0

#     while month_index < max_months and not _is_all_cleared(ds):
#         month_index += 1
        
#         # Calculate total minimum payments needed
#         active_debts = [d for d in ds if d.balance > 0]
#         if not active_debts:
#             break
            
#         total_min_payments = sum(d.min_payment for d in active_debts)
#         extra_budget = max(0.0, budget - total_min_payments)
        
#         # Create allocations - start with minimum payments
#         allocations = []
#         for d in ds:
#             if d.balance <= 0:
#                 allocations.append(Allocation(
#                     name=d.name, 
#                     payment=0, 
#                     interest_accrued=0, 
#                     principal_reduction=0
#                 ))
#             else:
#                 r = _monthly_rate(d.apr)
#                 interest = d.balance * r
#                 min_payment = d.min_payment
#                 allocations.append(Allocation(
#                     name=d.name,
#                     payment=min_payment,
#                     interest_accrued=interest,
#                     principal_reduction=max(0.0, min_payment - interest)
#                 ))
        
#         # SNOWBALL STRATEGY: Put ALL extra money on SMALLEST BALANCE debt
#         if extra_budget > 0 and active_debts:
#             # Find the debt with smallest balance
#             smallest_balance_debt = min(active_debts, key=lambda x: x.balance)
            
#             # Find the allocation for this debt
#             target_alloc = next(a for a in allocations if a.name == smallest_balance_debt.name)
            
#             # Calculate max we can pay toward this debt
#             r = _monthly_rate(smallest_balance_debt.apr)
#             total_owed_this_month = smallest_balance_debt.balance + (smallest_balance_debt.balance * r)
#             max_possible_payment = total_owed_this_month
#             current_payment = target_alloc.payment
#             max_extra = max_possible_payment - current_payment
            
#             # Apply the extra budget (or as much as possible)
#             extra_to_apply = min(extra_budget, max_extra)
#             target_alloc.payment += extra_to_apply
#             target_alloc.principal_reduction = max(0.0, target_alloc.payment - target_alloc.interest_accrued)
        
#         # Calculate month totals
#         month_interest = sum(a.interest_accrued for a in allocations)
#         month_total_paid = sum(a.payment for a in allocations)
#         total_interest += month_interest
        
#         # Create month record
#         month = RepaymentMonth(
#             month_index=month_index,
#             allocations=allocations,
#             total_interest=month_interest,
#             total_paid=month_total_paid
#         )
#         months.append(month)
        
#         # Apply payments to debts
#         _apply_month(ds, allocations)

#     return RepaymentPlan(
#         strategy="snowball", 
#         months=months, 
#         total_interest_paid=total_interest, 
#         months_to_debt_free=month_index
#     )

# def one_step_optimal_allocation(debts: List[Debt], budget: float) -> RepaymentPlan:
#     """
#     One-step optimal allocation using linear programming
#     """
#     ok, _ = _validate_budget_and_aprs(debts, budget)
#     if not ok:
#         return RepaymentPlan(strategy="one_step_optimal", months=[], total_interest_paid=0.0, months_to_debt_free=0)
    
#     try:
#         import pulp as pl
#     except ImportError:
#         # Fallback to avalanche if pulp not available
#         return compute_avalanche_plan(debts, budget, 1)

#     ds = _clone_debts(debts)
#     prob = pl.LpProblem("MinimizeInterest", pl.LpMinimize)
#     pays = {d.name: pl.LpVariable(f"pay_{i}", lowBound=0) for i, d in enumerate(ds)}
#     r = {d.name: _monthly_rate(d.apr) for d in ds}
    
#     # Objective: minimize total interest after payments
#     prob += pl.lpSum(((d.balance + d.balance*r[d.name]) - pays[d.name]) * r[d.name] for d in ds)
    
#     # Constraints
#     prob += pl.lpSum(pays.values()) <= budget  # Budget constraint
    
#     for d in ds:
#         if d.balance > 0:
#             prob += pays[d.name] >= d.min_payment  # Minimum payment constraint
#             prob += pays[d.name] <= d.balance + d.balance*r[d.name]  # Can't pay more than owed
#         else:
#             prob += pays[d.name] == 0  # No payment to paid-off debts
    
#     # Solve
#     prob.solve(pl.PULP_CBC_CMD(msg=False))

#     # Create allocations
#     allocs = []
#     month_interest = 0.0
#     for d in ds:
#         payment = max(0.0, float(pays[d.name].value() or 0))
#         interest = d.balance * r[d.name]
#         month_interest += interest
#         allocs.append(Allocation(
#             name=d.name, 
#             payment=payment, 
#             interest_accrued=interest, 
#             principal_reduction=max(0.0, payment - interest)
#         ))
    
#     # Apply payments
#     _apply_month(ds, allocs)
    
#     plan = RepaymentPlan(
#         strategy="one_step_optimal", 
#         months=[RepaymentMonth(
#             month_index=1, 
#             allocations=allocs, 
#             total_interest=month_interest, 
#             total_paid=sum(a.payment for a in allocs)
#         )], 
#         total_interest_paid=month_interest, 
#         months_to_debt_free=1
#     )
#     return plan


# core/optimization.py
from typing import List, Tuple
from .schemas import Debt, RepaymentPlan, RepaymentMonth, Allocation
from math import isclose

def _monthly_rate(apr: float) -> float:
    return max(0.0, apr) / 12.0

def _apply_month(debts: List[Debt], allocations: List[Allocation]) -> None:
    name_to_alloc = {a.name: a for a in allocations}
    for d in debts:
        if d.balance <= 0:
            continue
        r = _monthly_rate(d.apr)
        interest = d.balance * r
        pay = max(0.0, name_to_alloc.get(d.name, Allocation(name=d.name, payment=0, interest_accrued=0, principal_reduction=0)).payment)
        total_due = d.balance + interest
        pay = min(pay, total_due)
        d.balance = max(0.0, total_due - pay)

def _is_all_cleared(debts: List[Debt]) -> bool:
    return all(d.balance <= 0.01 for d in debts)

def _clone_debts(debts: List[Debt]) -> List[Debt]:
    return [Debt(**d.model_dump()) for d in debts]

def _validate_budget_and_aprs(debts: List[Debt], budget: float) -> Tuple[bool, str]:
    if budget < 0:
        return False, "Budget cannot be negative."
    min_total = sum(d.min_payment for d in debts if d.balance > 0)
    if min_total > 0 and budget < min_total:
        return False, f"Budget (₹{budget:,.0f}) is less than total minimum payments (₹{min_total:,.0f})."
    for d in debts:
        if d.apr is None or d.apr < 0:
            return False, f"Invalid APR for '{d.name}'."
    return True, ""

def compute_avalanche_plan(debts: List[Debt], budget: float, max_months: int) -> RepaymentPlan:
    ok, _ = _validate_budget_and_aprs(debts, budget)
    if not ok:
        return RepaymentPlan(strategy="avalanche", months=[], total_interest_paid=0.0, months_to_debt_free=0)

    ds = _clone_debts(debts)
    months: List[RepaymentMonth] = []
    mi = 0
    total_interest = 0.0

    while mi < max_months and not _is_all_cleared(ds):
        min_total = sum(d.min_payment for d in ds if d.balance > 0)
        remaining = max(0.0, budget - min_total)

        allocs: List[Allocation] = []
        for d in ds:
            if d.balance <= 0:
                allocs.append(Allocation(name=d.name, payment=0, interest_accrued=0, principal_reduction=0))
                continue
            r = _monthly_rate(d.apr)
            interest = d.balance * r
            pay = min(d.balance + interest, d.min_payment)
            allocs.append(Allocation(name=d.name, payment=pay, interest_accrued=interest, principal_reduction=max(0.0, pay - interest)))

        for d in sorted(ds, key=lambda x: (-x.apr, x.balance)):
            if remaining <= 0: break
            if d.balance <= 0: continue
            already = next(a for a in allocs if a.name == d.name).payment
            due = max(0.0, d.balance + (d.balance * _monthly_rate(d.apr)) - already)
            extra = min(remaining, due)
            next(a for a in allocs if a.name == d.name).payment += extra
            remaining -= extra

        month_interest = 0.0
        for a, d in zip(allocs, ds):
            r = _monthly_rate(d.apr)
            a.interest_accrued = d.balance * r
            a.principal_reduction = max(0.0, a.payment - a.interest_accrued)
            month_interest += a.interest_accrued

        total_interest += month_interest
        months.append(RepaymentMonth(month_index=mi+1, allocations=allocs, total_interest=month_interest, total_paid=sum(a.payment for a in allocs)))
        _apply_month(ds, allocs)
        mi += 1

    return RepaymentPlan(strategy="avalanche", months=months, total_interest_paid=total_interest, months_to_debt_free=mi)

def compute_snowball_plan(debts: List[Debt], budget: float, max_months: int) -> RepaymentPlan:
    ok, _ = _validate_budget_and_aprs(debts, budget)
    if not ok:
        return RepaymentPlan(strategy="snowball", months=[], total_interest_paid=0.0, months_to_debt_free=0)

    ds = _clone_debts(debts)
    months: List[RepaymentMonth] = []
    mi = 0
    total_interest = 0.0

    while mi < max_months and not _is_all_cleared(ds):
        min_total = sum(d.min_payment for d in ds if d.balance > 0)
        remaining = max(0.0, budget - min_total)

        allocs: List[Allocation] = []
        for d in ds:
            if d.balance <= 0:
                allocs.append(Allocation(name=d.name, payment=0, interest_accrued=0, principal_reduction=0))
                continue
            r = _monthly_rate(d.apr)
            interest = d.balance * r
            pay = min(d.balance + interest, d.min_payment)
            allocs.append(Allocation(name=d.name, payment=pay, interest_accrued=interest, principal_reduction=max(0.0, pay - interest)))

        for d in sorted(ds, key=lambda x: (x.balance, -x.apr)):
            if remaining <= 0: break
            if d.balance <= 0: continue
            already = next(a for a in allocs if a.name == d.name).payment
            due = max(0.0, d.balance + (d.balance * _monthly_rate(d.apr)) - already)
            extra = min(remaining, due)
            next(a for a in allocs if a.name == d.name).payment += extra
            remaining -= extra

        month_interest = 0.0
        for a, d in zip(allocs, ds):
            r = _monthly_rate(d.apr)
            a.interest_accrued = d.balance * r
            a.principal_reduction = max(0.0, a.payment - a.interest_accrued)
            month_interest += a.interest_accrued

        total_interest += month_interest
        months.append(RepaymentMonth(month_index=mi+1, allocations=allocs, total_interest=month_interest, total_paid=sum(a.payment for a in allocs)))
        _apply_month(ds, allocs)
        mi += 1

    return RepaymentPlan(strategy="snowball", months=months, total_interest_paid=total_interest, months_to_debt_free=mi)

def one_step_optimal_allocation(debts: List[Debt], budget: float) -> RepaymentPlan:
    ok, _ = _validate_budget_and_aprs(debts, budget)
    if not ok:
        return RepaymentPlan(strategy="one_step_optimal", months=[], total_interest_paid=0.0, months_to_debt_free=0)
    try:
        import pulp as pl
    except Exception:
        return compute_avalanche_plan(debts, budget, 1)

    ds = _clone_debts(debts)
    prob = pl.LpProblem("MinimizeInterest", pl.LpMinimize)
    pays = {d.name: pl.LpVariable(f"pay_{i}", lowBound=0) for i,d in enumerate(ds)}
    r = {d.name: _monthly_rate(d.apr) for d in ds}
    prob += pl.lpSum( ( (d.balance + d.balance*r[d.name]) - pays[d.name]) * r[d.name] for d in ds )
    prob += pl.lpSum(pays.values()) <= budget
    for d in ds:
        prob += pays[d.name] >= (0 if d.balance <= 0 else d.min_payment)
        prob += pays[d.name] <= d.balance + d.balance*r[d.name]
    prob.solve(pl.PULP_CBC_CMD(msg=False))

    allocs = []
    month_interest = 0.0
    for d in ds:
        p = max(0.0, float(pays[d.name].value()))
        interest = d.balance * r[d.name]
        month_interest += interest
        allocs.append(Allocation(name=d.name, payment=p, interest_accrued=interest, principal_reduction=max(0.0, p-interest)))
    _apply_month(ds, allocs)
    plan = RepaymentPlan(strategy="one_step_optimal", months=[RepaymentMonth(month_index=1, allocations=allocs, total_interest=month_interest, total_paid=sum(a.payment for a in allocs))], total_interest_paid=month_interest, months_to_debt_free=1)
    return plan
