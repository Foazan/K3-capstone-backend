# app/models/violation_type.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class ViolationType(Base):
    """
    Model untuk tabel 'violation_type'.
    Mendefinisikan jenis pelanggaran APD yang bisa dideteksi YOLO.
    """
    __tablename__ = "violation_type"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    yolo_class_id = Column(
        Integer,
        unique=True,
        nullable=False,
        index=True,
        comment="Index class dari YOLO (0, 1, 2, dst)"
    )
    label_name = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Label YOLO untuk jenis pelanggaran (misal: Tidak Pakai Helm)"
    )
    penalty_score = Column(
        Integer,
        nullable=False,
        default=1,
        comment="Skor penalti untuk pelanggaran ini"
    )

    # Relasi ke violation_log
    violation_logs = relationship("ViolationLog", back_populates="violation_type", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<ViolationType(id={self.id}, yolo_class={self.yolo_class_id}, label='{self.label_name}', score={self.penalty_score})>"


# Data seed awal
VIOLATION_TYPE_SEEDS = [
    {"yolo_class_id": 0, "label_name": "Tidak Pakai Helm", "penalty_score": 3},
    {"yolo_class_id": 1, "label_name": "Tidak Pakai Rompi", "penalty_score": 2},
    {"yolo_class_id": 2, "label_name": "Tidak Pakai Sarung Tangan", "penalty_score": 1},
]
