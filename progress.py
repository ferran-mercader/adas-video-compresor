"""
Visualización de progreso para la conversión de videos.
"""

import os
import sys
from typing import List, Tuple, Optional
from pathlib import Path


# Códigos ANSI para colores (Windows 10+ soporta esto)
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RED = "\033[91m"
    GRAY = "\033[90m"


def enable_windows_ansi():
    """Habilita soporte ANSI en Windows."""
    if os.name == 'nt':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass


def clear_line():
    """Limpia la línea actual de la consola."""
    sys.stdout.write('\r' + ' ' * 80 + '\r')
    sys.stdout.flush()


def print_header():
    """Imprime el encabezado del programa."""
    enable_windows_ansi()
    print()
    print(f"{Colors.CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}║          AVI to MP4 Video Compressor (H.264)                 ║{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}")
    print()


def print_detected_files(files_info: List[Tuple[Path, str, int]]):
    """
    Muestra la lista de archivos detectados.
    
    Args:
        files_info: Lista de tuplas (path, tamaño_formateado, tamaño_bytes)
    """
    print(f"{Colors.YELLOW}{Colors.BOLD}📁 Videos AVI detectados:{Colors.RESET}")
    print(f"{Colors.GRAY}{'─' * 60}{Colors.RESET}")
    
    total_size = 0
    for i, (file, size_str, size_bytes) in enumerate(files_info, 1):
        total_size += size_bytes
        print(f"  {Colors.BLUE}{i:3}.{Colors.RESET} {file.name:<40} {Colors.GREEN}{size_str:>10}{Colors.RESET}")
    
    print(f"{Colors.GRAY}{'─' * 60}{Colors.RESET}")
    
    # Formatear tamaño total
    if total_size >= 1024 * 1024 * 1024:
        total_str = f"{total_size / (1024 * 1024 * 1024):.2f} GB"
    else:
        total_str = f"{total_size / (1024 * 1024):.2f} MB"
    
    print(f"  {Colors.BOLD}Total: {len(files_info)} archivos ({total_str}){Colors.RESET}")
    print()


def print_no_files_found():
    """Muestra mensaje cuando no se encuentran archivos."""
    print(f"{Colors.RED}{Colors.BOLD}❌ No se encontraron archivos .avi en el directorio actual.{Colors.RESET}")
    print()


def print_conversion_start(total_files: int):
    """Muestra mensaje de inicio de conversión."""
    print(f"{Colors.GREEN}{Colors.BOLD}🚀 Iniciando conversión de {total_files} archivo(s)...{Colors.RESET}")
    print()


def print_file_progress(current_file: int, total_files: int, filename: str):
    """Muestra el archivo actual siendo procesado."""
    print(f"{Colors.CYAN}[{current_file}/{total_files}]{Colors.RESET} Convirtiendo: {Colors.BOLD}{filename}{Colors.RESET}")


def format_time(seconds: float) -> str:
    """Formatea segundos a formato legible."""
    if seconds < 0:
        return "--:--"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def create_progress_bar(percent: float, width: int = 40) -> str:
    """
    Crea una barra de progreso visual.
    
    Args:
        percent: Porcentaje completado (0-100)
        width: Ancho de la barra en caracteres
    
    Returns:
        String con la barra de progreso
    """
    percent = max(0, min(100, percent))
    filled = int(width * percent / 100)
    empty = width - filled
    
    bar = f"{Colors.GREEN}{'█' * filled}{Colors.GRAY}{'░' * empty}{Colors.RESET}"
    return f"[{bar}] {percent:5.1f}%"


def print_progress(percent: float, speed: str = "", eta: str = "", fps: str = ""):
    """
    Actualiza la línea de progreso en tiempo real.
    
    Args:
        percent: Porcentaje completado
        speed: Velocidad de procesamiento
        eta: Tiempo estimado restante
        fps: Frames por segundo
    """
    bar = create_progress_bar(percent)
    
    info_parts = []
    if speed:
        info_parts.append(f"Vel: {speed}")
    if fps:
        info_parts.append(f"FPS: {fps}")
    if eta:
        info_parts.append(f"ETA: {eta}")
    
    info_str = " | ".join(info_parts)
    
    sys.stdout.write(f"\r  {bar} {Colors.GRAY}{info_str}{Colors.RESET}    ")
    sys.stdout.flush()


def print_file_complete(filename: str, output_size: str, time_taken: float, compression_ratio: Optional[float] = None):
    """Muestra mensaje de archivo completado."""
    clear_line()
    time_str = format_time(time_taken)
    
    msg = f"  {Colors.GREEN}✓{Colors.RESET} {filename} → {output_size} ({time_str})"
    if compression_ratio is not None:
        msg += f" [{Colors.CYAN}{compression_ratio:.1f}% del original{Colors.RESET}]"
    
    print(msg)


def print_file_error(filename: str, error: str):
    """Muestra mensaje de error en archivo."""
    clear_line()
    print(f"  {Colors.RED}✗{Colors.RESET} {filename}: {Colors.RED}{error}{Colors.RESET}")


def print_summary(total_files: int, successful: int, failed: int, 
                  total_time: float, original_size: int, converted_size: int):
    """Muestra resumen final de la conversión."""
    print()
    print(f"{Colors.CYAN}{Colors.BOLD}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}📊 RESUMEN{Colors.RESET}")
    print(f"{Colors.GRAY}{'─' * 60}{Colors.RESET}")
    
    # Archivos
    print(f"  Archivos procesados: {Colors.BOLD}{successful}/{total_files}{Colors.RESET}", end="")
    if failed > 0:
        print(f" {Colors.RED}({failed} errores){Colors.RESET}")
    else:
        print(f" {Colors.GREEN}(sin errores){Colors.RESET}")
    
    # Tiempo
    print(f"  Tiempo total: {Colors.BOLD}{format_time(total_time)}{Colors.RESET}")
    
    # Tamaños
    def format_size(size_bytes):
        if size_bytes >= 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
    
    original_str = format_size(original_size)
    converted_str = format_size(converted_size)
    saved = original_size - converted_size
    saved_str = format_size(abs(saved))
    
    print(f"  Tamaño original: {original_str}")
    print(f"  Tamaño convertido: {Colors.GREEN}{converted_str}{Colors.RESET}")
    
    if saved > 0:
        percent_saved = (saved / original_size) * 100 if original_size > 0 else 0
        print(f"  {Colors.GREEN}💾 Espacio ahorrado: {saved_str} ({percent_saved:.1f}%){Colors.RESET}")
    
    print(f"{Colors.CYAN}{Colors.BOLD}{'═' * 60}{Colors.RESET}")
    print()


def ask_confirmation() -> bool:
    """Pide confirmación al usuario para continuar."""
    try:
        response = input(f"{Colors.YELLOW}¿Iniciar conversión? (s/n): {Colors.RESET}").strip().lower()
        return response in ('s', 'si', 'sí', 'y', 'yes', '')
    except (KeyboardInterrupt, EOFError):
        return False


def print_cancelled():
    """Muestra mensaje de operación cancelada."""
    print(f"\n{Colors.YELLOW}⚠️  Operación cancelada por el usuario.{Colors.RESET}")


def print_output_location(output_dir: Path):
    """Muestra ubicación de los archivos convertidos."""
    print(f"{Colors.GREEN}📂 Archivos guardados en: {Colors.BOLD}{output_dir}{Colors.RESET}")
    print()


def wait_for_exit():
    """Espera a que el usuario presione Enter para salir."""
    print()
    input(f"{Colors.GRAY}Presiona Enter para salir...{Colors.RESET}")
