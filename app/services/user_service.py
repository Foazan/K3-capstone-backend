# app/services/user_service.py
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_user_list(db: Session, skip: int = 0, limit: int = 50) -> Tuple[List[User], int]:
    query = db.query(User)
    total = query.count()
    items = query.order_by(User.id).offset(skip).limit(limit).all()
    return items, total


def create_user(db: Session, data: UserCreate) -> User:
    db_user = User(
        username=data.username,
        password=get_password_hash(data.password),
        role=data.role.value,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, data: UserUpdate) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    update_dict = data.model_dump(exclude_unset=True)
    if "password" in update_dict:
        update_dict["password"] = get_password_hash(update_dict["password"])
    if "role" in update_dict and hasattr(update_dict["role"], "value"):
        update_dict["role"] = update_dict["role"].value
    for field, value in update_dict.items():
        setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True
