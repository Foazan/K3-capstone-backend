# main.py
"""
Entry point utama aplikasi FastAPI Monitoring K3 EPSON.
Jalankan dengan: uvicorn main:app --reload
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.core.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle handler aplikasi.
    - Startup: Buat tabel, seed data, buat folder uploads.
    - Shutdown: Cleanup.
    """
    # === STARTUP ===
    print("[STARTUP] Aplikasi K3 Monitoring dimulai...")

    # Buat folder uploads jika belum ada
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    print(f"[STARTUP] Folder upload: '{settings.UPLOAD_DIR}' siap.")

    # Import model baru agar SQLAlchemy mendaftarkan semua tabel
    from app.models import User, Camera, ViolationType, ViolationLog  # noqa: F401
    Base.metadata.create_all(bind=engine)
    print("[STARTUP] Tabel database siap.")

    # Seed data awal ViolationType (no_helmet, no_vest, no_gloves)
    from app.core.database import SessionLocal
    from app.services.violation_type_service import seed_violation_types
    db = SessionLocal()
    try:
        seed_violation_types(db)
    finally:
        db.close()

    yield  # Aplikasi berjalan di sini

    # === SHUTDOWN ===
    print("[SHUTDOWN] Aplikasi K3 Monitoring dihentikan.")



# Inisialisasi aplikasi FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="""
## 🦺 API Monitoring K3 - Sistem Deteksi APD

Backend untuk sistem monitoring **Keselamatan dan Kesehatan Kerja (K3)** 
yang terintegrasi dengan model Computer Vision (YOLO) untuk deteksi 
penggunaan Alat Pelindung Diri (APD) secara real-time.

### Fitur Utama:
- 📹 **Manajemen Kamera**: CRUD kamera CCTV di area kerja
- 🔍 **Penerimaan Deteksi**: Menerima payload deteksi dari script YOLO
- 📊 **Riwayat Pelanggaran**: Filter dan pagination log deteksi
- 🔒 **Autentikasi**: JWT-based login untuk admin dashboard
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# === Middleware ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ganti dengan domain spesifik di production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Static Files (untuk serving foto bukti pelanggaran) ===
if os.path.exists(settings.UPLOAD_DIR):
    app.mount(
        "/uploads",
        StaticFiles(directory=settings.UPLOAD_DIR),
        name="uploads",
    )

# === Register Semua Router API ===
app.include_router(api_router, prefix="/api")


# === Root Endpoint ===
@app.get("/", tags=["Root"], summary="Health Check")
def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "message": "Server Backend Monitoring K3 berhasil berjalan!",
        "aplikasi": settings.APP_NAME,
        "versi": settings.APP_VERSION,
        "dokumentasi": "/docs",
    }