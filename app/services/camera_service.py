# app/services/camera_service.py
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraUpdate


def get_camera(db: Session, camera_id: int) -> Optional[Camera]:
    return db.query(Camera).filter(Camera.id == camera_id).first()


def get_camera_list(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    status_cam: Optional[bool] = None,
) -> Tuple[List[Camera], int]:
    query = db.query(Camera)
    if status_cam is not None:
        query = query.filter(Camera.status_cam == status_cam)
    total = query.count()
    items = query.order_by(Camera.id).offset(skip).limit(limit).all()
    return items, total


def create_camera(db: Session, data: CameraCreate) -> Camera:
    db_cam = Camera(**data.model_dump())
    db.add(db_cam)
    db.commit()
    db.refresh(db_cam)
    return db_cam


def update_camera(db: Session, camera_id: int, data: CameraUpdate) -> Optional[Camera]:
    db_cam = get_camera(db, camera_id)
    if not db_cam:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_cam, field, value)
    db.commit()
    db.refresh(db_cam)
    return db_cam


def delete_camera(db: Session, camera_id: int) -> bool:
    db_cam = get_camera(db, camera_id)
    if not db_cam:
        return False
    db.delete(db_cam)
    db.commit()
    return True
