# app/api/users.py
"""
CRUD API untuk manajemen user.
Seluruh endpoint hanya bisa diakses oleh role 'admin'.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.schemas.user import UserCreate, UserList, UserRead, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Manajemen User (Admin Only)"])


@router.get("/", response_model=UserList, summary="Daftar semua user")
def list_users(
    _: Annotated[User, Depends(require_admin)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * page_size
    items, total = user_service.get_user_list(db, skip=skip, limit=page_size)
    return UserList(total=total, items=items)


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tambah user baru",
)
def create_user(
    data: UserCreate,
    _: Annotated[User, Depends(require_admin)],
    db: Session = Depends(get_db),
):
    if user_service.get_user_by_username(db, data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{data.username}' sudah digunakan.",
        )
    return user_service.create_user(db, data)


@router.get("/{user_id}", response_model=UserRead, summary="Detail user")
def get_user(
    user_id: int,
    _: Annotated[User, Depends(require_admin)],
    db: Session = Depends(get_db),
):
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan.")
    return user


@router.patch("/{user_id}", response_model=UserRead, summary="Update user")
def update_user(
    user_id: int,
    data: UserUpdate,
    _: Annotated[User, Depends(require_admin)],
    db: Session = Depends(get_db),
):
    # Cek username unik jika diupdate
    if data.username:
        existing = user_service.get_user_by_username(db, data.username)
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=400,
                detail=f"Username '{data.username}' sudah digunakan user lain.",
            )
    user = user_service.update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan.")
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hapus user",
)
def delete_user(
    user_id: int,
    current_admin: Annotated[User, Depends(require_admin)],
    db: Session = Depends(get_db),
):
    # Cegah admin hapus dirinya sendiri
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=400,
            detail="Tidak bisa menghapus akun Anda sendiri.",
        )
    if not user_service.delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="User tidak ditemukan.")
