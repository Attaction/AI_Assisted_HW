"""Gemini (Antigravity) independent implementation of the budget check.

Generated from the shared prompt in ../two_tool_comparison.md, run in a separate
workspace that did not contain backend/app/services/budget.py. Pasted unmodified
below this docstring.
"""

from decimal import Decimal

from backend.app.errors import BudgetExceededError


def assert_within_budget_gemini(shopping_list, projected_total: Decimal) -> None:
    if shopping_list.budget_limit is None:
        return

    budget_limit = (
        shopping_list.budget_limit
        if isinstance(shopping_list.budget_limit, Decimal)
        else Decimal(str(shopping_list.budget_limit))
    )

    if projected_total > budget_limit:
        raise BudgetExceededError(
            f"Projected total {projected_total} exceeds budget limit of {budget_limit}."
        )
