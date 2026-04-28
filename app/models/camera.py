# app/models/camera.py
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Camera(Base):
    """Model untuk tabel 'camera'. Data CCTV di area kerja."""
    __tablename__ = "camera"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    area_name = Column(String(150), nullable=False, comment="Nama area/lokasi kamera")
    status_cam = Column(
        Boolean,
        default=True,
        server_default="1",
        nullable=False,
        comment="Status aktif kamera"
    )

    # Relasi ke violation_log
    violation_logs = relationship("ViolationLog", back_populates="camera", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Camera(id={self.id}, area_name='{self.area_name}')>"
