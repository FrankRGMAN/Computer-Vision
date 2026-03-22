#!/usr/bin/env python3
"""
proyecto1_asistencia/tomar_asistencia.py
Sistema de asistencia automática con reconocimiento facial.
Escanea database/ dinámicamente — reconoce cualquier persona registrada.
"""
import os, time, cv2, datetime
import numpy as np, pandas as pd
from deepface import DeepFace

BASE_DIR           = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR       = os.path.join(BASE_DIR, "database")
CARPETA_CAPTURAS   = os.path.join(BASE_DIR, "captures")
ARCHIVO_ASISTENCIA = os.path.join(BASE_DIR, "asistencia.csv")
CAMERA_INDEX       = 1
CAMERA_BACKEND     = cv2.CAP_DSHOW
COOLDOWN           = 3
DETECTOR           = "mtcnn"
MODELOS            = ["VGG-Face", "ArcFace"]
DISTANCE_METRIC    = "cosine"
UMBRALES           = {"VGG-Face": 0.68, "ArcFace": 0.40}

os.makedirs(CARPETA_CAPTURAS, exist_ok=True)

def construir_usuarios():
    usuarios = {}
    if not os.path.exists(DATABASE_DIR):
        return usuarios
    for f in sorted(os.listdir(DATABASE_DIR)):
        if not f.lower().endswith(".jpg"):
            continue
        sin_ext = os.path.splitext(f)[0]
        partes  = sin_ext.rsplit("_", 1)
        nombre  = partes[0] if len(partes)==2 and partes[1].isdigit() else sin_ext
        usuarios.setdefault(nombre, []).append(os.path.join(DATABASE_DIR, f))
    return usuarios

def cargar_csv():
    try:
        df = pd.read_csv(ARCHIVO_ASISTENCIA)
        for c in ["Nombre","Fecha","Hora","Foto"]:
            if c not in df.columns: df[c] = ""
        return df[["Nombre","Fecha","Hora","Foto"]]
    except FileNotFoundError:
        return pd.DataFrame(columns=["Nombre","Fecha","Hora","Foto"])

def ya_registrado(df, nombre, fecha):
    return not df[(df["Nombre"]==nombre)&(df["Fecha"]==fecha)].empty

def guardar_registro(df, nombre, fecha, hora, foto):
    nueva = pd.DataFrame([[nombre,fecha,hora,foto]], columns=["Nombre","Fecha","Hora","Foto"])
    df = pd.concat([df, nueva], ignore_index=True)
    df.to_csv(ARCHIVO_ASISTENCIA, index=False)
    return df

def abrir_camara():
    for idx in [CAMERA_INDEX, 0]:
        cap = cv2.VideoCapture(idx, CAMERA_BACKEND)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        time.sleep(1.5)
        if cap.isOpened():
            print(f"[INFO] Cámara abierta (índice {idx})")
            return cap
        cap.release()
    return None

def extraer_cara(frame):
    try:
        face_rgb = DeepFace.detectFace(frame, detector_backend=DETECTOR, enforce_detection=False)
        arr = np.array(face_rgb)
        if arr.max() <= 1.0: arr = (arr*255).astype("uint8")
        else: arr = arr.astype("uint8")
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"[WARN] detectFace: {e}")
        return None

def verificar(face_path, fotos_ref):
    mejor = {"dist":1.0,"modelo":"","ok":False}
    for modelo in MODELOS:
        dists = []
        for ref in fotos_ref:
            try:
                r = DeepFace.verify(face_path, ref,
                    enforce_detection=False, detector_backend=DETECTOR,
                    model_name=modelo, distance_metric=DISTANCE_METRIC)
                dists.append(r.get("distance",1.0))
            except Exception: pass
        if not dists: continue
        d = min(dists)
        thresh = UMBRALES.get(modelo, 0.68)
        print(f"  [{modelo}] dist={d:.4f} umbral={thresh}")
        if d < mejor["dist"]:
            mejor = {"dist":d,"modelo":modelo,"ok": d < thresh}
        if d < thresh:
            return True, d, modelo
    return mejor["ok"], mejor["dist"], mejor["modelo"]

def main():
    usuarios = construir_usuarios()
    if not usuarios:
        print("[ERROR] Base de datos vacía. Ejecuta primero: python registrar.py")
        return

    print(f"[INFO] Personas detectadas: {', '.join(usuarios.keys())}")
    df = cargar_csv()
    registrados = set()
    cap = abrir_camara()
    if cap is None:
        print("[ERROR] No se pudo abrir ninguna cámara.")
        return

    print("Sistema activo. Presiona 'q' para salir.\n")
    ultimo_msg = "Esperando rostro..."
    color_msg  = (180, 180, 180)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.3)
                continue

            display    = frame.copy()
            h, w       = display.shape[:2]
            fecha_hoy  = datetime.date.today().strftime("%Y-%m-%d")

            # HUD
            cv2.rectangle(display, (0,0), (w,80), (0,0,0), -1)
            cv2.putText(display, "SISTEMA DE ASISTENCIA", (10,32),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,200,255), 2)
            cv2.putText(display, ultimo_msg, (10,65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_msg, 2)
            cv2.putText(display, f"q: salir  |  {fecha_hoy}", (10, h-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150,150,150), 1)
            # Lista registrados en sesión
            y = 95
            for reg in sorted(registrados):
                cv2.putText(display, f"  OK: {reg}", (10, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,220,80), 1)
                y += 22

            cv2.imshow("Sistema de Asistencia", display)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            for nombre, fotos in usuarios.items():
                if ya_registrado(df, nombre, fecha_hoy) or nombre in registrados:
                    continue
                cara = extraer_cara(frame)
                if cara is None:
                    continue
                ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                tmp = os.path.join(CARPETA_CAPTURAS, f"tmp_{ts}.jpg")
                cv2.imwrite(tmp, cara)
                print(f"\n[INFO] Verificando: {nombre}...")
                ok, dist, modelo = verificar(tmp, fotos)
                if os.path.exists(tmp): os.remove(tmp)
                if ok:
                    hora = datetime.datetime.now().strftime("%H:%M:%S")
                    nombre_foto = f"{nombre}_{fecha_hoy}_{hora.replace(':','-')}.jpg"
                    ruta_captura = os.path.join(CARPETA_CAPTURAS, nombre_foto)
                    cv2.imwrite(ruta_captura, cara)
                    df = guardar_registro(df, nombre, fecha_hoy, hora, ruta_captura)
                    registrados.add(nombre)
                    print(f"[OK] {nombre} | {hora} | {modelo} | dist={dist:.4f}")
                    ultimo_msg = f"OK: {nombre} — {hora}"
                    color_msg  = (0, 220, 80)
                    time.sleep(COOLDOWN)
                    break
                else:
                    ultimo_msg = f"No reconocido (dist={dist:.3f})"
                    color_msg  = (0, 100, 255)
    finally:
        cap.release()
        cv2.destroyAllWindows()
        df.to_csv(ARCHIVO_ASISTENCIA, index=False)
        print("\n[INFO] Resumen del día:")
        hoy = datetime.date.today().strftime("%Y-%m-%d")
        hoy_df = df[df["Fecha"]==hoy][["Nombre","Hora"]]
        print("  Sin registros." if hoy_df.empty else hoy_df.to_string(index=False))

if __name__ == "__main__":
    main()
