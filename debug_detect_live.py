# debug_detect_live.py
import cv2, time, os
from deepface import DeepFace

os.makedirs("captures", exist_ok=True)

CAM_IDX = 1
BACKEND = cv2.CAP_DSHOW  # cambia a cv2.CAP_MSMF si hace falta

cap = cv2.VideoCapture(CAM_IDX, BACKEND)
time.sleep(1)
if not cap.isOpened():
    print("No se pudo abrir la cámara. Prueba otro índice o backend.")
    raise SystemExit(1)

print("Presiona 'q' para salir. Presiona 's' para guardar la cara extraída actual.")
detector_order = ["retinaface", "mtcnn"]

while True:
    ret, frame = cap.read()
    if not ret:
        print("ret=False al leer frame. Reintentando...")
        time.sleep(0.5)
        continue

    cv2.imshow("Frame", frame)

    face_bgr = None
    for det in detector_order:
        try:
            face_rgb = DeepFace.detectFace(frame, detector_backend=det)  # acepta array o ruta
            # detectFace puede devolver array float 0..1 o BGR; normalizamos
            import numpy as np
            face_bgr = cv2.cvtColor((face_rgb * 255).astype("uint8"), cv2.COLOR_RGB2BGR)
            print(f"Detector exitoso: {det}")
            break
        except Exception as e:
            print(f"Detector {det} falló: {e}")
            face_bgr = None

    if face_bgr is not None:
        cv2.imshow("Cara extraida", face_bgr)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    if key == ord('s') and face_bgr is not None:
        ts = int(time.time())
        path = f"captures/face_debug_{ts}.jpg"
        cv2.imwrite(path, face_bgr)
        print("Guardada cara en:", path)

cap.release()
cv2.destroyAllWindows()
