# Computer Vision con DeepFace

Tres proyectos de visión por computadora desarrollados con **DeepFace** y **OpenCV**.  
Cada proyecto implementa reconocimiento o verificación facial en tiempo real usando la cámara del equipo.

---

## Requisitos previos

- Python 3.10 o superior
- Cámara web (integrada o USB)
- Windows / macOS / Linux

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/PinedaAlan/Computer-Vision.git
cd Computer-Vision

# 2. Crear entorno virtual
python -m venv venv

# Windows:
venv\Scripts\Activate.ps1

# macOS / Linux:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

> **Nota:** La primera ejecución descarga los modelos de DeepFace automáticamente (~600 MB).  
> Requiere conexión a internet. Los warnings de TensorFlow/oneDNN son normales y no afectan el funcionamiento.

---

## Proyecto 1 — Sistema de Asistencia Automatizada

Detecta y registra automáticamente la asistencia de personas reconociendo sus rostros  
en tiempo real a través de la cámara. Soporta múltiples personas. Los registros se  
guardan en `asistencia.csv` con nombre, fecha y hora. Evita duplicados por día.

**Características:**
- Base de datos dinámica: agrega personas sin modificar código
- Verificación con VGG-Face y ArcFace en paralelo
- Captura de evidencia fotográfica por cada registro
- Resumen del día al cerrar el sistema

### Ejecución

```bash
cd proyecto1_asistencia

# Paso 1: Registrar personas (repetir para cada persona)
python registrar.py
# → Ingresa el nombre cuando lo pida
# → Presiona ESPACIO para capturar (captura múltiples fotos para mayor precisión)

# Paso 2: Iniciar el sistema de asistencia
python tomar_asistencia.py
# → El sistema reconoce rostros automáticamente en tiempo real
# → Registra asistencia en asistencia.csv
# → Presiona 'q' para salir y ver el resumen del día
```

### Archivos generados
| Archivo / Carpeta | Descripción |
|---|---|
| `database/` | Fotos de referencia de cada persona |
| `captures/` | Capturas de evidencia por cada registro |
| `asistencia.csv` | Registro con columnas: Nombre, Fecha, Hora, Foto |

---

## Proyecto 2 — Sistema de Login con Verificación Facial

Autenticación biométrica que reemplaza las contraseñas. Compara el rostro en vivo  
contra la foto registrada del usuario. Incluye límite de intentos y bloqueo temporal.

**Características:**
- Verificación con DeepFace.verify (modelo VGG-Face)
- Feedback visual en pantalla: marco verde (acceso) / rojo (denegado)
- Máximo 3 intentos antes de bloqueo
- Muestra distancia facial para transparencia del resultado

### Ejecución

```bash
cd proyecto2_login

# Paso 1: Registrar al usuario (solo la primera vez)
python registrar_usuario.py
# → Ingresa el nombre de usuario
# → Presiona ESPACIO para capturar la foto biométrica

# Paso 2: Iniciar sesión
python iniciar_sesion.py
# → Presiona ESPACIO para verificar tu identidad
# → 3 intentos máximo antes de bloqueo temporal
# → ESC para cancelar
```

---

## Proyecto 3 — Hogar Inteligente con Reconocimiento Facial

Detecta quién entra al hogar y activa automáticamente preferencias personalizadas  
según el perfil del residente. Si detecta un desconocido, activa protocolo de seguridad  
y analiza atributos biométricos (edad estimada, género, emoción).

**Características:**
- Perfiles: Adulto (música relajante, iluminación cálida, cafetera) / Niño (control parental, caricaturas)
- Modo visitante desconocido con análisis automático via DeepFace.analyze
- Preferencias guardadas en `perfiles.json`
- HUD en tiempo real con último residente detectado

### Ejecución

```bash
cd proyecto3_hogar

# Paso 1: Registrar residentes (repetir para cada uno)
python registrar_residente.py
# → Ingresa nombre y tipo de perfil (1=Adulto, 2=Niño)
# → Presiona ESPACIO para capturar la foto

# Paso 2: Iniciar el sistema del hogar
python hogar_inteligente.py
# → Presiona ESPACIO cuando alguien entre al hogar
# → El sistema activa preferencias según el residente detectado
# → Desconocido → activa protocolo de seguridad + análisis biométrico
# → ESC para apagar el sistema
```

---

## Controles comunes

| Tecla | Acción |
|---|---|
| `ESPACIO` | Capturar foto / Verificar / Detectar |
| `q` | Salir (Proyecto 1) |
| `ESC` | Cancelar / Salir (Proyectos 2 y 3) |

---

## Tecnologías utilizadas

| Librería | Uso |
|---|---|
| [DeepFace](https://github.com/serengil/deepface) | Reconocimiento, verificación y análisis facial |
| [OpenCV](https://opencv.org/) | Captura de video y procesamiento de imágenes |
| [Pandas](https://pandas.pydata.org/) | Manejo del CSV de asistencia |
| TensorFlow / tf-keras | Backend de los modelos de DeepFace |

---

## Estructura del repositorio

```
Computer-Vision/
├── requirements.txt
├── README.md
├── proyecto1_asistencia/
│   ├── registrar.py            # Registrar personas en la base de datos
│   ├── tomar_asistencia.py     # Sistema de asistencia en tiempo real
│   ├── database/               # Fotos de referencia (generadas en ejecución)
│   └── captures/               # Evidencia fotográfica de asistencias
├── proyecto2_login/
│   ├── registrar_usuario.py    # Registrar usuario biométrico
│   ├── iniciar_sesion.py       # Login con verificación facial
│   └── usuario_registrado/     # Foto de referencia del usuario
└── proyecto3_hogar/
    ├── registrar_residente.py  # Registrar residentes del hogar
    ├── hogar_inteligente.py    # Sistema principal del hogar
    ├── perfiles.json           # Preferencias de cada residente
    └── residentes/             # Fotos de referencia de residentes
```

---

## Notas importantes

- El índice de cámara por defecto es `1` (cámara externa). Si usas cámara integrada, el sistema prueba automáticamente el índice `0`.
- Las fotos de personas no se suben al repositorio (`.gitignore`) por privacidad.
- En Windows, activar el entorno virtual requiere: `venv\Scripts\Activate.ps1`
