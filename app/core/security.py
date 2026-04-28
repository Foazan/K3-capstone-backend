# app/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

# ── Password Hashing (bcrypt langsung, tanpa passlib) ──────────────────────
# passlib 1.7.x tidak kompatibel dengan bcrypt 4.x karena internal
# detect_wrap_bug() mencoba hash string >72 byte yang dilarang di bcrypt 4.0+.
# Solusi: gunakan library bcrypt secara langsung.

_BCRYPT_ROUNDS = 12  # cost factor standar (semakin tinggi semakin aman tapi lambat)


def get_password_hash(password: str) -> str:
    """
    Buat hash bcrypt dari password plain text.
    Password dibatasi max 72 karakter di level Pydantic schema.
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifikasi password plain text terhadap hash bcrypt di database.
    Mengembalikan False (bukan crash) jika terjadi error.
    """
    try:
        password_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


# ── JWT Token ───────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Buat JWT access token.

    Args:
        data: Payload data yang akan di-encode ke token.
        expires_delta: Durasi token berlaku. Default dari settings.

    Returns:
        JWT token string yang telah di-encode.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode dan validasi JWT token.

    Returns:
        Payload dict jika token valid, None jika tidak valid.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
