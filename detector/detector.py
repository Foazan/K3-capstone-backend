import cv2
import requests
import time
import os
from ultralytics import YOLO

# Konfigurasi Path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(SCRIPT_DIR, "best.pt")

# URL Stream Menggunakan ESP32-CAM
# STREAM_URL = "http://192.168.1.200:81/stream"

#URL Testing Menggunakan Webcam
STREAM_URL = 0

# URL Endpoint Backend FastAPI
API_URL = "http://localhost:8000/api/violations/detect"

# ID Kamera
CAMERA_ID = 1
COOLDOWN_TIME = 10 
CONFIDENCE_THRESHOLD = 0.5

CLASS_NAMES = {
    0: "Tidak Pakai Helm",
    1: "Tidak Pakai Rompi",
    2: "Tidak Pakai Sarung Tangan"
}

# Optimasi Performa Agar Tidak Lag (Testing)
PROCESS_EVERY_N_FRAMES = 3
FRAME_WIDTH = 640

# Inisialisasi
print("[INFO] Memuat model YOLO...")
if not os.path.exists(MODEL_PATH):
    print(f"[ERROR] Model {MODEL_PATH} tidak ditemukan")
    exit(1)

model = YOLO(MODEL_PATH)

last_sent_time = {}

print(f"[INFO] Mencoba terhubung ke kamera: {STREAM_URL}")
cap = cv2.VideoCapture(STREAM_URL)

if not cap.isOpened():
    print("[ERROR] Tidak dapat terhubung ke kamera. Cek URL atau koneksi jaringan ESP32-CAM.")
    exit(1)

print("[INFO] Detektor berjalan. Tekan 'q' pada jendela video untuk berhenti.")

# Looping untuk Deteksi Realtime
frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("[WARNING] Gagal membaca frame dari stream kamera. Mencoba lagi...")
        time.sleep(1)
        continue

    frame_count += 1

    # Resize frame agar lebih ringan (Testing)
    height, width = frame.shape[:2]
    scale = FRAME_WIDTH / width
    frame = cv2.resize(frame, (FRAME_WIDTH, int(height * scale)))

    # Menjalankan YOLO tiap N frame
    if frame_count % PROCESS_EVERY_N_FRAMES != 0:
        cv2.imshow("K3 Violation Detector (YOLO)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[INFO] Menghentikan detektor...")
            break
        continue

    results = model(frame, verbose=False)
    
    current_time = time.time()

    for result in results:
        boxes = result.boxes
        for box in boxes:
            conf = float(box.conf[0])
            yolo_class_id = int(box.cls[0])

            # Mengabaikan class selain 0, 1, 2
            if yolo_class_id not in CLASS_NAMES:
                continue

            # Jika tingkat kepercayaan cukup tinggi
            if conf >= CONFIDENCE_THRESHOLD:
                # Cek logika anti-spam (cooldown) agar tidak spam 
                last_time = last_sent_time.get(yolo_class_id, 0)
                
                if (current_time - last_time) > COOLDOWN_TIME:
                    # Ambil nama label jika ada, kalau tidak ada pakai tulisan "Class X"
                    label_text = CLASS_NAMES.get(yolo_class_id, f"Class {yolo_class_id}")
                    
                    print(f"\n[ALERT] Pelanggaran terdeteksi! ({label_text}, Conf: {conf:.2f})")
                    
                    success, encoded_image = cv2.imencode('.jpg', frame)
                    if success:
                        image_bytes = encoded_image.tobytes()

                        data = {
                            "camera_id": str(CAMERA_ID),
                            "yolo_class_id": str(yolo_class_id)
                        }
                        files = {
                            "image": ("violation.jpg", image_bytes, "image/jpeg")
                        }

                        try:
                            print(f"[INFO] Mengirim data ke {API_URL} ...")
                            response = requests.post(API_URL, data=data, files=files, timeout=5)
                            
                            if response.status_code == 201:
                                print("[SUCCESS] Data pelanggaran berhasil dicatat di Backend!")
                            else:
                                print(f"[ERROR] API mengembalikan status: {response.status_code}")
                                print(response.text)
                                
                            # Update waktu terakhir dikirim agar tidak spam
                            last_sent_time[yolo_class_id] = current_time

                        except requests.exceptions.RequestException as e:
                            print(f"[ERROR] Gagal terhubung ke API: {e}")
                
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                
                label_text = CLASS_NAMES.get(yolo_class_id, f"Class {yolo_class_id}")
                cv2.putText(frame, f"{label_text} ({conf:.2f})", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    cv2.imshow("K3 Violation Detector (YOLO)", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("[INFO] Menghentikan detektor...")
        break

cap.release()
cv2.destroyAllWindows()
