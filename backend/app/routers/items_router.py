from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..errors import BudgetExceededError, PermissionDeniedError
from ..models import Item, ShoppingList, User
from ..schemas import ItemCreate, ItemOut, ItemUpdate
from ..services.budget import assert_within_budget, compute_list_total
from ..services.permissions import require_editor_or_owner, require_member

router = APIRouter(prefix="/lists/{list_id}/items", tags=["items"])


def _get_list_or_404(db: Session, list_id: int) -> ShoppingList:
    shopping_list = db.get(ShoppingList, list_id)
    if shopping_list is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "List not found")
    return shopping_list


def _get_item_or_404(db: Session, list_id: int, item_id: int) -> Item:
    item = (
        db.query(Item).filter(Item.id == item_id, Item.list_id == list_id).first()
    )
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")
    return item


@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def add_item(
    list_id: int,
    payload: ItemCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    shopping_list = _get_list_or_404(db, list_id)
    try:
        require_editor_or_owner(shopping_list, user)
    except PermissionDeniedError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc))

    current_total = compute_list_total(shopping_list)
    projected_total = current_total + Decimal(payload.quantity) * payload.unit_price
    try:
        assert_within_budget(shopping_list, projected_total)
    except BudgetExceededError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc))

    item = Item(
        list_id=list_id,
        name=payload.name,
        quantity=payload.quantity,
        unit_price=payload.unit_price,
        added_by_id=user.id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=ItemOut)
def update_item(
    list_id: int,
    item_id: int,
    payload: ItemUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    shopping_list = _get_list_or_404(db, list_id)
    item = _get_item_or_404(db, list_id, item_id)

    bought_only = (
        payload.name is None and payload.quantity is None and payload.unit_price is None
    )
    if bought_only and payload.is_bought is not None:
        try:
            require_member(shopping_list, user)
        except PermissionDeniedError as exc:
            raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc))
        item.is_bought = payload.is_bought
        db.commit()
        db.refresh(item)
        return item

    try:
        require_editor_or_owner(shopping_list, user)
    except PermissionDeniedError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc))

    new_quantity = payload.quantity if payload.quantity is not None else item.quantity
    new_unit_price = (
        payload.unit_price if payload.unit_price is not None else Decimal(item.unit_price)
    )
    other_items_total = compute_list_total(
        shopping_list, [i for i in shopping_list.items if i.id != item.id]
    )
    projected_total = other_items_total + Decimal(new_quantity) * Decimal(new_unit_price)
    try:
        assert_within_budget(shopping_list, projected_total)
    except BudgetExceededError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc))

    if payload.name is not None:
        item.name = payload.name
    item.quantity = new_quantity
    item.unit_price = new_unit_price
    if payload.is_bought is not None:
        item.is_bought = payload.is_bought
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    list_id: int,
    item_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    shopping_list = _get_list_or_404(db, list_id)
    item = _get_item_or_404(db, list_id, item_id)
    try:
        require_editor_or_owner(shopping_list, user)
    except PermissionDeniedError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc))
    db.delete(item)
    db.commit()
