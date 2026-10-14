from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..errors import PermissionDeniedError
from ..models import ListMembership, Role, ShoppingList, User
from ..schemas import CollaboratorAdd, CollaboratorOut, ListCreate, ListOut, ListUpdate
from ..services.budget import compute_list_total
from ..services.permissions import require_member, require_owner

router = APIRouter(prefix="/lists", tags=["lists"])


def _to_list_out(shopping_list: ShoppingList) -> ListOut:
    return ListOut(
        id=shopping_list.id,
        name=shopping_list.name,
        owner_id=shopping_list.owner_id,
        budget_limit=shopping_list.budget_limit,
        total=compute_list_total(shopping_list),
        items=shopping_list.items,
    )


def _get_list_or_404(db: Session, list_id: int) -> ShoppingList:
    shopping_list = db.get(ShoppingList, list_id)
    if shopping_list is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "List not found")
    return shopping_list


@router.post("", response_model=ListOut, status_code=status.HTTP_201_CREATED)
def create_list(
    payload: ListCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    shopping_list = ShoppingList(
        name=payload.name, owner_id=user.id, budget_limit=payload.budget_limit
    )
    db.add(shopping_list)
    db.commit()
    db.refresh(shopping_list)
    return _to_list_out(shopping_list)


@router.get("", response_model=list[ListOut])
def list_my_lists(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    owned = db.query(ShoppingList).filter(ShoppingList.owner_id == user.id).all()
    shared_ids = [
        m.list_id for m in db.query(ListMembership).filter(ListMembership.user_id == user.id)
    ]
    shared = (
        db.query(ShoppingList).filter(ShoppingList.id.in_(shared_ids)).all() if shared_ids else []
    )
    return [_to_list_out(lst) for lst in owned + shared]


@router.get("/{list_id}", response_model=ListOut)
def get_list(
    list_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    shopping_list = _get_list_or_404(db, list_id)
    try:
        require_member(shopping_list, user)
    except PermissionDeniedError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc))
    return _to_list_out(shopping_list)


@router.patch("/{list_id}", response_model=ListOut)
def update_list(
    list_id: int,
    payload: ListUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    shopping_list = _get_list_or_404(db, list_id)
    try:
        require_owner(shopping_list, user)
    except PermissionDeniedError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc))

    if payload.name is not None:
        shopping_list.name = payload.name
    if payload.budget_limit is not None:
        shopping_list.budget_limit = payload.budget_limit
    db.commit()
    db.refresh(shopping_list)
    return _to_list_out(shopping_list)


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_list(
    list_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    shopping_list = _get_list_or_404(db, list_id)
    try:
        require_owner(shopping_list, user)
    except PermissionDeniedError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc))
    db.delete(shopping_list)
    db.commit()


@router.get("/{list_id}/collaborators", response_model=list[CollaboratorOut])
def get_collaborators(
    list_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    shopping_list = _get_list_or_404(db, list_id)
    try:
        require_member(shopping_list, user)
    except PermissionDeniedError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc))
    return [
        CollaboratorOut(user_id=m.user_id, username=m.user.username, role=m.role)
        for m in shopping_list.memberships
    ]


@router.post(
    "/{list_id}/collaborators",
    response_model=CollaboratorOut,
    status_code=status.HTTP_201_CREATED,
)
def add_collaborator(
    list_id: int,
    payload: CollaboratorAdd,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    shopping_list = _get_list_or_404(db, list_id)
    try:
        require_owner(shopping_list, user)
    except PermissionDeniedError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc))

    target = db.query(User).filter(User.username == payload.username).first()
    if target is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    if target.id == shopping_list.owner_id:
        raise HTTPException(status.HTTP_409_CONFLICT, "Owner is already a member")
    existing = (
        db.query(ListMembership)
        .filter(ListMembership.list_id == list_id, ListMembership.user_id == target.id)
        .first()
    )
    if existing is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "User is already a collaborator")

    membership = ListMembership(list_id=list_id, user_id=target.id, role=payload.role)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return CollaboratorOut(user_id=target.id, username=target.username, role=membership.role)


@router.delete("/{list_id}/collaborators/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_collaborator(
    list_id: int,
    user_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    shopping_list = _get_list_or_404(db, list_id)
    try:
        require_owner(shopping_list, user)
    except PermissionDeniedError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc))

    membership = (
        db.query(ListMembership)
        .filter(ListMembership.list_id == list_id, ListMembership.user_id == user_id)
        .first()
    )
    if membership is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Collaborator not found")
    db.delete(membership)
    db.commit()
