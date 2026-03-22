"""
Proyecto 2 - Sistema de Inicio de Sesión Seguro con Verificación Facial
Módulo: Registro de usuario
Captura y guarda la foto de referencia biométrica del usuario.
"""
import cv2
import os

USUARIO_DIR = "usuario_registrado"


def registrar_usuario(nombre_usuario: str):
    os.makedirs(USUARIO_DIR, exist_ok=True)
    ruta = os.path.join(USUARIO_DIR, f"{nombre_usuario}.jpg")

    cap = cv2.VideoCapture(0)
    print(f"\nRegistrando usuario: {nombre_usuario}")
    print("Asegúrate de estar bien iluminado y centrado.")
    print("Presiona ESPACIO para capturar, ESC para cancelar.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error al acceder a la cámara.")
            break

        cv2.putText(frame, "Centrate y presiona ESPACIO", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.imshow("Registro de Usuario", frame)
        key = cv2.waitKey(1)

        if key == 27:
            print("Registro cancelado.")
            break
        elif key == 32:
            cv2.imwrite(ruta, frame)
            print(f"✅ Usuario '{nombre_usuario}' registrado correctamente.")
            print(f"   Foto guardada en: {ruta}")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    nombre = input("Nombre de usuario a registrar: ").strip()
    if nombre:
        registrar_usuario(nombre)
    else:
        print("Nombre de usuario inválido.")
