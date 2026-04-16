#!/usr/bin/env python3
"""
 ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
 ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
 ██║███████║██████╔╝██║   ██║██║███████╗
██  ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████║██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝

Jarvis - Tu asistente personal por voz con deteccion de palmas.

CONTROLES:
  1 PALMA  -> Activar modo escucha (di un comando)
  2 PALMAS -> Play/Pause musica
  3 PALMAS -> Informe completo (sistema + clima + noticias)

COMANDOS DE VOZ:
  "pon musica"           -> Reproducir musica
  "para la musica"       -> Detener musica
  "siguiente cancion"    -> Siguiente
  "abre chrome"          -> Abrir aplicacion
  "noticias"             -> Titulares de hoy
  "clima en Madrid"      -> Clima de una ciudad
  "que hora es"          -> Hora actual
  "recuerdame que..."    -> Crear recordatorio
  "informe"              -> Briefing completo
  "ayuda"                -> Lista de comandos

Autor: Carlos Portada
"""

import sys
import signal
import time
import os

# Asegurar que el directorio del script sea el working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import config
from modules.clap_detector import ClapDetector
from modules.voice import Voice
from modules.music_player import MusicPlayer
from modules.system_manager import SystemManager
from modules.news_updater import NewsUpdater
from modules.assistant import Assistant


BANNER = r"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗              ║
║        ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝              ║
║        ██║███████║██████╔╝██║   ██║██║███████╗              ║
║   ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║              ║
║   ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║              ║
║    ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝              ║
║                                                              ║
║   Tu asistente personal con deteccion de palmas              ║
║                                                              ║
║   1 PALMA  = Escuchar comando                               ║
║   2 PALMAS = Play/Pause musica                               ║
║   3 PALMAS = Informe completo                                ║
║                                                              ║
║   Escribe 'salir' o pulsa Ctrl+C para cerrar                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""


def main():
    """Punto de entrada principal de Jarvis."""

    if config.SHOW_BANNER:
        print(BANNER)

    print("[Jarvis] Inicializando modulos...\n")

    # Inicializar modulos
    voice = Voice(
        language=config.VOICE_LANGUAGE,
        rate=config.VOICE_RATE,
        volume=config.VOICE_VOLUME,
    )

    music = MusicPlayer(music_dir=config.MUSIC_DIR)

    system = SystemManager()

    news = NewsUpdater(reminders_file=config.REMINDERS_FILE)

    assistant = Assistant(voice, music, system, news)

    # Configurar detector de palmas
    clap = ClapDetector(
        threshold=config.CLAP_THRESHOLD,
        clap_interval=config.CLAP_INTERVAL,
        sample_rate=config.SAMPLE_RATE,
        chunk_size=config.CHUNK_SIZE,
    )

    # Registrar callbacks para las palmas
    clap.on_clap(1, assistant.activate_listening)
    clap.on_clap(2, assistant.toggle_music)
    clap.on_clap(3, assistant.full_briefing)

    # Manejar Ctrl+C
    def shutdown(sig=None, frame=None):
        print("\n[Jarvis] Apagando sistemas...")
        voice.say_sync("Hasta la proxima, senor.")
        clap.stop()
        voice.shutdown()
        print("[Jarvis] Sistemas apagados. Hasta pronto!")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Saludo inicial
    voice.say(news.get_greeting())
    voice.say("Todos los sistemas operativos. Esperando ordenes.")

    # Iniciar deteccion de palmas
    clap.start()

    print("\n[Jarvis] Sistema activo. Escuchando palmas...")
    print("[Jarvis] Tambien puedes escribir comandos directamente.")
    print("[Jarvis] Escribe 'salir' para cerrar.\n")

    # Bucle principal: acepta tambien comandos por teclado
    while True:
        try:
            user_input = input(f"[{config.ASSISTANT_NAME}] > ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["salir", "exit", "quit", "q"]:
                shutdown()

            elif user_input.lower() == "status":
                print(f"  Musica: {music.get_status()}")
                print(f"  Sistema: {system.get_quick_status()}")

            elif user_input.lower() == "help":
                print("""
  Comandos por teclado:
    Cualquier comando de voz (pon musica, abre chrome, noticias...)
    status  -> Estado del sistema y musica
    help    -> Esta ayuda
    salir   -> Cerrar Jarvis
                """)

            else:
                # Procesar como comando de voz
                assistant.process_command(user_input)

        except EOFError:
            shutdown()
        except KeyboardInterrupt:
            shutdown()


if __name__ == "__main__":
    main()
