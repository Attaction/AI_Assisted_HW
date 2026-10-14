from ..errors import PermissionDeniedError
from ..models import ListMembership, Role, ShoppingList, User


def get_membership(shopping_list: ShoppingList, user: User) -> ListMembership | None:
    for membership in shopping_list.memberships:
        if membership.user_id == user.id:
            return membership
    return None


def require_member(shopping_list: ShoppingList, user: User) -> ListMembership | None:
    """Raise if user is neither owner nor collaborator. Returns membership (None if owner)."""
    if shopping_list.owner_id == user.id:
        return None
    membership = get_membership(shopping_list, user)
    if membership is None:
        raise PermissionDeniedError("You are not a member of this list")
    return membership


def require_owner(shopping_list: ShoppingList, user: User) -> None:
    if shopping_list.owner_id != user.id:
        raise PermissionDeniedError("Only the list owner can perform this action")


def require_editor_or_owner(shopping_list: ShoppingList, user: User) -> None:
    if shopping_list.owner_id == user.id:
        return
    membership = get_membership(shopping_list, user)
    if membership is None or membership.role != Role.editor:
        raise PermissionDeniedError("Only the owner or an editor can perform this action")
