"""
Utilidades para descubrimiento de archivos y gestión de carpetas.
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional


def get_script_directory() -> Path:
    """Obtiene el directorio donde se ejecuta el script/ejecutable."""
    # Cuando se ejecuta como .exe, usa el directorio del ejecutable
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent


def find_avi_files(directory: Optional[Path] = None) -> List[Path]:
    """
    Busca todos los archivos .avi en el directorio especificado.
    
    Args:
        directory: Directorio donde buscar. Si es None, usa el directorio del script.
    
    Returns:
        Lista de paths a archivos .avi encontrados.
    """
    if directory is None:
        directory = get_script_directory()
    
    avi_files = []
    for file in directory.iterdir():
        if file.is_file() and file.suffix.lower() == '.avi':
            avi_files.append(file)
    
    # Ordenar por nombre
    avi_files.sort(key=lambda x: x.name.lower())
    return avi_files


def get_file_size_mb(file_path: Path) -> float:
    """Obtiene el tamaño de un archivo en MB."""
    return file_path.stat().st_size / (1024 * 1024)


def get_file_size_gb(file_path: Path) -> float:
    """Obtiene el tamaño de un archivo en GB."""
    return file_path.stat().st_size / (1024 * 1024 * 1024)


def format_file_size(size_bytes: int) -> str:
    """Formatea el tamaño de archivo de forma legible."""
    if size_bytes >= 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
    elif size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes} B"


def get_files_info(files: List[Path]) -> List[Tuple[Path, str, int]]:
    """
    Obtiene información de una lista de archivos.
    
    Returns:
        Lista de tuplas (path, tamaño_formateado, tamaño_bytes)
    """
    info = []
    for file in files:
        size_bytes = file.stat().st_size
        size_formatted = format_file_size(size_bytes)
        info.append((file, size_formatted, size_bytes))
    return info


def ensure_output_directory(base_dir: Optional[Path] = None) -> Path:
    """
    Crea la carpeta 'output' si no existe.
    
    Args:
        base_dir: Directorio base. Si es None, usa el directorio del script.
    
    Returns:
        Path a la carpeta output.
    """
    if base_dir is None:
        base_dir = get_script_directory()
    
    output_dir = base_dir / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


def get_output_path(input_file: Path, output_dir: Path) -> Path:
    """
    Genera el path de salida para un archivo convertido.
    
    Args:
        input_file: Archivo de entrada (.avi)
        output_dir: Directorio de salida
    
    Returns:
        Path del archivo de salida (.mp4)
    """
    return output_dir / f"{input_file.stem}.mp4"


def validate_files_exist(files: List[Path]) -> Tuple[List[Path], List[Path]]:
    """
    Valida que los archivos existan y sean accesibles.
    
    Returns:
        Tupla de (archivos_validos, archivos_invalidos)
    """
    valid = []
    invalid = []
    
    for file in files:
        if file.exists() and file.is_file():
            try:
                # Intentar abrir para verificar acceso
                with open(file, 'rb') as f:
                    f.read(1)
                valid.append(file)
            except (PermissionError, IOError):
                invalid.append(file)
        else:
            invalid.append(file)
    
    return valid, invalid


def get_total_size(files: List[Path]) -> int:
    """Calcula el tamaño total de una lista de archivos en bytes."""
    return sum(f.stat().st_size for f in files)
