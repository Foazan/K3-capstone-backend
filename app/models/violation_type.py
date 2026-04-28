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
    label_name = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Label YOLO untuk jenis pelanggaran (misal: no_helmet)"
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
        return f"<ViolationType(id={self.id}, label='{self.label_name}', score={self.penalty_score})>"


# Data seed awal
VIOLATION_TYPE_SEEDS = [
    {"label_name": "no_helmet",  "penalty_score": 3},
    {"label_name": "no_vest",    "penalty_score": 2},
    {"label_name": "no_gloves",  "penalty_score": 1},
]
