"""
Wrapper de FFmpeg para conversión de video con progreso en tiempo real.
"""

import os
import sys
import re
import subprocess
import threading
import time
from pathlib import Path
from typing import Callable, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ConversionResult:
    """Resultado de una conversión."""
    success: bool
    input_file: Path
    output_file: Path
    input_size: int
    output_size: int
    duration: float
    error_message: str = ""


@dataclass
class ConversionProgress:
    """Información de progreso de conversión."""
    percent: float
    speed: str
    fps: str
    eta: str
    current_time: float
    total_duration: float


def get_ffmpeg_path() -> str:
    """
    Obtiene la ruta al ejecutable de FFmpeg.
    Primero busca en la carpeta del ejecutable, luego en PATH.
    """
    # Si estamos en un ejecutable, buscar FFmpeg en varias ubicaciones
    if getattr(sys, 'frozen', False):
        exe_dir = Path(sys.executable).parent
        
        # Buscar en el directorio del ejecutable
        ffmpeg_local = exe_dir / "ffmpeg.exe"
        if ffmpeg_local.exists():
            return str(ffmpeg_local)
        
        # PyInstaller --onedir coloca los archivos en _internal/
        ffmpeg_internal = exe_dir / "_internal" / "ffmpeg.exe"
        if ffmpeg_internal.exists():
            return str(ffmpeg_internal)
        
        # También buscar en subcarpeta ffmpeg
        ffmpeg_subfolder = exe_dir / "ffmpeg" / "ffmpeg.exe"
        if ffmpeg_subfolder.exists():
            return str(ffmpeg_subfolder)
        
        # Subcarpeta ffmpeg dentro de _internal
        ffmpeg_internal_subfolder = exe_dir / "_internal" / "ffmpeg" / "ffmpeg.exe"
        if ffmpeg_internal_subfolder.exists():
            return str(ffmpeg_internal_subfolder)
    else:
        # En desarrollo, buscar en carpeta ffmpeg local
        script_dir = Path(__file__).parent
        ffmpeg_local = script_dir / "ffmpeg" / "ffmpeg.exe"
        if ffmpeg_local.exists():
            return str(ffmpeg_local)
    
    # Usar FFmpeg del PATH
    return "ffmpeg"


def get_ffprobe_path() -> str:
    """Obtiene la ruta al ejecutable de FFprobe."""
    if getattr(sys, 'frozen', False):
        exe_dir = Path(sys.executable).parent
        
        # Buscar en el directorio del ejecutable
        ffprobe_local = exe_dir / "ffprobe.exe"
        if ffprobe_local.exists():
            return str(ffprobe_local)
        
        # PyInstaller --onedir coloca los archivos en _internal/
        ffprobe_internal = exe_dir / "_internal" / "ffprobe.exe"
        if ffprobe_internal.exists():
            return str(ffprobe_internal)
        
        # Subcarpeta ffmpeg
        ffprobe_subfolder = exe_dir / "ffmpeg" / "ffprobe.exe"
        if ffprobe_subfolder.exists():
            return str(ffprobe_subfolder)
        
        # Subcarpeta ffmpeg dentro de _internal
        ffprobe_internal_subfolder = exe_dir / "_internal" / "ffmpeg" / "ffprobe.exe"
        if ffprobe_internal_subfolder.exists():
            return str(ffprobe_internal_subfolder)
    else:
        script_dir = Path(__file__).parent
        ffprobe_local = script_dir / "ffmpeg" / "ffprobe.exe"
        if ffprobe_local.exists():
            return str(ffprobe_local)
    
    return "ffprobe"


def check_ffmpeg_available() -> Tuple[bool, str]:
    """
    Verifica si FFmpeg está disponible.
    
    Returns:
        Tupla (disponible, mensaje)
    """
    ffmpeg = get_ffmpeg_path()
    try:
        result = subprocess.run(
            [ffmpeg, "-version"],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        if result.returncode == 0:
            # Extraer versión
            version_match = re.search(r'ffmpeg version (\S+)', result.stdout)
            version = version_match.group(1) if version_match else "desconocida"
            return True, f"FFmpeg versión {version}"
        else:
            return False, "FFmpeg no responde correctamente"
    except FileNotFoundError:
        return False, "FFmpeg no encontrado. Asegúrate de que esté instalado y en el PATH."
    except Exception as e:
        return False, f"Error al verificar FFmpeg: {str(e)}"


def get_video_duration(input_file: Path) -> float:
    """
    Obtiene la duración del video en segundos usando FFprobe.
    
    Args:
        input_file: Ruta al archivo de video
    
    Returns:
        Duración en segundos, o 0 si no se puede determinar
    """
    ffprobe = get_ffprobe_path()
    try:
        result = subprocess.run(
            [
                ffprobe,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(input_file)
            ],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())
    except Exception:
        pass
    return 0


def parse_ffmpeg_progress(line: str, total_duration: float) -> Optional[ConversionProgress]:
    """
    Parsea una línea de salida de FFmpeg para extraer información de progreso.
    
    Args:
        line: Línea de stderr de FFmpeg
        total_duration: Duración total del video en segundos
    
    Returns:
        ConversionProgress o None si no se puede parsear
    """
    # Buscar patrón de tiempo: time=00:01:23.45
    time_match = re.search(r'time=(\d{2}):(\d{2}):(\d{2})\.(\d+)', line)
    if not time_match:
        return None
    
    hours = int(time_match.group(1))
    minutes = int(time_match.group(2))
    seconds = int(time_match.group(3))
    centiseconds = int(time_match.group(4)[:2]) if len(time_match.group(4)) >= 2 else 0
    
    current_time = hours * 3600 + minutes * 60 + seconds + centiseconds / 100
    
    # Calcular porcentaje
    if total_duration > 0:
        percent = (current_time / total_duration) * 100
        percent = min(percent, 100)
    else:
        percent = 0
    
    # Buscar velocidad
    speed_match = re.search(r'speed=\s*([\d.]+)x', line)
    speed = f"{speed_match.group(1)}x" if speed_match else ""
    
    # Buscar FPS
    fps_match = re.search(r'fps=\s*([\d.]+)', line)
    fps = fps_match.group(1) if fps_match else ""
    
    # Calcular ETA
    eta = ""
    if total_duration > 0 and speed_match:
        try:
            speed_val = float(speed_match.group(1))
            if speed_val > 0:
                remaining_time = (total_duration - current_time) / speed_val
                if remaining_time > 0:
                    mins = int(remaining_time // 60)
                    secs = int(remaining_time % 60)
                    eta = f"{mins:02d}:{secs:02d}"
        except ValueError:
            pass
    
    return ConversionProgress(
        percent=percent,
        speed=speed,
        fps=fps,
        eta=eta,
        current_time=current_time,
        total_duration=total_duration
    )


def convert_video(
    input_file: Path,
    output_file: Path,
    preset: str = "medium",
    crf: int = 23,
    audio_bitrate: str = "128k",
    progress_callback: Optional[Callable[[ConversionProgress], None]] = None
) -> ConversionResult:
    """
    Convierte un video AVI a MP4 usando H.264.
    
    Args:
        input_file: Archivo de entrada (.avi)
        output_file: Archivo de salida (.mp4)
        preset: Preset de codificación (ultrafast, fast, medium, slow, slower)
        crf: Constant Rate Factor (0-51, menor = mejor calidad)
        audio_bitrate: Bitrate del audio
        progress_callback: Función llamada con actualizaciones de progreso
    
    Returns:
        ConversionResult con el resultado de la conversión
    """
    start_time = time.time()
    input_size = input_file.stat().st_size
    
    # Obtener duración del video
    total_duration = get_video_duration(input_file)
    
    ffmpeg = get_ffmpeg_path()
    
    # Construir comando FFmpeg
    cmd = [
        ffmpeg,
        "-y",  # Sobrescribir sin preguntar
        "-i", str(input_file),
        "-c:v", "libx264",
        "-preset", preset,
        "-crf", str(crf),
        "-c:a", "aac",
        "-b:a", audio_bitrate,
        "-movflags", "+faststart",  # Optimizar para streaming
        "-progress", "pipe:1",  # Salida de progreso a stdout
        "-nostats",  # No mostrar stats normales
        str(output_file)
    ]
    
    try:
        # Ejecutar FFmpeg
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        # Variables para tracking
        last_progress = None
        error_output = []
        
        def read_stderr():
            if process.stderr is None:
                return
            for line in process.stderr:
                error_output.append(line)
                if progress_callback:
                    progress = parse_ffmpeg_progress(line, total_duration)
                    if progress:
                        progress_callback(progress)
        
        stderr_thread = threading.Thread(target=read_stderr)
        stderr_thread.daemon = True
        stderr_thread.start()
        
        # Leer stdout (progress)
        if process.stdout is None:
            process.wait()
            stderr_thread.join(timeout=5)
            return ConversionResult(
                success=False,
                input_file=input_file,
                output_file=output_file,
                input_size=input_size,
                output_size=0,
                duration=time.time() - start_time,
                error_message="No se pudo leer la salida de FFmpeg"
            )
        
        for line in process.stdout:
            if line.startswith('out_time='):
                # Parsear tiempo de progreso
                time_str = line.split('=')[1].strip()
                if time_str and time_str != 'N/A':
                    try:
                        parts = time_str.split(':')
                        if len(parts) >= 3:
                            hours = int(parts[0])
                            minutes = int(parts[1])
                            seconds = float(parts[2])
                            current_time = hours * 3600 + minutes * 60 + seconds
                            
                            if total_duration > 0 and progress_callback:
                                percent = min((current_time / total_duration) * 100, 100)
                                progress = ConversionProgress(
                                    percent=percent,
                                    speed="",
                                    fps="",
                                    eta="",
                                    current_time=current_time,
                                    total_duration=total_duration
                                )
                                last_progress = progress
                                progress_callback(progress)
                    except (ValueError, IndexError):
                        pass
            elif line.startswith('speed='):
                speed_val = line.split('=')[1].strip()
                if last_progress and speed_val and speed_val != 'N/A':
                    last_progress.speed = speed_val
                    
                    # Calcular ETA
                    try:
                        speed_num = float(speed_val.replace('x', ''))
                        if speed_num > 0 and total_duration > 0:
                            remaining = (total_duration - last_progress.current_time) / speed_num
                            if remaining > 0:
                                mins = int(remaining // 60)
                                secs = int(remaining % 60)
                                last_progress.eta = f"{mins:02d}:{secs:02d}"
                    except ValueError:
                        pass
                    
                    if progress_callback:
                        progress_callback(last_progress)
            elif line.startswith('fps='):
                fps_val = line.split('=')[1].strip()
                if last_progress and fps_val and fps_val != 'N/A':
                    last_progress.fps = fps_val
        
        # Esperar a que termine
        process.wait()
        stderr_thread.join(timeout=5)
        
        duration = time.time() - start_time
        
        if process.returncode == 0 and output_file.exists():
            output_size = output_file.stat().st_size
            return ConversionResult(
                success=True,
                input_file=input_file,
                output_file=output_file,
                input_size=input_size,
                output_size=output_size,
                duration=duration
            )
        else:
            error_msg = ''.join(error_output[-10:]) if error_output else "Error desconocido"
            # Limpiar archivo de salida parcial
            if output_file.exists():
                try:
                    output_file.unlink()
                except Exception:
                    pass
            
            return ConversionResult(
                success=False,
                input_file=input_file,
                output_file=output_file,
                input_size=input_size,
                output_size=0,
                duration=duration,
                error_message=error_msg.strip()
            )
    
    except Exception as e:
        duration = time.time() - start_time
        return ConversionResult(
            success=False,
            input_file=input_file,
            output_file=output_file,
            input_size=input_size,
            output_size=0,
            duration=duration,
            error_message=str(e)
        )
