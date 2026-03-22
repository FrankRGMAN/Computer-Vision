import cv2

for index in range(3):
    print(f"Probando cámara en índice {index}...")
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print(f"No se pudo abrir la cámara en índice {index}")
        continue

    ret, frame = cap.read()
    if not ret:
        print(f"No se pudo capturar frame en índice {index}")
        cap.release()
        continue

    print(f"¡Cámara encontrada en índice {index}! Mostrando imagen...")
    cv2.imshow(f"Camara {index}", frame)
    cv2.waitKey(3000)  # mostrar 3 segundos
    cap.release()
    cv2.destroyAllWindows()
