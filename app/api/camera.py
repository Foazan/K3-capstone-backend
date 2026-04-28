# app/api/camera.py
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.camera import CameraCreate, CameraList, CameraRead, CameraUpdate
from app.services import camera_service

router = APIRouter(prefix="/camera", tags=["Manajemen Kamera"])


@router.get("/", response_model=CameraList, summary="Daftar kamera")
def list_cameras(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status_cam: Optional[bool] = Query(default=None, description="Filter aktif/nonaktif"),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * page_size
    items, total = camera_service.get_camera_list(db, skip=skip, limit=page_size, status_cam=status_cam)
    return CameraList(total=total, items=items)


@router.post("/", response_model=CameraRead, status_code=status.HTTP_201_CREATED, summary="Tambah kamera")
def create_camera(data: CameraCreate, db: Session = Depends(get_db)):
    return camera_service.create_camera(db, data)


@router.get("/{camera_id}", response_model=CameraRead, summary="Detail kamera")
def get_camera(camera_id: int, db: Session = Depends(get_db)):
    cam = camera_service.get_camera(db, camera_id)
    if not cam:
        raise HTTPException(status_code=404, detail="Kamera tidak ditemukan.")
    return cam


@router.patch("/{camera_id}", response_model=CameraRead, summary="Update kamera")
def update_camera(camera_id: int, data: CameraUpdate, db: Session = Depends(get_db)):
    cam = camera_service.update_camera(db, camera_id, data)
    if not cam:
        raise HTTPException(status_code=404, detail="Kamera tidak ditemukan.")
    return cam


@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Hapus kamera")
def delete_camera(camera_id: int, db: Session = Depends(get_db)):
    if not camera_service.delete_camera(db, camera_id):
        raise HTTPException(status_code=404, detail="Kamera tidak ditemukan.")
