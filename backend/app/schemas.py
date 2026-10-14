from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field

from .models import Role


# ---- Auth ----
class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(min_length=8, max_length=255)


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    user: UserOut


# ---- Lists ----
class ListCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    budget_limit: Decimal | None = Field(default=None, ge=0)


class ListUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    budget_limit: Decimal | None = Field(default=None, ge=0)


class ItemOut(BaseModel):
    id: int
    name: str
    quantity: int
    unit_price: Decimal
    is_bought: bool
    added_by_id: int

    class Config:
        from_attributes = True


class ListOut(BaseModel):
    id: int
    name: str
    owner_id: int
    budget_limit: Decimal | None
    total: Decimal
    items: list[ItemOut]

    class Config:
        from_attributes = True


# ---- Items ----
class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(ge=0)


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    quantity: int | None = Field(default=None, gt=0)
    unit_price: Decimal | None = Field(default=None, ge=0)
    is_bought: bool | None = None


# ---- Collaborators ----
class CollaboratorAdd(BaseModel):
    username: str
    role: Role


class CollaboratorOut(BaseModel):
    user_id: int
    username: str
    role: Role

    class Config:
        from_attributes = True
