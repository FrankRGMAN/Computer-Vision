#!/usr/bin/env python3
"""
src/asistencia.py

Sistema de asistencia con DeepFace:
- Usa cámara índice 1 (EVCAM) por defecto.
- Extrae la cara con mtcnn/retinaface (según disponibilidad) y verifica sobre la cara recortada.
- Guarda captura de la cara en captures/ y registra en asistencia.csv.
- Evita registros duplicados por día y añade cooldown.
- Guarda frames de diagnóstico cuando no se detecta cara.
"""

import os
import time
import cv2
import datetime
import traceback
import numpy as np
import pandas as pd
from deepface import DeepFace

# ------------------------------
# CONFIGURACIÓN
# ------------------------------
ARCHIVO_ASISTENCIA = "asistencia.csv"
CARPETA_CAPTURAS = "captures"
os.makedirs(CARPETA_CAPTURAS, exist_ok=True)

CAMERA_INDEX = 1
CAMERA_BACKEND = cv2.CAP_DSHOW  # cambiar a cv2.CAP_MSMF si DSHOW falla
COOLDOWN_SEGUNDOS = 2

# Detector preferido: mtcnn funcionó bien en tus pruebas; retinaface también es válido.
DETECTOR_PREFERIDO = "mtcnn"

# Usuarios: ajusta las rutas a tus imágenes en data/
usuarios = {
    "Frank": [
        "data/frank_1.jpg",
        "data/frank_2.jpg",
        "data/frank_3.jpg",
        "data/frank_4.jpg",
        "data/frank_5.jpg",
        "data/frank_6.jpg",
        "data/frank_7.jpg"
    ]
}

# ------------------------------
# CARGAR O CREAR CSV
# ------------------------------
try:
    asistencia = pd.read_csv(ARCHIVO_ASISTENCIA)
    for c in ["Nombre", "Fecha", "Hora", "Foto"]:
        if c not in asistencia.columns:
            asistencia[c] = ""
    asistencia = asistencia[["Nombre", "Fecha", "Hora", "Foto"]]
except FileNotFoundError:
    asistencia = pd.DataFrame(columns=["Nombre", "Fecha", "Hora", "Foto"])

# ------------------------------
# FUNCIONES AUXILIARES
# ------------------------------
def abrir_camara(index: int, backend):
    print(f"[INFO] Intentando abrir cámara índice={index} backend={backend}")
    cap = cv2.VideoCapture(index, backend)
    # Forzar resolución mayor para mejorar detección
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    time.sleep(1.5)
    if not cap.isOpened():
        print("[WARN] VideoCapture.isOpened() -> False")
        return None
    print("[INFO] Cámara abierta correctamente.")
    return cap

def _normalize_face_array(face_arr):
    """
    Normaliza un array de cara devuelto por DeepFace a BGR uint8.
    face_arr puede estar en rango 0..1 (float) o 0..255 (uint8), y en RGB.
    """
    try:
        if face_arr is None:
            return None
        arr = np.array(face_arr)
        if arr.size == 0:
            return None
        # Si valores en 0..1
        if arr.max() <= 1.0:
            arr = (arr * 255).astype("uint8")
        else:
            arr = arr.astype("uint8")
        # Convertir RGB -> BGR para OpenCV
        try:
            bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        except Exception:
            bgr = arr
        return bgr
    except Exception:
        return None

def extraer_cara_desde_frame(frame_bgr, detector_backend=DETECTOR_PREFERIDO):
    """
    Versión directa: usa DeepFace.detectFace sobre el array 'frame' (igual que debug_detect_live).
    Devuelve face_bgr (numpy uint8) o None si no se detecta.
    """
    try:
        # Intentar detectFace directamente con el array (igual que en debug)
        face_rgb = DeepFace.detectFace(frame_bgr, detector_backend=detector_backend, enforce_detection=False)
        arr = np.array(face_rgb)
        if arr.max() <= 1.0:
            arr = (arr * 255).astype("uint8")
        else:
            arr = arr.astype("uint8")
        try:
            face_bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        except Exception:
            face_bgr = arr
        return face_bgr
    except Exception as e:
        ts = int(time.time())
        diag_path = os.path.join(CARPETA_CAPTURAS, f"diag_no_face_{ts}.jpg")
        try:
            cv2.imwrite(diag_path, frame_bgr)
            print(f"[DIAG] detectFace no encontró cara. Frame guardado en {diag_path}")
        except Exception:
            print("[DIAG] No se pudo guardar frame de diagnóstico.")
        print(f"[WARN] detectFace falló: {e}")
        return None

# ------------------------------
# INICIALIZAR CÁMARA
# ------------------------------
cap = abrir_camara(CAMERA_INDEX, CAMERA_BACKEND)
if cap is None:
    print("[INFO] Probando backend MSMF...")
    cap = abrir_camara(CAMERA_INDEX, cv2.CAP_MSMF)
    if cap is None:
        print("[ERROR] No se pudo abrir la cámara. Revisa índice/backend y que ninguna otra app la use.")
        raise SystemExit(1)

print("Presiona 'q' para salir del sistema de asistencia...")

# ------------------------------
# CONTROL DE REGISTROS
# ------------------------------
registrados_en_sesion = set()

# ------------------------------
# LOOP PRINCIPAL
# ------------------------------
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARN] ret=False al leer frame. Reintentando en 0.5s...")
            time.sleep(0.5)
            continue

        # Mostrar el frame
        cv2.imshow("Sistema de Asistencia", frame)

        fecha_hoy = datetime.date.today().strftime("%Y-%m-%d")

        for nombre, fotos in usuarios.items():
            # Saltar si ya registrado hoy
            ya_registrado_hoy = ((asistencia['Nombre'] == nombre) & (asistencia['Fecha'] == fecha_hoy)).any()
            if ya_registrado_hoy or (nombre in registrados_en_sesion):
                continue

            # Extraer cara (usando detectFace directo)
            face_bgr = extraer_cara_desde_frame(frame, detector_backend=DETECTOR_PREFERIDO)

            if face_bgr is None:
                # No se detectó cara en este frame; continuar con siguiente iteración
                continue

            # Guardar cara recortada temporal para inspección
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            face_temp_path = os.path.join(CARPETA_CAPTURAS, f"face_tmp_{nombre}_{timestamp}.jpg")
            try:
                cv2.imwrite(face_temp_path, face_bgr)
            except Exception as e:
                print(f"[WARN] No se pudo guardar cara temporal: {e}")
                face_temp_path = None

            # Verificar la cara recortada contra cada foto de referencia
            verificado = False
            for foto_ref in fotos:
                try:
                    resultado = DeepFace.verify(face_temp_path if face_temp_path else frame,
                                                foto_ref,
                                                enforce_detection=False,
                                                detector_backend=DETECTOR_PREFERIDO,
                                                distance_metric='cosine')
                except Exception as e:
                    print(f"[WARN] DeepFace.verify lanzó excepción con {foto_ref}: {e}")
                    resultado = None

                print(f"[DEBUG] Verificando {nombre} vs {os.path.basename(foto_ref)} -> {resultado}")

                # Umbral más permisivo: usar distance en vez de solo 'verified'
                if resultado:
                    dist = resultado.get("distance", 1.0)
                    thresh = resultado.get("threshold", 0.68)
                    print(f"[DEBUG] distance={dist:.4f} threshold={thresh:.4f}")
                    if dist < 0.75:   # umbral ajustable; 0.75 es más permisivo
                        hora = datetime.datetime.now().strftime("%H:%M:%S")
                        nombre_archivo = f"{nombre}_{fecha_hoy}_{hora.replace(':','-')}.jpg"
                        ruta_foto = os.path.join(CARPETA_CAPTURAS, nombre_archivo)
                        try:
                            cv2.imwrite(ruta_foto, face_bgr)
                        except Exception as e:
                            print(f"[WARN] No se pudo guardar la captura final: {e}")
                            ruta_foto = ""
                        nueva_fila = pd.DataFrame([[nombre, fecha_hoy, hora, ruta_foto]],
                                                  columns=["Nombre", "Fecha", "Hora", "Foto"])
                        asistencia = pd.concat([asistencia, nueva_fila], ignore_index=True)
                        try:
                            asistencia.to_csv(ARCHIVO_ASISTENCIA, index=False)
                        except Exception as e:
                            print(f"[WARN] Error guardando CSV: {e}")
                        print(f"[INFO] Asistencia registrada: {nombre} a las {hora} - foto: {ruta_foto}")
                        registrados_en_sesion.add(nombre)
                        verificado = True
                        time.sleep(COOLDOWN_SEGUNDOS)
                        break

            # si ya verificado, no verificar otros usuarios en este frame
            if verificado:
                break

        # Salir con 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[INFO] Salida solicitada por usuario.")
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    try:
        asistencia.to_csv(ARCHIVO_ASISTENCIA, index=False)
    except Exception:
        pass
    print("[INFO] Proceso finalizado. CSV guardado.")
