"""
Proyecto 1 - Sistema de Asistencia Automatizada con Reconocimiento Facial
Módulo: Registro de personas
Captura una foto desde la cámara y la guarda en la base de datos de rostros.
"""
import cv2
import os

DATABASE_DIR = "database"


def registrar_persona(nombre: str):
    os.makedirs(DATABASE_DIR, exist_ok=True)

    cap = cv2.VideoCapture(0)
    print(f"\nRegistrando a: {nombre}")
    print("Presiona ESPACIO para capturar la foto, o ESC para cancelar.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: no se pudo acceder a la cámara.")
            break

        cv2.imshow("Registro - Presiona ESPACIO para capturar", frame)
        key = cv2.waitKey(1)

        if key == 27:  # ESC
            print("Registro cancelado.")
            break
        elif key == 32:  # ESPACIO
            ruta = os.path.join(DATABASE_DIR, f"{nombre}.jpg")
            cv2.imwrite(ruta, frame)
            print(f"✅ Foto guardada en: {ruta}")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    nombre = input("Ingresa el nombre de la persona a registrar: ").strip()
    if nombre:
        registrar_persona(nombre)
    else:
        print("Nombre inválido.")
