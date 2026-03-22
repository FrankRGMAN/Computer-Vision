#!/usr/bin/env python3
"""
proyecto3_hogar/registrar_residente.py
Registra residentes del hogar con perfil y preferencias personalizadas.
"""
import os, cv2, json, time

BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
RESIDENTES_DIR = os.path.join(BASE_DIR, "residentes")
PERFILES_JSON  = os.path.join(BASE_DIR, "perfiles.json")
CAMERA_INDEX   = 1
CAMERA_BACKEND = cv2.CAP_DSHOW

PREFERENCIAS = {
    "adulto": {
        "musica":"Jazz relajante / Lo-fi",
        "iluminacion":"60% — tono cálido 3000K",
        "temperatura":"22°C",
        "tv":"Noticias / Series",
        "extras":["Cafetera automática","Privacidad en ventanas"]
    },
    "niño": {
        "musica":"Canciones infantiles",
        "iluminacion":"100% — colores brillantes",
        "temperatura":"24°C",
        "tv":"Caricaturas / Educativo",
        "extras":["Control parental activo","Bloqueo contenido adulto"]
    }
}

def abrir_camara():
    for idx in [CAMERA_INDEX, 0]:
        cap = cv2.VideoCapture(idx, CAMERA_BACKEND)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
        time.sleep(1.0)
        if cap.isOpened(): return cap
        cap.release()
    return None

def cargar_perfiles():
    if os.path.exists(PERFILES_JSON):
        with open(PERFILES_JSON,"r",encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_perfiles(p):
    with open(PERFILES_JSON,"w",encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=2)

def registrar_residente(nombre, tipo):
    os.makedirs(RESIDENTES_DIR, exist_ok=True)
    ruta_foto = os.path.join(RESIDENTES_DIR, f"{nombre}.jpg")
    prefs = PREFERENCIAS.get(tipo, PREFERENCIAS["adulto"])
    cap = abrir_camara()
    if cap is None:
        print("[ERROR] No se pudo abrir la cámara.")
        return

    print(f"\n=== Registrando: {nombre} ({tipo}) ===")
    print(f"  Música       : {prefs['musica']}")
    print(f"  Iluminación  : {prefs['iluminacion']}")
    print(f"  Temperatura  : {prefs['temperatura']}")
    print(f"  TV           : {prefs['tv']}")
    print("\n  ESPACIO: capturar  |  ESC: cancelar\n")

    capturado = False
    while not capturado:
        ret, frame = cap.read()
        if not ret: continue
        display = frame.copy()
        h, w = display.shape[:2]
        cx, cy = w//2, h//2
        color = (0,200,255) if tipo=="adulto" else (0,255,180)
        cv2.ellipse(display,(cx,cy),(110,150),0,0,360,color,2)
        cv2.rectangle(display,(0,0),(w,55),(0,0,0),-1)
        cv2.putText(display,"HOGAR INTELIGENTE — Registro",(10,28),
                    cv2.FONT_HERSHEY_SIMPLEX,0.75,(255,200,0),2)
        cv2.putText(display,f"{nombre}  ({tipo.upper()})",(10,50),
                    cv2.FONT_HERSHEY_SIMPLEX,0.55,color,1)
        cv2.putText(display,"ESPACIO: capturar  |  ESC: cancelar",
                    (10,h-10),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),1)
        cv2.imshow("Registro Residente", display)
        key = cv2.waitKey(1)
        if key == 27:
            print("[INFO] Cancelado.")
            break
        elif key == 32:
            cv2.imwrite(ruta_foto, frame)
            capturado = True
            conf = frame.copy()
            cv2.rectangle(conf,(0,0),(conf.shape[1],conf.shape[0]),(0,200,255),10)
            cv2.putText(conf,f"BIENVENIDO, {nombre.upper()}",(w//2-180,h//2),
                        cv2.FONT_HERSHEY_SIMPLEX,1.1,(0,255,200),3)
            cv2.imshow("Registro Residente", conf)
            cv2.waitKey(1500)

    cap.release()
    cv2.destroyAllWindows()
    if capturado:
        perfiles = cargar_perfiles()
        perfiles[nombre] = {"tipo":tipo,"foto":ruta_foto,"preferencias":prefs}
        guardar_perfiles(perfiles)
        print(f"\n[OK] Residente '{nombre}' registrado como '{tipo}'.")

def listar_residentes():
    p = cargar_perfiles()
    if not p:
        print("  (sin residentes registrados)")
        return
    print(f"\n  Residentes ({len(p)}):")
    for n,d in p.items():
        print(f"    • {n:<15}  {d['tipo']}")

if __name__ == "__main__":
    print("╔══════════════════════════════════════════╗")
    print("║   HOGAR INTELIGENTE — REGISTRO           ║")
    print("╚══════════════════════════════════════════╝")
    listar_residentes()
    print()
    nombre = input("  Nombre del residente: ").strip()
    if not nombre:
        print("[ERROR] Nombre vacío.")
    else:
        print("\n  1 → Adulto  |  2 → Niño")
        opcion = input("  Selecciona (1/2): ").strip()
        tipo = "niño" if opcion == "2" else "adulto"
        registrar_residente(nombre, tipo)
