# K3 Monitoring System - Backend

API Backend untuk Sistem Monitoring Keselamatan dan Kesehatan Kerja (K3) menggunakan Computer Vision (YOLO/ESP32-CAM). 
Proyek ini dibangun menggunakan **FastAPI** dan terhubung dengan **MySQL** serta integrasi notifikasi WhatsApp menggunakan **WAHA (WhatsApp HTTP API)**.

## Fitur Utama
- **Deteksi APD Real-time**: Webhook API untuk menerima tangkapan gambar dan data deteksi dari ESP32-CAM atau script YOLO.
- **Manajemen Pelanggaran**: Pencatatan riwayat pelanggaran APD (Helm, Rompi, Sarung Tangan).
- **Notifikasi WhatsApp**: Otomatis mengirim pesan peringatan ke Grup WhatsApp saat pelanggaran divalidasi secara satuan maupun *bulk*.
- **Dashboard API**: Endpoint untuk statistik tingkat kepatuhan (compliance rate) dan riwayat pelanggaran.
- **Role-Based Access Control**: Autentikasi berbasis JWT untuk manajemen hak akses (Admin dan Manager).

## Teknologi yang Digunakan
- **Framework**: FastAPI (Python 3)
- **Database**: MySQL 8.0 (via SQLAlchemy & PyMySQL)
- **Notifikasi**: WAHA (WhatsApp HTTP API)
- **Infrastruktur**: Docker & Docker Compose

---

## Prasyarat (Prerequisites)

Sebelum menjalankan aplikasi ini (terutama di laptop rekan tim atau server), pastikan sistem sudah terinstal perangkat lunak berikut:
1. **Python 3.9+**
2. **Docker Desktop** (atau Docker Engine & Docker Compose)
3. **Git** (opsional)

---

## Langkah-langkah Menjalankan Proyek

### 1. Clone Repositori
Jika Anda baru pertama kali mengambil proyek ini, jalankan perintah berikut di terminal:
```bash
git clone <url-repo-anda>
cd k3-epson
```

### 2. Konfigurasi Environment Variables
Sistem ini menggunakan Environment Variables untuk mengamankan data kredensial.
1. Salin (copy) file `.env.example` menjadi file baru bernama `.env`.
2. Buka file `.env` dan sesuaikan nilainya (terutama isikan `SECRET_KEY` dengan string acak, serta `WA_API_TOKEN` dengan API Key dari WAHA Anda).

### 3. Jalankan Layanan Database & WhatsApp API
Kita menggunakan Docker Compose untuk membungkus (containerize) MySQL dan WAHA agar lingkungan *development* dan *production* tetap konsisten tanpa repot menginstal satu per satu.

Jalankan perintah ini di root folder proyek:
```bash
docker-compose up -d
```
*(Catatan: Tunggu beberapa saat hingga container menyala sempurna. Database MySQL akan otomatis terbuat dan diisi data awal oleh file `init.sql`).*

### 4. Buat dan Aktifkan Virtual Environment (Python)
Untuk mencegah bentrok antar versi library Python di sistem operasi, gunakan virtual environment:

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 5. Install Dependencies Python
Install seluruh modul dan library yang dibutuhkan oleh FastAPI:
```bash
pip install -r requirements.txt
```

### 6. Jalankan Server Aplikasi
Setelah semua siap, jalankan server *backend* menggunakan Uvicorn:
```bash
uvicorn main:app --reload --port 8000
```
Server akan mulai berjalan dan bisa diakses di `http://localhost:8000`.

---

## Dokumentasi API Interaktif (Swagger UI)

Keunggulan menggunakan FastAPI adalah dokumentasi API yang *auto-generated* dan interaktif. Setelah server berjalan (langkah ke-6), buka browser dan akses URL berikut:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

Melalui halaman Swagger UI tersebut, Anda maupun developer Front-End bisa langsung menguji coba (*test*) memanggil API seperti login, melihat riwayat pelanggaran, hingga mengirim deteksi YOLO.

---

## Struktur Folder Proyek
```text
k3-epson/
├── app/
│   ├── api/             # Kumpulan endpoint (violations, auth, dll)
│   ├── core/            # Konfigurasi, Security (JWT), Dependensi Database
│   ├── models/          # Struktur Tabel Database (SQLAlchemy)
│   ├── schemas/         # Validasi Input/Output JSON (Pydantic)
│   └── services/        # Logika Bisnis & Integrasi WhatsApp
├── uploads/             # Folder tempat penyimpanan foto deteksi YOLO
├── main.py              # File utama (entry point) aplikasi FastAPI
├── docker-compose.yml   # Konfigurasi environment Docker
├── requirements.txt     # Daftar lengkap versi library Python
├── .env                 # File environment (JANGAN di-commit ke Git!)
└── init.sql             # Script SQL untuk inisialisasi awal MySQL
```
