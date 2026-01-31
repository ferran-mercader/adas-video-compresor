"""
Script para crear el ejecutable Windows con PyInstaller.

Este script:
1. Verifica/descarga FFmpeg estático
2. Crea el ejecutable con PyInstaller
3. Incluye FFmpeg en el paquete final
"""

import os
import sys
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path


# Configuración
APP_NAME = "avi2mp4"
FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
SCRIPT_DIR = Path(__file__).parent


def print_step(msg: str):
    """Imprime un paso del proceso."""
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}")


def check_pyinstaller():
    """Verifica que PyInstaller esté instalado."""
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} encontrado")
        return True
    except ImportError:
        print("✗ PyInstaller no encontrado")
        print("  Instálalo con: pip install pyinstaller")
        return False


def download_ffmpeg():
    """Descarga FFmpeg estático si no existe."""
    ffmpeg_dir = SCRIPT_DIR / "ffmpeg"
    ffmpeg_exe = ffmpeg_dir / "ffmpeg.exe"
    ffprobe_exe = ffmpeg_dir / "ffprobe.exe"
    
    if ffmpeg_exe.exists() and ffprobe_exe.exists():
        print("✓ FFmpeg ya existe en carpeta local")
        return True
    
    print("Descargando FFmpeg estático...")
    print(f"  URL: {FFMPEG_URL}")
    
    zip_path = SCRIPT_DIR / "ffmpeg-temp.zip"
    
    try:
        # Descargar
        def progress_hook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, downloaded * 100 / total_size)
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                print(f"\r  Descargando: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end="")
        
        urllib.request.urlretrieve(FFMPEG_URL, zip_path, progress_hook)
        print("\n✓ Descarga completada")
        
        # Extraer
        print("Extrayendo FFmpeg...")
        ffmpeg_dir.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Buscar los ejecutables dentro del zip
            for file_info in zip_ref.filelist:
                if file_info.filename.endswith('ffmpeg.exe'):
                    # Extraer solo el archivo
                    with zip_ref.open(file_info) as source:
                        with open(ffmpeg_exe, 'wb') as target:
                            target.write(source.read())
                    print(f"  ✓ Extraído: ffmpeg.exe")
                elif file_info.filename.endswith('ffprobe.exe'):
                    with zip_ref.open(file_info) as source:
                        with open(ffprobe_exe, 'wb') as target:
                            target.write(source.read())
                    print(f"  ✓ Extraído: ffprobe.exe")
        
        # Limpiar
        zip_path.unlink()
        
        if ffmpeg_exe.exists() and ffprobe_exe.exists():
            print("✓ FFmpeg listo")
            return True
        else:
            print("✗ Error: No se encontraron los ejecutables en el zip")
            return False
        
    except Exception as e:
        print(f"\n✗ Error descargando FFmpeg: {e}")
        if zip_path.exists():
            zip_path.unlink()
        return False


def create_executable():
    """Crea el ejecutable con PyInstaller."""
    print("Creando ejecutable...")
    
    ffmpeg_dir = SCRIPT_DIR / "ffmpeg"
    dist_dir = SCRIPT_DIR / "dist"
    build_dir = SCRIPT_DIR / "build"
    
    # Limpiar builds anteriores
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Comando PyInstaller
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--onedir",  # Crear carpeta con dependencias (mejor para incluir FFmpeg)
        "--console",  # Mostrar consola
        "--name", APP_NAME,
        "--clean",
        # Añadir archivos de datos (FFmpeg)
        "--add-data", f"{ffmpeg_dir / 'ffmpeg.exe'};.",
        "--add-data", f"{ffmpeg_dir / 'ffprobe.exe'};.",
        # Archivo principal
        str(SCRIPT_DIR / "main.py")
    ]
    
    print(f"  Ejecutando: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, cwd=SCRIPT_DIR)
    
    if result.returncode == 0:
        exe_path = dist_dir / APP_NAME / f"{APP_NAME}.exe"
        if exe_path.exists():
            print(f"\n✓ Ejecutable creado exitosamente!")
            print(f"  Ubicación: {exe_path}")
            
            # Mostrar tamaño
            total_size = sum(f.stat().st_size for f in (dist_dir / APP_NAME).rglob('*') if f.is_file())
            print(f"  Tamaño total: {total_size / (1024*1024):.1f} MB")
            
            return True
    
    print("✗ Error creando ejecutable")
    return False


def create_single_exe():
    """Crea un ejecutable único (alternativa más portable)."""
    print("Creando ejecutable único (--onefile)...")
    print("  Nota: Esta opción es más lenta de iniciar pero más portable")
    
    ffmpeg_dir = SCRIPT_DIR / "ffmpeg"
    
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--onefile",  # Un solo archivo .exe
        "--console",
        "--name", f"{APP_NAME}_portable",
        "--clean",
        "--add-data", f"{ffmpeg_dir / 'ffmpeg.exe'};.",
        "--add-data", f"{ffmpeg_dir / 'ffprobe.exe'};.",
        str(SCRIPT_DIR / "main.py")
    ]
    
    result = subprocess.run(cmd, cwd=SCRIPT_DIR)
    
    if result.returncode == 0:
        exe_path = SCRIPT_DIR / "dist" / f"{APP_NAME}_portable.exe"
        if exe_path.exists():
            print(f"\n✓ Ejecutable portable creado!")
            print(f"  Ubicación: {exe_path}")
            print(f"  Tamaño: {exe_path.stat().st_size / (1024*1024):.1f} MB")
            return True
    
    return False


def main():
    """Función principal del build."""
    print("\n" + "="*60)
    print("  AVI to MP4 Compressor - Build Script")
    print("="*60)
    
    # Paso 1: Verificar PyInstaller
    print_step("Paso 1: Verificando PyInstaller")
    if not check_pyinstaller():
        print("\nInstalando PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        if not check_pyinstaller():
            print("Error: No se pudo instalar PyInstaller")
            sys.exit(1)
    
    # Paso 2: Descargar FFmpeg
    print_step("Paso 2: Preparando FFmpeg")
    if not download_ffmpeg():
        print("\nPuedes descargar FFmpeg manualmente desde:")
        print("  https://ffmpeg.org/download.html")
        print("Coloca ffmpeg.exe y ffprobe.exe en la carpeta 'ffmpeg/'")
        sys.exit(1)
    
    # Paso 3: Crear ejecutable
    print_step("Paso 3: Creando ejecutable")
    if not create_executable():
        sys.exit(1)
    
    # Resumen
    print("\n" + "="*60)
    print("  ¡BUILD COMPLETADO!")
    print("="*60)
    print(f"""
Para distribuir el programa:
1. Copia la carpeta 'dist/{APP_NAME}/' completa
2. El usuario solo necesita ejecutar '{APP_NAME}.exe'
3. No requiere instalación de Python ni FFmpeg

Para una versión más portable (un solo archivo):
  Ejecuta: python build.py --onefile
""")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--onefile":
        # Solo crear versión portable
        if check_pyinstaller() and download_ffmpeg():
            create_single_exe()
    else:
        main()
