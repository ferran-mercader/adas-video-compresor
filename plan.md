# Plan: AVI to MP4 Video Compressor

Script de Python que usa `subprocess` + FFmpeg para convertir videos `.avi` a `.mp4` (H.264) de forma eficiente. Ideal para archivos grandes (varios GB) porque no carga videos en RAM y muestra progreso en tiempo real.

---

## 📋 Tareas MVP (Primera Vuelta)

### 1. Estructura del Proyecto
- [ ] Crear módulos separados:
  - `main.py` → Punto de entrada CLI
  - `converter.py` → Wrapper de FFmpeg
  - `progress.py` → Visualización de progreso
  - `utils.py` → Descubrimiento de archivos

### 2. Descubrimiento de Archivos (`utils.py`)
- [ ] Escanear directorio actual por archivos `.avi`
- [ ] Validar que los archivos existan y sean accesibles
- [ ] Crear carpeta `output/` si no existe
- [ ] Mostrar lista de videos detectados con tamaño

### 3. Wrapper de FFmpeg (`converter.py`)
- [ ] Implementar conversión con subprocess
- [ ] Comando base: `ffmpeg -i input.avi -c:v libx264 -preset medium -crf 23 -c:a aac -b:a 128k output.mp4`
- [ ] Parsear salida de FFmpeg para obtener progreso en tiempo real
- [ ] Manejar errores de conversión

### 4. Visualización de Progreso (`progress.py`)
- [ ] Mostrar lista de videos detectados al inicio
- [ ] Barra de progreso por archivo actual
- [ ] Porcentaje completado del batch total
- [ ] Tiempo estimado restante

### 5. Integración CLI (`main.py`)
- [ ] Mostrar videos detectados al ejecutar
- [ ] Confirmar antes de iniciar conversión
- [ ] Orquestar conversión con feedback visual
- [ ] Mostrar resumen al finalizar (archivos convertidos, espacio ahorrado, tiempo total)

### 6. Ejecutable Windows 🆕
- [ ] Usar PyInstaller para crear `.exe` standalone
- [ ] Incluir FFmpeg embebido (ffmpeg.exe estático)
- [ ] Script de build automatizado
- [ ] No requiere instalación de Python ni FFmpeg por el usuario

---

## ⚙️ Configuración por Defecto

| Parámetro | Valor |
|-----------|-------|
| Preset | `medium` |
| CRF (calidad) | `23` |
| Codec video | `libx264` (H.264) |
| Codec audio | `aac` |
| Bitrate audio | `128k` |
| Carpeta salida | `output/` |

---

## 🚀 Features Extras (Segunda Vuelta)

| Feature | Prioridad | Descripción |
|---------|-----------|-------------|
| **Skip ya convertidos** | Alta | Verificar si output existe para reanudar batches |
| **Presets CLI** | Alta | `--preset ultrafast/fast/medium/slow` |
| **Control CRF** | Media | `--crf N` configurable (18-28) |
| **Procesamiento paralelo** | Media | `--workers N` para múltiples videos simultáneos |
| **Modo dry-run** | Media | `--dry-run` listar sin convertir |
| **Log de errores** | Alta | Continuar batch si un archivo falla |
| **Borrar originales** | Baja | `--delete-originals` post-conversión |
| **Escalado resolución** | Baja | `--scale 720p` reducir tamaño |
| **Aceleración GPU** | Baja | Soporte NVENC/QuickSync |

---

## 📁 Estructura Final

```
adas-video-compresor/
├── main.py              # Entry point CLI
├── converter.py         # FFmpeg wrapper
├── progress.py          # Barras de progreso
├── utils.py             # Utilidades archivos
├── build.py             # Script para crear .exe
├── ffmpeg/              # FFmpeg estático (para build)
│   └── ffmpeg.exe
├── output/              # Videos convertidos
├── dist/                # Ejecutable generado
│   └── avi2mp4.exe
├── requirements.txt     # Dependencias
└── plan.md              # Este archivo
```

---

## 🔧 Comando FFmpeg Base

```bash
ffmpeg -i input.avi -c:v libx264 -preset medium -crf 23 -c:a aac -b:a 128k -progress pipe:1 output.mp4
```

---

## 📝 Notas

- FFmpeg se incluirá como binario estático en el ejecutable
- El ejecutable será portable (no requiere instalación)
- Probado para archivos de varios GB
