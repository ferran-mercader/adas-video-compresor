"""
AVI to MP4 Video Compressor

Script principal que convierte archivos .avi a .mp4 (H.264) con progreso en tiempo real.
"""

import sys
import time
from pathlib import Path

from utils import (
    find_avi_files,
    get_files_info,
    ensure_output_directory,
    get_output_path,
    validate_files_exist,
    get_script_directory,
    format_file_size
)
from progress import (
    print_header,
    print_detected_files,
    print_no_files_found,
    print_conversion_start,
    print_file_progress,
    print_progress,
    print_file_complete,
    print_file_error,
    print_summary,
    print_output_location,
    print_cancelled,
    ask_confirmation,
    wait_for_exit,
    Colors
)
from converter import (
    check_ffmpeg_available,
    convert_video,
    ConversionProgress
)


def main():
    """Función principal del programa."""
    # Mostrar encabezado
    print_header()
    
    # Verificar FFmpeg
    ffmpeg_ok, ffmpeg_msg = check_ffmpeg_available()
    if not ffmpeg_ok:
        print(f"{Colors.RED}❌ Error: {ffmpeg_msg}{Colors.RESET}")
        print()
        print("Para usar este programa necesitas FFmpeg instalado.")
        print("Descárgalo desde: https://ffmpeg.org/download.html")
        wait_for_exit()
        sys.exit(1)
    
    print(f"{Colors.GREEN}✓ {ffmpeg_msg}{Colors.RESET}")
    print()
    
    # Buscar archivos AVI
    script_dir = get_script_directory()
    print(f"{Colors.GRAY}Buscando en: {script_dir}{Colors.RESET}")
    print()
    
    avi_files = find_avi_files(script_dir)
    
    if not avi_files:
        print_no_files_found()
        wait_for_exit()
        sys.exit(0)
    
    # Validar archivos
    valid_files, invalid_files = validate_files_exist(avi_files)
    
    if invalid_files:
        print(f"{Colors.YELLOW}⚠️  Algunos archivos no son accesibles:{Colors.RESET}")
        for f in invalid_files:
            print(f"   - {f.name}")
        print()
    
    if not valid_files:
        print(f"{Colors.RED}❌ No hay archivos válidos para convertir.{Colors.RESET}")
        wait_for_exit()
        sys.exit(1)
    
    # Mostrar archivos detectados
    files_info = get_files_info(valid_files)
    print_detected_files(files_info)
    
    # Pedir confirmación
    if not ask_confirmation():
        print_cancelled()
        wait_for_exit()
        sys.exit(0)
    
    # Crear carpeta de salida
    output_dir = ensure_output_directory(script_dir)
    print()
    print_conversion_start(len(valid_files))
    
    # Variables de tracking
    total_start_time = time.time()
    successful = 0
    failed = 0
    total_input_size = 0
    total_output_size = 0
    
    # Procesar cada archivo
    for i, (file, size_str, size_bytes) in enumerate(files_info, 1):
        total_input_size += size_bytes
        output_file = get_output_path(file, output_dir)
        
        print_file_progress(i, len(files_info), file.name)
        
        # Callback de progreso
        def progress_callback(progress: ConversionProgress):
            print_progress(
                percent=progress.percent,
                speed=progress.speed,
                fps=progress.fps,
                eta=progress.eta
            )
        
        # Convertir
        file_start_time = time.time()
        result = convert_video(
            input_file=file,
            output_file=output_file,
            preset="medium",
            crf=23,
            audio_bitrate="128k",
            progress_callback=progress_callback
        )
        
        if result.success:
            successful += 1
            total_output_size += result.output_size
            
            # Calcular ratio de compresión
            compression_ratio = (result.output_size / result.input_size) * 100 if result.input_size > 0 else 100
            
            print_file_complete(
                filename=file.name,
                output_size=format_file_size(result.output_size),
                time_taken=result.duration,
                compression_ratio=compression_ratio
            )
        else:
            failed += 1
            print_file_error(file.name, result.error_message[:50] if result.error_message else "Error desconocido")
    
    # Mostrar resumen
    total_time = time.time() - total_start_time
    print_summary(
        total_files=len(files_info),
        successful=successful,
        failed=failed,
        total_time=total_time,
        original_size=total_input_size,
        converted_size=total_output_size
    )
    
    if successful > 0:
        print_output_location(output_dir)
    
    wait_for_exit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_cancelled()
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Error inesperado: {e}{Colors.RESET}")
        wait_for_exit()
        sys.exit(1)