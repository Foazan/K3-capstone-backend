# app/services/notification_service.py
"""
Layanan notifikasi WhatsApp.
Dipicu oleh Manager saat menekan tombol "Tindak Lanjut" di dashboard.

Provider yang didukung: Fonnte (https://fonnte.com) — default.
Mudah diganti ke Wablas/Twilio dengan mengubah format request di send_whatsapp().
"""
import logging
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_whatsapp(
    message: str,
    target: Optional[str] = None,
) -> dict:
    """
    Kirim pesan WhatsApp via Fonnte API.

    Args:
        message: Teks pesan yang dikirim.
        target: Nomor tujuan (format: 628xxx). Default dari settings.

    Returns:
        dict: Response dari WA API atau error info.
    """
    phone = target or settings.WA_DEFAULT_TARGET

    if not settings.WA_API_URL or not settings.WA_API_TOKEN:
        logger.warning("WA_API_URL / WA_API_TOKEN belum dikonfigurasi. Notifikasi dilewati.")
        return {"status": "skipped", "reason": "WA API not configured"}

    if not phone:
        return {"status": "error", "reason": "Nomor tujuan WhatsApp tidak ditentukan"}

    headers = {"Authorization": settings.WA_API_TOKEN}
    payload = {
        "target": phone,
        "message": message,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(settings.WA_API_URL, data=payload, headers=headers)
            result = response.json()
            logger.info(f"WA notification sent to {phone}: {result}")
            return {"status": "sent", "response": result}
    except httpx.TimeoutException:
        logger.error("WA API timeout")
        return {"status": "error", "reason": "WA API request timeout"}
    except Exception as e:
        logger.error(f"WA API error: {e}")
        return {"status": "error", "reason": str(e)}


def build_violation_message(
    area_name: str,
    violation_label: str,
    violation_id: int,
    image_url: Optional[str] = None,
) -> str:
    """Buat format pesan WhatsApp standar untuk notifikasi pelanggaran."""
    lines = [
        "🚨 *PERINGATAN K3 — Pelanggaran Terdeteksi*",
        "",
        f"📍 *Lokasi*: {area_name}",
        f"⚠️  *Jenis*: {violation_label}",
        f"🆔 *ID Log*: #{violation_id}",
    ]
    if image_url:
        lines.append(f"🖼️  *Bukti*: {image_url}")
    lines += [
        "",
        "Harap segera ditindaklanjuti melalui Dashboard K3.",
    ]
    return "\n".join(lines)
