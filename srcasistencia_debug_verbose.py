@"
#!/usr/bin/env python3
"""
src/asistencia_debug_verbose.py

Versión de diagnóstico muy verbosa de asistencia.py:
- Igual flujo que el sistema de asistencia.
- Logs detallados en cada paso de detección y verificación.
- Guarda caras temporales y frames de diagnóstico en captures/.
- No silencia excepciones: imprime stacktrace cuando ocurra.
"""
import os
import time
import cv2
import datetime
import traceback
import numpy as np
import pandas as pd
from deepface import DeepFace

# CONFIG
ARCHIVO_ASISTENCIA = "asistencia.csv"
CARPETA_CAPTURAS = "captures"
os.makedirs(CARPETA_CAPTURAS, exist_ok=True)

CAMERA_INDEX = 1
CAMERA_BACKEND = cv2.CAP_DSHOW
COOLDOWN_SEGUNDOS = 2
DETECTOR_PREFERIDO = "mtcnn"   # usa mtcnn por defecto (ajusta si quieres)

usuarios = {
    "Frank": [
        "data/frank_1.jpg",
        "data/frank_2.jpg",
        "data/frank_3.jpg"
    ]
}

# CARGAR CSV
try:
    asistencia = pd.read_csv(ARCHIVO_ASISTENCIA)
    for c in ["Nombre","Fecha","Hora","Foto"]:
        if c not in asistencia.columns:
            asistencia[c] = ""
    asistencia = asistencia[["Nombre","Fecha","Hora","Foto"]]
except FileNotFoundError:
    asistencia = pd.DataFrame(columns=["Nombre","Fecha","Hora","Foto"])

# FUNCIONES
def abrir_camara(index:int, backend):
    print(f"[INFO] Abrir cámara índice={index} backend={backend}")
    cap = cv2.VideoCapture(index, backend)
    # intentar forzar resolución
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    time.sleep(1.2)
    if not cap.isOpened():
        print("[ERROR] VideoCapture.isOpened() -> False")
        return None
    print("[INFO] Cámara abierta OK")
    return cap

def normalize_face_array(face_arr):
    if face_arr is None:
        return None
    arr = np.array(face_arr)
    if arr.size == 0:
        return None
    if arr.max() <= 1.0:
        arr = (arr * 255).astype("uint8")
    else:
        arr = arr.astype("uint8")
    try:
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    except Exception:
        bgr = arr
    return bgr

def detect_face_verbose(frame_bgr, detector_backend=DETECTOR_PREFERIDO):
    """
    Intenta detectar cara usando detectFace sobre el array (igual que debug_detect_live).
    Devuelve (face_bgr, info_str) o (None, error_str).
    """
    try:
        print(f"[DETECT] Llamando DeepFace.detectFace con backend={detector_backend}")
        face_rgb = DeepFace.detectFace(frame_bgr, detector_backend=detector_backend, enforce_detection=False)
        face_bgr = normalize_face_array(face_rgb)
        if face_bgr is None:
            raise ValueError("normalize_face_array devolvió None")
        print("[DETECT] detectFace devolvió una cara (array). Tamaño:", face_bgr.shape)
        return face_bgr, f"detected_by={detector_backend}"
    except Exception as e:
        tb = traceback.format_exc()
        print("[DETECT] detectFace falló:", e)
        print(tb)
        # guardar frame diagnóstico
        ts = int(time.time())
        diag = os.path.join(CARPETA_CAPTURAS, f"diag_no_face_{ts}.jpg")
        try:
            cv2.imwrite(diag, frame_bgr)
            print(f"[DIAG] Frame guardado para inspección: {diag}")
        except Exception as ee:
            print("[DIAG] No se pudo guardar frame diagnóstico:", ee)
        return None, str(e)

# INICIALIZAR
cap = abrir_camara(CAMERA_INDEX, CAMERA_BACKEND)
if cap is None:
    print("[INFO] Intentando backend MSMF...")
    cap = abrir_camara(CAMERA_INDEX, cv2.CAP_MSMF)
    if cap is None:
        raise SystemExit("[FATAL] No se pudo abrir la cámara")

print("[INFO] Presiona 'q' para salir. Presiona 'p' para forzar una verificación manual en el frame actual.")

registrados_en_sesion = set()

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARN] ret=False al leer frame. Reintentando...")
            time.sleep(0.5)
            continue

        # Mostrar
        cv2.imshow("Asistencia DEBUG", frame)

        # Tecla para forzar verificación manual (útil para comparar con debug_detect_live)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("[INFO] Salida solicitada por usuario.")
            break
        manual_trigger = (key == ord('p'))

        fecha_hoy = datetime.date.today().strftime("%Y-%m-%d")

        # Intentar detectar cara una vez por frame y reutilizar para todos los usuarios
        face_bgr, info = detect_face_verbose(frame, detector_backend=DETECTOR_PREFERIDO)
        if face_bgr is None:
            # intentar fallback a retinaface si mtcnn falla
            if DETECTOR_PREFERIDO != "retinaface":
                print("[DETECT] Intentando fallback detector retinaface")
                face_bgr, info2 = detect_face_verbose(frame, detector_backend="retinaface")
                if face_bgr is not None:
                    info = info2
        else:
            # guardar una copia temporal para inspección
            ts = int(time.time())
            tmp = os.path.join(CARPETA_CAPTURAS, f"face_live_tmp_{ts}.jpg")
            try:
                cv2.imwrite(tmp, face_bgr)
                print(f"[SAVE] Cara temporal guardada: {tmp}")
            except Exception as e:
                print("[WARN] No se pudo guardar cara temporal:", e)

        # Si no hay cara y no es trigger manual, saltar
        if face_bgr is None and not manual_trigger:
            # imprimir breve para no saturar
            print("[INFO] No se detectó cara en este frame.")
            continue

        # Si manual_trigger y no hay face_bgr, aún intentamos verificar usando frame completo
        if face_bgr is None and manual_trigger:
            print("[MANUAL] Forzando verificación usando frame completo (sin recorte).")

        # Para cada usuario, verificar (si ya registrado hoy, saltar)
        for nombre, fotos in usuarios.items():
            ya_reg = ((asistencia['Nombre'] == nombre) & (asistencia['Fecha'] == fecha_hoy)).any()
            if ya_reg or (nombre in registrados_en_sesion):
                print(f"[SKIP] {nombre} ya registrado hoy; saltando.")
                continue

            # Preparar imagen a verificar: cara recortada si existe, si no el frame completo
            img_to_verify_path = None
            if face_bgr is not None:
                ts = int(time.time())
                img_to_verify_path = os.path.join(CARPETA_CAPTURAS, f"face_for_verify_{nombre}_{ts}.jpg")
                cv2.imwrite(img_to_verify_path, face_bgr)
                print(f"[VERIFY] Usando cara recortada para verificar: {img_to_verify_path}")
            else:
                # guardar frame temporal
                ts = int(time.time())
                img_to_verify_path = os.path.join(CARPETA_CAPTURAS, f"frame_for_verify_{nombre}_{ts}.jpg")
                cv2.imwrite(img_to_verify_path, frame)
                print(f"[VERIFY] Usando frame completo para verificar: {img_to_verify_path}")

            # Verificar contra cada referencia
            for foto_ref in fotos:
                try:
                    print(f"[VERIFY] Llamando DeepFace.verify({os.path.basename(img_to_verify_path)}, {os.path.basename(foto_ref)})")
                    resultado = DeepFace.verify(img_to_verify_path,
                                                foto_ref,
                                                enforce_detection=False,
                                                detector_backend=DETECTOR_PREFERIDO,
                                                distance_metric='cosine')
                    print("[VERIFY] Resultado:", resultado)
                except Exception as e:
                    print("[ERROR] DeepFace.verify lanzó excepción:", e)
                    traceback.print_exc()
                    resultado = None

                if resultado:
                    dist = resultado.get("distance", 1.0)
                    thresh = resultado.get("threshold", 0.68)
                    print(f"[VERIFY] distance={dist:.4f} threshold={thresh:.4f}")
                    # umbral permisivo para debug
                    if dist < 0.75:
                        hora = datetime.datetime.now().strftime("%H:%M:%S")
                        nombre_archivo = f"{nombre}_{fecha_hoy}_{hora.replace(':','-')}.jpg"
                        ruta_foto = os.path.join(CARPETA_CAPTURAS, nombre_archivo)
                        try:
                            if face_bgr is not None:
                                cv2.imwrite(ruta_foto, face_bgr)
                            else:
                                cv2.imwrite(ruta_foto, frame)
                        except Exception as e:
                            print("[WARN] No se pudo guardar captura final:", e)
                            ruta_foto = ""
                        nueva_fila = pd.DataFrame([[nombre, fecha_hoy, hora, ruta_foto]],
                                                  columns=["Nombre","Fecha","Hora","Foto"])
                        asistencia = pd.concat([asistencia, nueva_fila], ignore_index=True)
                        asistencia.to_csv(ARCHIVO_ASISTENCIA, index=False)
                        print(f"[OK] Asistencia registrada: {nombre} a las {hora} - foto: {ruta_foto}")
                        registrados_en_sesion.add(nombre)
                        time.sleep(COOLDOWN_SEGUNDOS)
                        break
                    else:
                        print("[INFO] No cumple umbral; no registrado.")
                else:
                    print("[INFO] verify devolvió None o excepción; no registrado.")

            # si ya verificado, no verificar otros usuarios en este frame
            if nombre in registrados_en_sesion:
                break

finally:
    cap.release()
    cv2.destroyAllWindows()
    try:
        asistencia.to_csv(ARCHIVO_ASISTENCIA, index=False)
    except Exception:
        pass
    print("[INFO] Finalizado. CSV guardado.")
"@ > src\asistencia_debug_verbose.py
