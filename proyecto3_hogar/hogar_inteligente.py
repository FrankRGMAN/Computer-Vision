"""
Proyecto 3 - Sistema de Reconocimiento Facial para Hogares Inteligentes
Módulo: Sistema principal del hogar inteligente
Detecta quién entra al hogar y activa automáticamente sus preferencias personalizadas.
"""
import cv2
import os
import json
from deepface import DeepFace

RESIDENTES_DIR = "residentes"
PERFILES_JSON = "perfiles.json"


def cargar_perfiles() -> dict:
    if os.path.exists(PERFILES_JSON):
        with open(PERFILES_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# ──────────────────────────────────────────────
# Acciones del hogar por perfil
# ──────────────────────────────────────────────

def activar_modo_adulto(nombre: str):
    print(f"\n🏠 ¡Bienvenido a casa, {nombre}!")
    print("   🎵 Reproduciendo: Playlist relajante de jazz suave...")
    print("   💡 Ajustando iluminación → 60% de intensidad, tono cálido (3000K)...")
    print("   🌡️  Configurando temperatura → 22°C...")
    print("   📺 Encendiendo TV → Noticias del día...")
    print("   🔒 Activando privacidad en ventanas inteligentes...")
    print("   ☕ Iniciando cafetera automática...")


def activar_modo_nino(nombre: str):
    print(f"\n🏠 ¡Hola, {nombre}! ¡Bienvenido!")
    print("   🎮 Activando modo entretenimiento infantil...")
    print("   🎵 Reproduciendo: Canciones infantiles y cuentos...")
    print("   💡 Ajustando iluminación → 100%, colores brillantes y cálidos...")
    print("   🌡️  Configurando temperatura → 24°C...")
    print("   📺 Encendiendo TV → Contenido educativo y caricaturas...")
    print("   🔒 Activando control parental en todos los dispositivos...")
    print("   🚫 Bloqueando contenido no apto para menores...")


def activar_modo_desconocido():
    print("\n⚠️  PERSONA NO RECONOCIDA DETECTADA")
    print("   🚨 Activando protocolo de seguridad...")
    print("   💡 Iluminación al máximo (100%)...")
    print("   📸 Capturando foto para registro de visitantes...")
    print("   🔔 Enviando notificación push al propietario...")
    print("   🔒 Bloqueando acceso a áreas restringidas...")
    print("   📞 Preparando llamada de verificación...")


def analizar_visitante_desconocido(frame):
    """Usa DeepFace.analyze para obtener información del visitante desconocido."""
    temp_path = "temp_visitante.jpg"
    cv2.imwrite(temp_path, frame)
    try:
        analisis = DeepFace.analyze(
            img_path=temp_path,
            actions=["age", "gender", "emotion"],
            enforce_detection=False,
            silent=True
        )
        if analisis:
            a = analisis[0]
            edad = a.get("age", "?")
            genero = a.get("dominant_gender", "?")
            emocion = a.get("dominant_emotion", "?")
            print(f"\n   📊 Análisis biométrico del visitante:")
            print(f"      → Edad estimada : {edad} años")
            print(f"      → Género        : {genero}")
            print(f"      → Estado de ánimo: {emocion}")
            # Sugerencia automática basada en edad estimada
            if isinstance(edad, int) and edad < 18:
                print("   💡 Sugerencia: Podría ser un menor. Activando restricciones adicionales...")
    except Exception as e:
        print(f"   ⚠️  No se pudo analizar el visitante: {e}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ──────────────────────────────────────────────
# Sistema principal
# ──────────────────────────────────────────────

def hogar_inteligente():
    perfiles = cargar_perfiles()
    tiene_residentes = (
        os.path.exists(RESIDENTES_DIR) and
        len([f for f in os.listdir(RESIDENTES_DIR) if f.endswith(".jpg")]) > 0
    )

    print("\n🏠 Sistema de Hogar Inteligente - Iniciado")
    if not tiene_residentes:
        print("⚠️  Sin residentes registrados. Ejecuta registrar_residente.py primero.")
        print("    El sistema operará en modo 'visitante desconocido'.")
    else:
        print(f"   Residentes activos: {', '.join(perfiles.keys())}")

    print("\nPresiona ESPACIO para detectar quién entra, ESC para apagar el sistema.\n")

    cap = cv2.VideoCapture(0)
    ultimo_reconocido = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        display = frame.copy()

        # HUD en pantalla
        cv2.rectangle(display, (0, 0), (display.shape[1], 80), (0, 0, 0), -1)
        cv2.putText(display, "HOGAR INTELIGENTE", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 200, 255), 2)
        estado = f"Ultimo detectado: {ultimo_reconocido}" if ultimo_reconocido else "Esperando deteccion..."
        cv2.putText(display, estado, (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(display, "ESPACIO: detectar | ESC: apagar", (10, display.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        cv2.imshow("Hogar Inteligente", display)
        key = cv2.waitKey(1)

        if key == 27:
            print("\n🏠 Sistema de hogar apagado. ¡Hasta luego!")
            break

        elif key == 32:
            print("\n🔍 Escaneando... por favor espera.")
            temp_path = "temp_hogar.jpg"
            cv2.imwrite(temp_path, frame)

            reconocido = False

            if tiene_residentes:
                try:
                    resultados = DeepFace.find(
                        img_path=temp_path,
                        db_path=RESIDENTES_DIR,
                        enforce_detection=False,
                        silent=True
                    )

                    if resultados and not resultados[0].empty:
                        ruta = resultados[0].iloc[0]["identity"]
                        nombre = os.path.splitext(os.path.basename(ruta))[0]
                        perfil = perfiles.get(nombre, {})
                        tipo = perfil.get("tipo", "adulto")
                        ultimo_reconocido = nombre
                        reconocido = True

                        if tipo == "adulto":
                            activar_modo_adulto(nombre)
                        else:
                            activar_modo_nino(nombre)

                except Exception as e:
                    print(f"⚠️  Error en reconocimiento: {e}")

            if not reconocido:
                ultimo_reconocido = "Desconocido"
                activar_modo_desconocido()
                analizar_visitante_desconocido(frame)

            if os.path.exists(temp_path):
                os.remove(temp_path)

            print("\n" + "─" * 50)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    hogar_inteligente()
