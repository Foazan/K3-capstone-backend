# app/services/violation_type_service.py
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.violation_type import ViolationType, VIOLATION_TYPE_SEEDS
from app.schemas.violation_type import ViolationTypeCreate, ViolationTypeUpdate


def seed_violation_types(db: Session) -> None:
    """
    Isi data awal violation_type jika tabel masih kosong.
    Dipanggil saat startup aplikasi.
    """
    existing_count = db.query(ViolationType).count()
    if existing_count == 0:
        for seed in VIOLATION_TYPE_SEEDS:
            db.add(ViolationType(**seed))
        db.commit()
        print(f"[STARTUP] Seed violation_type: {len(VIOLATION_TYPE_SEEDS)} data ditambahkan.")
    else:
        print(f"[STARTUP] Violation types sudah ada ({existing_count} record), skip seed.")


def get_violation_type(db: Session, type_id: int) -> Optional[ViolationType]:
    return db.query(ViolationType).filter(ViolationType.id == type_id).first()


def get_violation_type_list(
    db: Session, skip: int = 0, limit: int = 50
) -> Tuple[List[ViolationType], int]:
    query = db.query(ViolationType)
    total = query.count()
    items = query.order_by(ViolationType.id).offset(skip).limit(limit).all()
    return items, total


def create_violation_type(db: Session, data: ViolationTypeCreate) -> ViolationType:
    db_vt = ViolationType(**data.model_dump())
    db.add(db_vt)
    db.commit()
    db.refresh(db_vt)
    return db_vt


def update_violation_type(
    db: Session, type_id: int, data: ViolationTypeUpdate
) -> Optional[ViolationType]:
    db_vt = get_violation_type(db, type_id)
    if not db_vt:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_vt, field, value)
    db.commit()
    db.refresh(db_vt)
    return db_vt


def delete_violation_type(db: Session, type_id: int) -> bool:
    db_vt = get_violation_type(db, type_id)
    if not db_vt:
        return False
    db.delete(db_vt)
    db.commit()
    return True
