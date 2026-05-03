# app/services/violation_log_service.py
import math
import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from fastapi import UploadFile, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.models.camera import Camera
from app.models.violation_log import ViolationLog, ViolationStatus
from app.models.violation_type import ViolationType
from app.schemas.violation_log import ViolationLogCreate


# ── Create ──────────────────────────────────────────────────────────────────

async def save_image(file: UploadFile) -> str:
    """
    Simpan file gambar ke folder uploads dan kembalikan path relatifnya.
    Nama file: {uuid}.{ext} agar tidak ada konflik.
    """
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or "image.jpg")[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    return file_path  # misal: "uploads/abc123.jpg"


def create_violation_log(db: Session, payload: ViolationLogCreate) -> ViolationLog:
    """Simpan log pelanggaran dari payload YOLO / ESP32-CAM."""
    
    # Translate yolo_class_id ke violation_type_id
    violation_type = db.query(ViolationType).filter(ViolationType.yolo_class_id == payload.yolo_class_id).first()
    if not violation_type:
        raise HTTPException(status_code=404, detail=f"Jenis pelanggaran dengan yolo_class_id {payload.yolo_class_id} tidak ditemukan.")

    timestamp = payload.created_at or datetime.now(timezone.utc)
    db_log = ViolationLog(
        camera_id=payload.camera_id,
        violation_type_id=violation_type.id,
        image_path=payload.image_path,
        created_at=timestamp,
        status=ViolationStatus.BELUM_DITINDAK.value,
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


# ── Read ─────────────────────────────────────────────────────────────────────

def _with_joins(query):
    return query.options(
        joinedload(ViolationLog.camera),
        joinedload(ViolationLog.violation_type),
    )


def get_violation_log(db: Session, log_id: int) -> Optional[ViolationLog]:
    return (
        _with_joins(db.query(ViolationLog))
        .filter(ViolationLog.id == log_id)
        .first()
    )


def get_violation_log_list(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    camera_id: Optional[int] = None,
    violation_type_id: Optional[int] = None,
    status: Optional[ViolationStatus] = None,
    tanggal_mulai: Optional[datetime] = None,
    tanggal_selesai: Optional[datetime] = None,
) -> Tuple[List[ViolationLog], int]:
    query = _with_joins(db.query(ViolationLog))

    if camera_id is not None:
        query = query.filter(ViolationLog.camera_id == camera_id)
    if violation_type_id is not None:
        query = query.filter(ViolationLog.violation_type_id == violation_type_id)
    if status is not None:
        query = query.filter(ViolationLog.status == status.value)
    if tanggal_mulai:
        query = query.filter(ViolationLog.created_at >= tanggal_mulai)
    if tanggal_selesai:
        query = query.filter(ViolationLog.created_at <= tanggal_selesai)

    total = query.count()
    items = query.order_by(ViolationLog.created_at.desc()).offset(skip).limit(limit).all()
    return items, total


# ── Update Status ─────────────────────────────────────────────────────────────

def update_violation_status(
    db: Session, log_id: int, new_status: ViolationStatus
) -> Optional[ViolationLog]:
    """Update status penanganan. Return None jika tidak ditemukan."""
    db_log = db.query(ViolationLog).filter(ViolationLog.id == log_id).first()
    if not db_log:
        return None
    db_log.status = new_status.value
    db.commit()
    db.refresh(db_log)
    return get_violation_log(db, log_id)  # re-fetch dengan JOIN


def bulk_update_violation_status(
    db: Session, log_ids: List[int], new_status: ViolationStatus
) -> List[ViolationLog]:
    """Update status penanganan secara bulk. Mengembalikan list log yang berhasil diupdate."""
    db_logs = db.query(ViolationLog).filter(ViolationLog.id.in_(log_ids)).all()
    
    if not db_logs:
        return []

    for log in db_logs:
        log.status = new_status.value
        
    db.commit()
    
    # Re-fetch semua log yang diupdate dengan JOIN
    updated_ids = [log.id for log in db_logs]
    return (
        _with_joins(db.query(ViolationLog))
        .filter(ViolationLog.id.in_(updated_ids))
        .all()
    )


# ── Dashboard Stats ──────────────────────────────────────────────────────────

def get_dashboard_stats(db: Session) -> dict:
    """
    Statistik ringkasan untuk dashboard:
    - Total pelanggaran
    - Jumlah per jenis pelanggaran
    - Compliance rate
    - Jumlah belum/sudah ditindak
    - Total kamera aktif
    """
    total = db.query(ViolationLog).count()
    belum = db.query(ViolationLog).filter(
        ViolationLog.status == ViolationStatus.BELUM_DITINDAK.value
    ).count()
    sudah = db.query(ViolationLog).filter(
        ViolationLog.status == ViolationStatus.SUDAH_DITINDAK.value
    ).count()
    active_cameras = db.query(Camera).filter(Camera.status_cam == True).count()

    # Compliance rate = % log yang sudah ditindak dari total
    compliance_rate = round((sudah / total * 100), 2) if total > 0 else 100.0

    # Pelanggaran per jenis
    per_type = (
        db.query(
            ViolationType.id,
            ViolationType.label_name,
            ViolationType.penalty_score,
            func.count(ViolationLog.id).label("count"),
        )
        .outerjoin(ViolationLog, ViolationType.id == ViolationLog.violation_type_id)
        .group_by(ViolationType.id, ViolationType.label_name, ViolationType.penalty_score)
        .order_by(func.count(ViolationLog.id).desc())
        .all()
    )

    # Pelanggaran per kamera
    per_camera = (
        db.query(
            Camera.id,
            Camera.area_name,
            func.count(ViolationLog.id).label("count"),
        )
        .outerjoin(ViolationLog, Camera.id == ViolationLog.camera_id)
        .group_by(Camera.id, Camera.area_name)
        .order_by(func.count(ViolationLog.id).desc())
        .limit(5)
        .all()
    )

    return {
        "total_violations": total,
        "belum_ditindak": belum,
        "sudah_ditindak": sudah,
        "compliance_rate_percent": compliance_rate,
        "active_cameras": active_cameras,
        "violations_per_type": [
            {
                "id": r.id,
                "label": r.label_name,
                "penalty_score": r.penalty_score,
                "count": r.count,
            }
            for r in per_type
        ],
        "top_cameras": [
            {"id": r.id, "area_name": r.area_name, "count": r.count}
            for r in per_camera
        ],
    }
