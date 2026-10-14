from decimal import Decimal

from ..errors import BudgetExceededError
from ..models import Item, ShoppingList


def compute_list_total(shopping_list: ShoppingList, items: list[Item] | None = None) -> Decimal:
    """Sum quantity*unit_price over all items on the list (bought or not).

    Bought items still count toward the budget: the chosen interpretation is
    that the budget tracks total planned spend, not just what remains to buy.
    See SPECIFICATION.md "Uncertainties".
    """
    rows = items if items is not None else shopping_list.items
    total = Decimal("0")
    for item in rows:
        total += Decimal(item.quantity) * Decimal(item.unit_price)
    return total


def assert_within_budget(shopping_list: ShoppingList, projected_total: Decimal) -> None:
    """Reject a projected total that would exceed budget_limit. Boundary is inclusive:
    a projected total exactly equal to budget_limit is allowed."""
    if shopping_list.budget_limit is None:
        return
    if projected_total > Decimal(shopping_list.budget_limit):
        raise BudgetExceededError(
            f"Projected total {projected_total} exceeds budget limit {shopping_list.budget_limit}"
        )
