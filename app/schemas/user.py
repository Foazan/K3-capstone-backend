# app/schemas/user.py
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.user import UserRole


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, examples=["admin_k3"])
    role: UserRole = UserRole.MANAGER

    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, v: str | None) -> UserRole:
        if v == "" or v is None:
            return UserRole.MANAGER
        return v


class UserCreate(UserBase):
    """Schema untuk registrasi/penambahan user baru (Admin only)."""
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description="Password (8-72 karakter).",
        examples=["password123"]
    )


class UserUpdate(BaseModel):
    """Partial update user (Admin only)."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=8, max_length=72)
    role: Optional[UserRole] = None


class UserRead(UserBase):
    """Respons data user (tanpa password)."""
    id: int

    model_config = {"from_attributes": True}


class UserList(BaseModel):
    total: int
    items: list[UserRead]


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
