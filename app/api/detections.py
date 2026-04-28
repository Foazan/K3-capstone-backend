# app/api/detections.py
import math
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.violation_log import ViolationLogCreate, ViolationLogList, ViolationLogRead
from app.services import violation_log_service

router = APIRouter(prefix="/detections", tags=["Log Pelanggaran APD"])


@router.post(
    "/",
    response_model=ViolationLogRead,
    status_code=status.HTTP_201_CREATED,
    summary="Terima data deteksi dari YOLO",
    description=(
        "Endpoint utama untuk menerima payload JSON dari script YOLO. "
        "Menyimpan log pelanggaran APD ke database."
    ),
)
def create_violation(
    payload: ViolationLogCreate,
    db: Session = Depends(get_db),
):
    """
    Menerima data deteksi dari YOLO dan menyimpannya ke violation_log.

    **Contoh payload:**
    ```json
    {
        "camera_id": 1,
        "violation_type_id": 1,
        "image_path": "uploads/frame_20240101_120000.jpg"
    }
    ```
    """
    log = violation_log_service.create_violation_log(db, payload)
    # Re-fetch dengan JOIN agar response langsung punya camera & violation_type
    return violation_log_service.get_violation_log(db, log.id)


@router.get(
    "/",
    response_model=ViolationLogList,
    summary="Riwayat log pelanggaran",
)
def list_violations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    camera_id: Optional[int] = Query(default=None, description="Filter berdasarkan kamera"),
    violation_type_id: Optional[int] = Query(default=None, description="Filter berdasarkan jenis pelanggaran"),
    tanggal_mulai: Optional[datetime] = Query(default=None, description="Filter dari tanggal"),
    tanggal_selesai: Optional[datetime] = Query(default=None, description="Filter sampai tanggal"),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * page_size
    items, total = violation_log_service.get_violation_log_list(
        db=db,
        skip=skip,
        limit=page_size,
        camera_id=camera_id,
        violation_type_id=violation_type_id,
        tanggal_mulai=tanggal_mulai,
        tanggal_selesai=tanggal_selesai,
    )
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    return ViolationLogList(total=total, page=page, page_size=page_size, total_pages=total_pages, items=items)


@router.get(
    "/statistik",
    summary="Statistik ringkasan dashboard",
)
def get_statistik(db: Session = Depends(get_db)):
    return violation_log_service.get_statistik(db)


@router.get(
    "/{log_id}",
    response_model=ViolationLogRead,
    summary="Detail log pelanggaran",
)
def get_violation(log_id: int, db: Session = Depends(get_db)):
    log = violation_log_service.get_violation_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail=f"Log ID {log_id} tidak ditemukan.")
    return log
