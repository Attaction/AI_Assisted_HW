"""Deliberately faulty variant of services/budget.py::assert_within_budget, kept here only
as rubric evidence of a fail-then-pass test cycle.

NOT a real bug encountered during development — introduced on purpose per the homework's
"testing and defect detection" requirement, which allows a clearly labeled deliberate fault
when no real defect was found during development.

Fault: uses `>=` instead of `>`, so a projected total that lands exactly on budget_limit
(the inclusive boundary required by AC4) is incorrectly rejected.
"""

from decimal import Decimal

from backend.app.errors import BudgetExceededError
from backend.app.models import ShoppingList


def assert_within_budget_faulty(shopping_list: ShoppingList, projected_total: Decimal) -> None:
    if shopping_list.budget_limit is None:
        return
    if projected_total >= Decimal(shopping_list.budget_limit):  # BUG: off-by-one, should be >
        raise BudgetExceededError(
            f"Projected total {projected_total} exceeds budget limit {shopping_list.budget_limit}"
        )
