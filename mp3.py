#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import platform
import subprocess
import re
import shutil
import time
import datetime

# Constantes
VERSION = "1.0"
AUTHOR = "@RealStrategy"
CANAL = "https://www.youtube.com/@zonatodoreal"

def clear_screen():
    """Limpia la pantalla de la consola"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Muestra el encabezado"""
    clear_screen()
    print("\n" + "="*50)
    print(f" YouTube Musica Downloader Pro".center(50))
    print(f" Versión {VERSION} (TD)".center(50))
    print("="*50 + "\n")

def print_menu():
    """Muestra el menú principal"""
    print(" MENÚ PRINCIPAL ".center(50, "-"))
    print("1. Descargar audio (MP3)")
    print("2. Verificar dependencias")
    print("3. Configuración")
    print("4. Salir")
    print("-"*50 + "\n")

def loading_animation(message):
    """Muestra una animación de carga básica"""
    for i in range(3):
        for char in "|/-\\":
            sys.stdout.write(f"\r{message} {char}")
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write("\r" + " "*len(message) + "\r")

def obtener_carpeta_descargas():
    """Obtiene la ruta de descargas"""
    if os.path.exists('/data/data/com.termux/files/home'):  # Android (Termux)
        posibles_rutas = [
            '/sdcard/Download',
            '/storage/emulated/0/Download',
            '/sdcard/Music'
        ]
        for ruta in posibles_rutas:
            if os.path.exists(ruta):
                return ruta
        return '/sdcard/Download'
    
    # Para otros sistemas operativos
    sistema = platform.system()
    home = os.path.expanduser("~")
    
    if sistema == "Windows":
        downloads = os.path.join(os.environ["USERPROFILE"], "Music")
    elif sistema == "Darwin":
        downloads = os.path.join(home, "Music")
    else:  # Linux y otros
        downloads = os.path.join(home, "Música")
        if not os.path.exists(downloads):
            downloads = os.path.join(home, "Music")
    
    os.makedirs(downloads, exist_ok=True)
    return downloads

def verificar_instalacion_yt_dlp():
    """Verifica e instala yt-dlp"""
    try:
        import yt_dlp
        print("\n✓ yt-dlp ya está instalado")
        return yt_dlp
    except ImportError:
        print("\nInstalando yt-dlp...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            import yt_dlp
            print("✓ yt-dlp instalado correctamente")
            return yt_dlp
        except Exception as e:
            print(f"\nError al instalar yt-dlp: {str(e)}")
            sys.exit(1)

def verificar_ffmpeg():
    """Verifica si FFmpeg está instalado"""
    try:
        if shutil.which('ffmpeg'):
            subprocess.run(['ffmpeg', '-version'], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE,
                         check=True)
            print("\n✓ FFmpeg está instalado (Necesario para MP3)")
            return True
        print("\n⚠ FFmpeg no encontrado (Se requiere para MP3)")
        return False
    except:
        print("\n✗ Error al verificar FFmpeg")
        return False

def mostrar_progreso(d):
    """Muestra el progreso de descarga"""
    if d['status'] == 'downloading':
        porcentaje = d.get('_percent_str', '0%').strip()
        velocidad = d.get('_speed_str', '?').strip()
        eta = d.get('_eta_str', '?').strip()
        sys.stdout.write(f"\rDescargando: {porcentaje} | Velocidad: {velocidad} | Tiempo restante: {eta}")
        sys.stdout.flush()

def mostrar_info_audio(info):
    """Muestra la información del audio"""
    titulo = info.get('title', 'Desconocido')
    duracion = info.get('duration', 0)
    vistas = info.get('view_count', 0)
    artista = info.get('artist', 'Desconocido')
    album = info.get('album', 'Desconocido')
    
    # Formatear duración
    mins, secs = divmod(duracion, 60)
    horas, mins = divmod(mins, 60)
    if horas > 0:
        duracion_str = f"{horas}:{mins:02d}:{secs:02d}"
    else:
        duracion_str = f"{mins}:{secs:02d}"
    
    # Formatear vistas
    try:
        vistas_str = f"{int(vistas):,}".replace(",", ".")
    except:
        vistas_str = str(vistas)
    
    print("\n--- INFORMACIÓN DEL AUDIO ---")
    print(f"\nTítulo: {titulo}")
    print(f"Artista: {artista}")
    print(f"Álbum: {album}")
    print(f"Duración: {duracion_str}")
    print(f"Vistas: {vistas_str}")
    print("\n" + "-"*30)

def descargar_mp3(url):
    """Función principal de descarga de MP3"""
    try:
        yt_dlp = verificar_instalacion_yt_dlp()
        carpeta_descargas = obtener_carpeta_descargas()
        
        if not verificar_ffmpeg():
            print("\n✗ FFmpeg es requerido para convertir a MP3")
            input("\nPresiona Enter para continuar...")
            return
        
        config = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(carpeta_descargas, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'progress_hooks': [mostrar_progreso],
            'retries': 10,
            'nocheckcertificate': True,
            'addmetadata': True,
            'writethumbnail': True,
            'postprocessor_args': [
                '-metadata', 'title=%(title)s',
                '-metadata', 'artist=%(uploader)s',
                '-metadata', 'album=%(playlist_title)s'
            ],
            'keepvideo': False
        }
        
        with yt_dlp.YoutubeDL(config) as ydl:
            print("\nObteniendo información del audio...")
            info = ydl.extract_info(url, download=False)
            
            mostrar_info_audio(info)
            
            confirmar = input("\n¿Descargar este audio? (s/n): ").lower()
            if confirmar != 's':
                print("\nDescarga cancelada")
                return
            
            print("\nIniciando descarga y conversión a MP3...")
            ydl.download([url])
            
            print(f"\n✓ Conversión a MP3 completada: {info['title']}.mp3")
            print(f"Ubicación: {carpeta_descargas}")
            
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")

if __name__ == "__main__":
    while True:
        print_header()
        print_menu()
        
        try:
            opcion = input("Selecciona una opción (1-4): ").strip()
            
            if opcion == "1":
                print_header()
                url = input("\nIngresa la URL de YouTube: ").strip()
                
                if not url.startswith(('http://', 'https://')):
                    print("\n⚠ Ingresa una URL válida (debe comenzar con http:// o https://)")
                    input("\nPresiona Enter para continuar...")
                    continue
                    
                if "youtube.com" not in url and "youtu.be" not in url:
                    print("\n⚠ Esta no parece ser una URL de YouTube")
                    input("\nPresiona Enter para continuar...")
                    continue
                    
                descargar_mp3(url)
                input("\nPresiona Enter para continuar...")
                
            elif opcion == "2":
                print_header()
                print("\nVerificando dependencias...")
                verificar_instalacion_yt_dlp()
                verificar_ffmpeg()
                input("\nPresiona Enter para continuar...")
                
            elif opcion == "3":
                print_header()
                print("\nConfiguración actual:")
                print(f"\n• Carpeta de descargas: {obtener_carpeta_descargas()}")
                print(f"• FFmpeg instalado: {'Sí' if verificar_ffmpeg() else 'No'}")
                print(f"• Modo Android: {'Sí' if os.path.exists('/data/data/com.termux/files/home') else 'No'}")
                input("\nPresiona Enter para continuar...")
                
            elif opcion == "4":
                print_header()
                print("\n¡Hasta luego!")
                print("\nGracias por usar YouTube Musica Downloader Pro")
                break
                
            else:
                print("\nOpción no válida. Por favor selecciona 1-4.")
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nOperación cancelada por el usuario")
            break
