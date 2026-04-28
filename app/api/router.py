# app/api/router.py
from fastapi import APIRouter

from app.api import auth, camera, users, violations, violation_types

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(camera.router)
api_router.include_router(violation_types.router)
api_router.include_router(violations.router)
