# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,       # Cek koneksi sebelum digunakan (hindari stale connections)
    pool_size=10,             # Jumlah koneksi yang disimpan di pool
    max_overflow=20,          # Koneksi extra saat pool penuh
    pool_recycle=3600,        # Recycle koneksi setiap 1 jam
    echo=settings.DEBUG,      # Tampilkan SQL query di console (hanya saat DEBUG=True)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency generator untuk mendapatkan sesi database.
    Digunakan dengan FastAPI Depends().
    Memastikan sesi selalu ditutup setelah request selesai.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
