# app/schemas/__init__.py
from app.schemas.user import UserCreate, UserRead, UserUpdate, Token, TokenData
from app.schemas.camera import CameraCreate, CameraRead, CameraUpdate, CameraList
from app.schemas.violation_type import (
    ViolationTypeCreate, ViolationTypeRead, ViolationTypeUpdate, ViolationTypeList
)
from app.schemas.violation_log import (
    ViolationLogCreate, ViolationLogRead, ViolationLogList
)

__all__ = [
    "UserCreate", "UserRead", "UserUpdate", "Token", "TokenData",
    "CameraCreate", "CameraRead", "CameraUpdate", "CameraList",
    "ViolationTypeCreate", "ViolationTypeRead", "ViolationTypeUpdate", "ViolationTypeList",
    "ViolationLogCreate", "ViolationLogRead", "ViolationLogList",
]
