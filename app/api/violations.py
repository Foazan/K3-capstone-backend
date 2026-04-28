# app/api/violations.py
"""
Router utama untuk pelanggaran K3.
Mencakup:
  - POST /detect      : Webhook dari ESP32-CAM / YOLO (dengan upload gambar)
  - GET  /            : Riwayat pelanggaran dengan filter & pagination
  - GET  /stats       : Statistik dashboard
  - GET  /{id}        : Detail pelanggaran
  - PUT  /{id}/status : Update status + notifikasi WhatsApp
"""
import math
from datetime import datetime
from typing import Annotated, Optional, List

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_manager_or_above
from app.models.user import User
from app.models.violation_log import ViolationStatus
from app.schemas.violation_log import (
    ViolationLogCreate,
    ViolationLogList,
    ViolationLogRead,
    ViolationStatusUpdate,
    ViolationStatusBulkUpdate,
)
from app.services import violation_log_service
from app.services.whatsapp_service import send_whatsapp_group_message

router = APIRouter(prefix="/violations", tags=["Pelanggaran K3"])


# ── POST /detect ─────────────────────────────────────────────────────────────

@router.post(
    "/detect",
    response_model=ViolationLogRead,
    status_code=status.HTTP_201_CREATED,
    summary="Webhook: Terima deteksi dari ESP32-CAM / YOLO",
    description=(
        "Endpoint untuk menerima data deteksi langsung dari modul AI. "
        "Mendukung upload file gambar sebagai bukti pelanggaran (multipart/form-data). "
        "Tidak memerlukan autentikasi agar ESP32-CAM bisa langsung POST."
    ),
)
async def detect_violation(
    camera_id: int = Form(..., description="ID kamera pengirim"),
    violation_type_id: int = Form(..., description="ID jenis pelanggaran"),
    image: Optional[UploadFile] = File(None, description="Foto bukti pelanggaran (opsional)"),
    db: Session = Depends(get_db),
):
    """
    Contoh curl dari ESP32-CAM:
    ```bash
    curl -X POST http://server:8000/api/violations/detect \\
      -F camera_id=1 \\
      -F violation_type_id=2 \\
      -F image=@/path/to/frame.jpg
    ```
    """
    # Simpan gambar jika ada
    image_path: Optional[str] = None
    if image and image.filename:
        image_path = await violation_log_service.save_image(image)

    payload = ViolationLogCreate(
        camera_id=camera_id,
        violation_type_id=violation_type_id,
        image_path=image_path,
    )
    log = violation_log_service.create_violation_log(db, payload)

    # Re-fetch dengan JOIN untuk response lengkap
    return violation_log_service.get_violation_log(db, log.id)


# ── GET /stats ────────────────────────────────────────────────────────────────

@router.get(
    "/stats",
    summary="Statistik dashboard",
    description="Total pelanggaran, per jenis, compliance rate. Butuh autentikasi.",
)
def get_stats(
    _: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    return violation_log_service.get_dashboard_stats(db)


# ── GET / ─────────────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=ViolationLogList,
    summary="Riwayat pelanggaran",
)
def list_violations(
    _: Annotated[User, Depends(get_current_user)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    camera_id: Optional[int] = Query(default=None, description="Filter kamera"),
    violation_type_id: Optional[int] = Query(default=None, description="Filter jenis"),
    status_filter: Optional[ViolationStatus] = Query(
        default=None, alias="status", description="Filter status penanganan"
    ),
    tanggal_mulai: Optional[datetime] = Query(default=None),
    tanggal_selesai: Optional[datetime] = Query(default=None),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * page_size
    items, total = violation_log_service.get_violation_log_list(
        db=db,
        skip=skip,
        limit=page_size,
        camera_id=camera_id,
        violation_type_id=violation_type_id,
        status=status_filter,
        tanggal_mulai=tanggal_mulai,
        tanggal_selesai=tanggal_selesai,
    )
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    return ViolationLogList(
        total=total, page=page, page_size=page_size,
        total_pages=total_pages, items=items,
    )


# ── GET /{id} ─────────────────────────────────────────────────────────────────

@router.get(
    "/{log_id}",
    response_model=ViolationLogRead,
    summary="Detail pelanggaran",
)
def get_violation(
    log_id: int,
    _: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    log = violation_log_service.get_violation_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail=f"Log ID {log_id} tidak ditemukan.")
    return log


# ── PUT /bulk/status ─────────────────────────────────────────────────────────

@router.put(
    "/bulk/status",
    response_model=List[ViolationLogRead],
    summary="Update status penanganan secara bulk + kirim notifikasi WhatsApp",
)
def bulk_update_status(
    payload: ViolationStatusBulkUpdate,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(require_manager_or_above)],
    db: Session = Depends(get_db),
):
    """
    Update status beberapa log sekaligus.
    Mengirimkan satu pesan ringkasan ke WhatsApp grup jika statusnya "Sudah Ditindak".
    """
    updated_logs = violation_log_service.bulk_update_violation_status(
        db, payload.log_ids, payload.status
    )

    if not updated_logs:
        raise HTTPException(status_code=404, detail="Tidak ada log ID yang ditemukan atau berhasil diupdate.")

    # Kirim notifikasi WA group jika status diubah menjadi SUDAH_DITINDAK
    if payload.status == ViolationStatus.SUDAH_DITINDAK:
        if len(updated_logs) == 1:
            log = updated_logs[0]
            area = log.camera.area_name if log.camera else "Tidak diketahui"
            label = log.violation_type.label_name if log.violation_type else "Tidak diketahui"
            waktu = log.created_at.strftime("%d %b %Y %H:%M") if log.created_at else "Waktu tidak diketahui"
            
            pesan = (
                f"🚨 *PERINGATAN K3!*\n\n"
                f"Terdapat pelanggaran yang telah divalidasi:\n"
                f"• *Jenis*: {label}\n"
                f"• *Lokasi*: {area}\n"
                f"• *Waktu*: {waktu}\n"
                f"• *ID Log*: #{log.id}\n\n"
                f"Mohon tim terkait segera menindaklanjuti di lapangan."
            )
        else:
            # Format pesan ringkasan untuk bulk
            pesan = "🚨 *UPDATE K3 (BULK VALIDATION)* 🚨\n\nBeberapa pelanggaran telah ditindaklanjuti:\n\n"
            for log in updated_logs:
                area = log.camera.area_name if log.camera else "Tidak diketahui"
                label = log.violation_type.label_name if log.violation_type else "Tidak diketahui"
                pesan += f"• #{log.id} - {label} di {area}\n"
                
            pesan += "\nMohon tim terkait memastikan penyelesaian di lapangan."
        
        # Kirim secara asinkron (menggunakan method yang sesuai dari whatsapp_service)
        # Group ID sudah dikonfigurasi di dalam whatsapp_service.py
        background_tasks.add_task(send_whatsapp_group_message, pesan)

    return updated_logs


# ── PUT /{id}/status ──────────────────────────────────────────────────────────

@router.put(
    "/{log_id}/status",
    response_model=ViolationLogRead,
    summary="Update status penanganan + kirim notifikasi WhatsApp",
)
def update_status(
    log_id: int,
    payload: ViolationStatusUpdate,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(require_manager_or_above)],
    db: Session = Depends(get_db),
):
    """
    Dipanggil ketika Manager/Admin menekan tombol tindak lanjut di dashboard.
    Otomatis mengirim notifikasi WhatsApp grup menggunakan WAHA.
    """
    log = violation_log_service.update_violation_status(db, log_id, payload.status)
    if not log:
        raise HTTPException(status_code=404, detail=f"Log ID {log_id} tidak ditemukan.")

    if payload.status == ViolationStatus.SUDAH_DITINDAK:
        area = log.camera.area_name if log.camera else "Tidak diketahui"
        label = log.violation_type.label_name if log.violation_type else "Tidak diketahui"
        waktu = log.created_at.strftime("%d %b %Y %H:%M") if log.created_at else "Waktu tidak diketahui"
        
        pesan = (
            f"🚨 *PERINGATAN K3!*\n\n"
            f"Terdapat pelanggaran yang telah divalidasi:\n"
            f"• *Jenis*: {label}\n"
            f"• *Lokasi*: {area}\n"
            f"• *Waktu*: {waktu}\n"
            f"• *ID Log*: #{log.id}\n\n"
            f"Mohon tim terkait segera menindaklanjuti di lapangan."
        )
        
        background_tasks.add_task(send_whatsapp_group_message, pesan)

    return log


# ── PUT /{violation_id}/validate ──────────────────────────────────────────────

@router.put(
    "/{violation_id}/validate",
    response_model=ViolationLogRead,
    summary="Validasi pelanggaran dan kirim WA ke grup",
)
def validate_violation(
    violation_id: int,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(require_manager_or_above)],
    db: Session = Depends(get_db),
):
    """
    Memvalidasi pelanggaran (ubah status menjadi 'Sudah Ditindak')
    lalu mengirim notifikasi ke grup WhatsApp secara asinkron.
    """
    # a. Cari log pelanggaran
    log = violation_log_service.get_violation_log(db, violation_id)
    if not log:
        raise HTTPException(status_code=404, detail=f"Log ID {violation_id} tidak ditemukan.")

    # b. Cek status
    if log.status == ViolationStatus.SUDAH_DITINDAK:
        raise HTTPException(status_code=400, detail="Pelanggaran ini sudah ditindak sebelumnya.")

    # c. Ubah status dan commit
    log.status = ViolationStatus.SUDAH_DITINDAK
    db.commit()
    db.refresh(log)

    # d. Format pesan teks
    area = log.camera.area_name if log.camera else "Tidak diketahui"
    label = log.violation_type.label_name if log.violation_type else "Tidak diketahui"
    waktu = log.created_at.strftime("%d %b %Y %H:%M") if log.created_at else "Waktu tidak diketahui"
    
    pesan = (
        f"🚨 *PERINGATAN K3!*\n\n"
        f"Terdapat pelanggaran yang telah divalidasi:\n"
        f"• *Jenis*: {label}\n"
        f"• *Lokasi*: {area}\n"
        f"• *Waktu*: {waktu}\n"
        f"• *ID Log*: #{violation_id}\n\n"
        f"Mohon tim terkait segera menindaklanjuti di lapangan."
    )

    # e. Panggil pengiriman pesan WA menggunakan BackgroundTasks
    background_tasks.add_task(send_whatsapp_group_message, pesan)

    return log
