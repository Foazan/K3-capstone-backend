# syntax=docker/dockerfile:1
FROM python:3.13-slim

# Set environment to non-interactive untuk pip
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies yang dibutuhkan PyMySQL dan Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies terlebih dahulu (layer caching)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy seluruh kode aplikasi
COPY . .

# Buat folder uploads
RUN mkdir -p uploads

EXPOSE 8000

# Jalankan dengan uvicorn; --host 0.0.0.0 wajib agar bisa diakses dari luar container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
