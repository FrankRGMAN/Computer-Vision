import cv2

# Lista de backends a probar
backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_VFW]

for backend in backends:
    print(f"Probando backend: {backend}")
    cap = cv2.VideoCapture(0, backend)

    if not cap.isOpened():
        print("No se pudo abrir la cámara con este backend")
        continue

    while True:
        ret, frame = cap.read()
        if not ret:
            print("No se pudo capturar frame")
            break

        cv2.imshow("Test Cam", frame)

        # Presiona 'q' para salir de la prueba
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()