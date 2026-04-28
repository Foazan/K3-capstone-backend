# app/models/user.py
import enum

from sqlalchemy import Column, Enum, Integer, String, Text

from app.core.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"


class User(Base):
    """Model untuk tabel 'user'. Digunakan untuk autentikasi."""
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(Text, nullable=False, comment="bcrypt hashed password")
    role = Column(
        Enum(UserRole, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=UserRole.MANAGER.value,
        server_default=UserRole.MANAGER.value,
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
