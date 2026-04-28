# app/api/violation_types.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.violation_type import (
    ViolationTypeCreate, ViolationTypeList, ViolationTypeRead, ViolationTypeUpdate
)
from app.services import violation_type_service

router = APIRouter(prefix="/violation-types", tags=["Jenis Pelanggaran"])


@router.get("/", response_model=ViolationTypeList, summary="Daftar jenis pelanggaran")
def list_violation_types(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * page_size
    items, total = violation_type_service.get_violation_type_list(db, skip=skip, limit=page_size)
    return ViolationTypeList(total=total, items=items)


@router.post(
    "/",
    response_model=ViolationTypeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Tambah jenis pelanggaran baru",
)
def create_violation_type(data: ViolationTypeCreate, db: Session = Depends(get_db)):
    return violation_type_service.create_violation_type(db, data)


@router.get("/{type_id}", response_model=ViolationTypeRead, summary="Detail jenis pelanggaran")
def get_violation_type(type_id: int, db: Session = Depends(get_db)):
    vt = violation_type_service.get_violation_type(db, type_id)
    if not vt:
        raise HTTPException(status_code=404, detail="Jenis pelanggaran tidak ditemukan.")
    return vt


@router.patch("/{type_id}", response_model=ViolationTypeRead, summary="Update jenis pelanggaran")
def update_violation_type(type_id: int, data: ViolationTypeUpdate, db: Session = Depends(get_db)):
    vt = violation_type_service.update_violation_type(db, type_id, data)
    if not vt:
        raise HTTPException(status_code=404, detail="Jenis pelanggaran tidak ditemukan.")
    return vt


@router.delete("/{type_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Hapus jenis pelanggaran")
def delete_violation_type(type_id: int, db: Session = Depends(get_db)):
    if not violation_type_service.delete_violation_type(db, type_id):
        raise HTTPException(status_code=404, detail="Jenis pelanggaran tidak ditemukan.")
