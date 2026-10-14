"""PLACEHOLDER — paste Gemini's output here.

This file is meant to hold Gemini's independent implementation of
`assert_within_budget`, written from the same prompt given to Claude Code
(see ../two_tool_comparison.md for the exact prompt and the comparison
write-up template). It must not be filled in by Claude Code itself — the
homework requires genuinely running a second AI tool and comparing results,
not a simulated second opinion.

Steps to fill this in for real:
1. Open Gemini (course-provided access is enough).
2. Paste the prompt from ../two_tool_comparison.md.
3. Paste Gemini's returned function body below, unmodified.
4. Run it against tests/test_budget_rule.py (temporarily swap it in for
   backend/app/services/budget.py::assert_within_budget, same way the
   faulty/fixed pair was captured) and record which tests pass/fail.
5. Fill in the comparison table and evaluation in ../two_tool_comparison.md.
"""

from decimal import Decimal

from backend.app.errors import BudgetExceededError
from backend.app.models import ShoppingList


def assert_within_budget_gemini(shopping_list: ShoppingList, projected_total: Decimal) -> None:
    raise NotImplementedError("Paste Gemini's generated implementation here.")
