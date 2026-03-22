"""
Proyecto 2 - Sistema de Inicio de Sesión Seguro con Verificación Facial
Módulo: Inicio de sesión biométrico
Verifica el rostro del usuario contra la foto registrada usando DeepFace.
"""
import cv2
import os
from deepface import DeepFace

USUARIO_DIR = "usuario_registrado"
MAX_INTENTOS = 3


def obtener_usuario_registrado():
    """Retorna (nombre, ruta_foto) del primer usuario registrado, o None."""
    if not os.path.exists(USUARIO_DIR):
        return None
    archivos = [f for f in os.listdir(USUARIO_DIR) if f.lower().endswith(".jpg")]
    if not archivos:
        return None
    nombre = os.path.splitext(archivos[0])[0]
    ruta = os.path.join(USUARIO_DIR, archivos[0])
    return nombre, ruta


def iniciar_sesion():
    usuario = obtener_usuario_registrado()
    if not usuario:
        print("❌ No hay usuarios registrados.")
        print("   Ejecuta primero: python registrar_usuario.py")
        return

    nombre_usuario, ruta_referencia = usuario
    print(f"\n🔐 Sistema de Login Biométrico")
    print(f"   Usuario: {nombre_usuario}")
    print(f"   Presiona ESPACIO para verificar tu identidad.")
    print(f"   Tienes {MAX_INTENTOS} intentos. ESC para cancelar.\n")

    cap = cv2.VideoCapture(0)
    intentos = 0
    acceso_concedido = False

    while intentos < MAX_INTENTOS:
        ret, frame = cap.read()
        if not ret:
            break

        display = frame.copy()
        intentos_restantes = MAX_INTENTOS - intentos
        cv2.putText(display, f"Usuario: {nombre_usuario}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        cv2.putText(display, f"Intentos restantes: {intentos_restantes}", (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
        cv2.putText(display, "ESPACIO: verificar | ESC: salir", (10, display.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.imshow("Login Facial", display)

        key = cv2.waitKey(1)

        if key == 27:
            print("\n🚪 Login cancelado.")
            break

        elif key == 32:
            print(f"\n🔍 Verificando identidad (intento {intentos + 1}/{MAX_INTENTOS})...")
            temp_path = "temp_login.jpg"
            cv2.imwrite(temp_path, frame)

            try:
                resultado = DeepFace.verify(
                    img1_path=temp_path,
                    img2_path=ruta_referencia,
                    enforce_detection=False
                )

                distancia = round(resultado["distance"], 4)

                if resultado["verified"]:
                    acceso_concedido = True
                    print(f"✅ Identidad verificada. (distancia facial: {distancia})")

                    # Mostrar confirmación en pantalla
                    cv2.rectangle(display, (0, 0), (display.shape[1], display.shape[0]),
                                  (0, 200, 0), 8)
                    cv2.putText(display, "ACCESO CONCEDIDO", (30, display.shape[0] // 2),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                    cv2.imshow("Login Facial", display)
                    cv2.waitKey(2000)

                    # Simular carga de sesión
                    print(f"\n🖥️  Iniciando sesión de {nombre_usuario}...")
                    print("   → Cargando perfil de usuario...")
                    print("   → Restaurando configuración personalizada...")
                    print("   → Sincronizando datos seguros...")
                    print(f"\n✅ ¡Bienvenido, {nombre_usuario}! Sesión iniciada exitosamente.\n")
                    break

                else:
                    intentos += 1
                    restantes = MAX_INTENTOS - intentos
                    print(f"❌ Rostro no coincide. (distancia facial: {distancia})")
                    if restantes > 0:
                        print(f"   Intentos restantes: {restantes}")

                    cv2.rectangle(display, (0, 0), (display.shape[1], display.shape[0]),
                                  (0, 0, 200), 8)
                    cv2.putText(display, "ACCESO DENEGADO", (30, display.shape[0] // 2),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
                    cv2.imshow("Login Facial", display)
                    cv2.waitKey(1500)

            except Exception as e:
                print(f"⚠️  No se detectó rostro claro. Intenta de nuevo. ({e})")

            if os.path.exists(temp_path):
                os.remove(temp_path)

    if not acceso_concedido and intentos >= MAX_INTENTOS:
        print(f"\n🔒 Cuenta bloqueada temporalmente tras {MAX_INTENTOS} intentos fallidos.")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    iniciar_sesion()
