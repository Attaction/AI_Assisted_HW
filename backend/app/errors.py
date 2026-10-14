class BudgetExceededError(Exception):
    """Raised when adding/editing an item would push a list's total past its budget_limit."""


class PermissionDeniedError(Exception):
    """Raised when a user attempts an action their role does not allow."""


class NotFoundError(Exception):
    """Raised when a referenced list/item/user does not exist."""
