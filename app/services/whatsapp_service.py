import logging
import httpx

from app.core.config import settings

# Setup Logger
logger = logging.getLogger(__name__)

# Konfigurasi WA API (WAHA / Evolution API)
WA_API_URL = "http://localhost:3000/api/sendText"

# Placeholder untuk ID Grup WhatsApp Anda
# Ganti ini dengan ID grup yang sebenarnya (misalnya: 120363xxxxxx@g.us)
K3_GROUP_ID = "120363409012877328@g.us"


async def send_whatsapp_group_message(message: str) -> None:
    """
    Mengirim pesan teks ke grup WhatsApp melalui API pihak ketiga (misal: WAHA).
    Berjalan secara asinkron agar tidak memblokir event loop.
    """
    payload = {
        "session": "default",
        "chatId": K3_GROUP_ID,
        "text": message
    }
    
    headers = {}
    if settings.WA_API_TOKEN:
        # WAHA Plus menggunakan X-Api-Key, Evolution API menggunakan apikey
        headers["X-Api-Key"] = settings.WA_API_TOKEN
        headers["apikey"] = settings.WA_API_TOKEN
        headers["Authorization"] = f"Bearer {settings.WA_API_TOKEN}"
    
    # Timeout 10 detik agar tidak hang jika server WA API mati
    timeout = httpx.Timeout(10.0)
    
    logger.info(f"Mengirim payload ke WAHA: {payload}")
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(WA_API_URL, json=payload, headers=headers)
            
            # Raise exception jika HTTP status code bukan 2xx
            response.raise_for_status()
            
            logger.info(f"Berhasil mengirim notifikasi WA ke grup {K3_GROUP_ID}")
            
    except httpx.HTTPStatusError as e:
        logger.error(
            f"Gagal mengirim notifikasi WA. HTTP Error: {e.response.status_code} - {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"Gagal mengirim notifikasi WA. Koneksi bermasalah: {e}")
    except Exception as e:
        logger.error(f"Terjadi error tidak terduga saat mengirim WA: {e}")
