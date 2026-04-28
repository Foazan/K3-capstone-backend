# app/core/dependencies.py
"""
Dependency injection untuk autentikasi dan otorisasi berbasis role (RBAC).

Penggunaan di endpoint:
    @router.get("/admin-only")
    def admin_endpoint(user: Annotated[User, Depends(require_admin)]):
        ...

    @router.get("/manager-or-admin")
    def manager_endpoint(user: Annotated[User, Depends(require_manager_or_above)]):
        ...
"""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
) -> User:
    """Dependency dasar: hanya membutuhkan token JWT valid."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid atau sudah kadaluarsa.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception

    username: str = payload.get("sub")
    if not username:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise credentials_exception
    return user


def require_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Dependency: hanya role 'admin' yang boleh mengakses."""
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Endpoint ini hanya untuk Admin.",
        )
    return current_user


def require_manager_or_above(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Dependency: role 'admin' atau 'manager' boleh mengakses."""
    allowed = {UserRole.ADMIN.value, UserRole.MANAGER.value}
    if current_user.role not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Endpoint ini untuk Admin atau Manager.",
        )
    return current_user
