# app/models/violation_log.py
import enum
from datetime import datetime, timezone

from sqlalchemy import BigInteger, Column, DateTime, Enum, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship

from app.core.database import Base


class ViolationStatus(str, enum.Enum):
    BELUM_DITINDAK = "Belum Ditindak"
    SUDAH_DITINDAK = "Sudah Ditindak"


class ViolationLog(Base):
    """
    Model untuk tabel 'violation_log'.
    Menyimpan setiap kejadian pelanggaran APD yang terdeteksi oleh YOLO.
    """
    __tablename__ = "violation_log"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)

    camera_id = Column(
        Integer,
        ForeignKey("camera.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID kamera sumber deteksi"
    )
    violation_type_id = Column(
        Integer,
        ForeignKey("violation_type.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID jenis pelanggaran"
    )
    image_path = Column(
        String(500),
        nullable=True,
        comment="Path/URL foto bukti pelanggaran"
    )
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
        index=True,
        comment="Waktu deteksi pelanggaran"
    )
    status = Column(
        Enum(
            ViolationStatus,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=ViolationStatus.BELUM_DITINDAK.value,
        server_default=ViolationStatus.BELUM_DITINDAK.value,
        index=True,
        comment="Status penanganan pelanggaran"
    )

    # Relasi
    camera = relationship("Camera", back_populates="violation_logs")
    violation_type = relationship("ViolationType", back_populates="violation_logs")

    def __repr__(self) -> str:
        return (
            f"<ViolationLog(id={self.id}, camera_id={self.camera_id}, "
            f"type_id={self.violation_type_id}, status='{self.status}')>"
        )
