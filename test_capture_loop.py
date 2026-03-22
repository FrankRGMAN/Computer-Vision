import cv2, time, os
os.makedirs("test_frames", exist_ok=True)
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
time.sleep(1)
if not cap.isOpened():
    print("No se pudo abrir la cámara (VideoCapture falló).")
    raise SystemExit(1)
print("Cámara abierta. Guardando 5 frames, 1 por segundo...")
for i in range(5):
    ret, frame = cap.read()
    if not ret:
        print(f"Frame {i} no capturado (ret=False).")
        break
    filename = f"test_frames/frame_{i:02d}.jpg"
    cv2.imwrite(filename, frame)
    print("Guardado:", filename)
    cv2.imshow("Prueba", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    time.sleep(1)
cap.release()
cv2.destroyAllWindows()
print("Fin prueba.")
