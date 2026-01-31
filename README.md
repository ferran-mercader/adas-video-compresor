# AVI to MP4 Video Compressor

Convierte archivos de video `.avi` a `.mp4` (H.264) con progreso en tiempo real.

## 📥 Descarga

**[⬇️ Descargar última versión](https://github.com/ferran-mercader/adas-video-compresor/releases/latest)**

> El ejecutable es portable y no requiere instalación. Incluye FFmpeg.

## Características

- 🎬 Conversión de AVI a MP4 con códec H.264
- 📊 Progreso en tiempo real con barra visual
- 💾 Muestra espacio ahorrado tras la compresión
- 📁 Guarda videos convertidos en carpeta `output/`
- 🖥️ Ejecutable portable para Windows (no requiere instalación)

## Uso

### Opción 1: Ejecutable Windows (Recomendado)

1. Descarga `avi2mp4.zip` desde [Releases](https://github.com/ferran-mercader/adas-video-compresor/releases/latest)
2. Extrae el contenido
3. Coloca la carpeta `avi2mp4/` junto a tus videos `.avi`
4. Ejecuta `avi2mp4.exe`
5. Los videos convertidos aparecerán en `output/`

### Opción 2: Script Python

```bash
# Instalar dependencias (solo para desarrollo)
pip install -r requirements.txt

# Ejecutar
python main.py
```

## Crear el Ejecutable

```bash
# Esto descarga FFmpeg y crea el .exe
python build.py
```

El ejecutable se creará en `dist/avi2mp4/`.

## Configuración por Defecto

| Parámetro | Valor |
|-----------|-------|
| Preset | medium |
| CRF (calidad) | 23 |
| Códec video | libx264 (H.264) |
| Códec audio | AAC |
| Bitrate audio | 128k |

## Requisitos

- **Para el ejecutable**: Ninguno (todo incluido)
- **Para desarrollo**: Python 3.8+, FFmpeg en PATH

## Estructura del Proyecto

```
adas-video-compresor/
├── main.py          # Punto de entrada
├── converter.py     # Wrapper FFmpeg
├── progress.py      # Visualización
├── utils.py         # Utilidades
├── build.py         # Crear .exe
├── requirements.txt # Dependencias
└── output/          # Videos convertidos
```
