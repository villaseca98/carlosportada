#!/usr/bin/env python3
"""
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝

Jarvis - Asistente personal con Spotify, Notion y deteccion de palmas.

PALMAS:
  1 palma  -> Activar modo escucha (di un comando de voz)
  2 palmas -> Play/Pause en Spotify
  3 palmas -> Informe completo (sistema + clima + calendario + noticias)

COMANDOS DE VOZ / TECLADO:
  "pon Stronger de Kanye West"   -> Busca y reproduce en Spotify
  "abre whatsapp"                -> Abre WhatsApp Web
  "abre notion"                  -> Abre Notion
  "calendario" / "que tengo hoy" -> Lee tu agenda de Notion
  "noticias"                     -> Titulares del dia
  "clima en Madrid"              -> Clima actual
  "recuerdame que..."            -> Crear recordatorio
  "informe"                      -> Briefing completo
  "ayuda"                        -> Lista de comandos

Autor: Carlos Portada
"""

import sys
import signal
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

import config
from modules.clap_detector import ClapDetector
from modules.voice import Voice
from modules.spotify_player import SpotifyPlayer
from modules.notion_calendar import NotionCalendar
from modules.system_manager import SystemManager
from modules.news_updater import NewsUpdater
from modules.assistant import Assistant


BANNER = r"""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║         ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗              ║
║         ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝              ║
║         ██║███████║██████╔╝██║   ██║██║███████╗              ║
║    ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║              ║
║    ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║              ║
║     ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝              ║
║                                                               ║
║   [Spotify] + [Notion] + [WhatsApp] + [Voz] + [Palmas]       ║
║                                                               ║
║   1 PALMA  = Escuchar comando de voz                         ║
║   2 PALMAS = Play/Pause Spotify                              ║
║   3 PALMAS = Informe completo del dia                        ║
║                                                               ║
║   Escribe comandos o 'salir' para cerrar | Ctrl+C            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""


def main():
    if config.SHOW_BANNER:
        print(BANNER)

    print("[Jarvis] Inicializando sistemas...\n")

    # --- Voz ---
    voice = Voice(
        language=config.VOICE_LANGUAGE,
        rate=config.VOICE_RATE,
        volume=config.VOICE_VOLUME,
    )

    # --- Spotify ---
    print("[Jarvis] Conectando a Spotify...")
    spotify = SpotifyPlayer(
        client_id=config.SPOTIFY_CLIENT_ID,
        client_secret=config.SPOTIFY_CLIENT_SECRET,
        redirect_uri=config.SPOTIFY_REDIRECT_URI,
        scope=config.SPOTIFY_SCOPE,
    )

    # --- Notion ---
    print("[Jarvis] Conectando a Notion...")
    notion = NotionCalendar(
        token=config.NOTION_TOKEN,
        calendar_db_id=config.NOTION_CALENDAR_DB,
    )

    # --- Sistema y Noticias ---
    system = SystemManager()
    news = NewsUpdater(reminders_file=config.REMINDERS_FILE)

    # --- Asistente ---
    assistant = Assistant(voice, spotify, notion, system, news)

    # --- Detector de palmas ---
    clap = ClapDetector(
        threshold=config.CLAP_THRESHOLD,
        clap_interval=config.CLAP_INTERVAL,
        sample_rate=config.SAMPLE_RATE,
        chunk_size=config.CHUNK_SIZE,
    )
    clap.on_clap(1, assistant.activate_listening)
    clap.on_clap(2, assistant.toggle_music)
    clap.on_clap(3, assistant.full_briefing)

    # --- Shutdown ---
    def shutdown(sig=None, frame=None):
        print("\n[Jarvis] Apagando sistemas...")
        voice.say_sync("Hasta la proxima, senor.")
        clap.stop()
        voice.shutdown()
        print("[Jarvis] Sistemas apagados. Hasta pronto!")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # --- Arranque ---
    print()
    status_lines = []
    status_lines.append(f"  Spotify: {'Conectado' if spotify.is_connected() else 'No conectado'}")
    status_lines.append(f"  Notion:  {'Conectado' if notion.is_connected() else 'No conectado'}")
    status_lines.append(f"  Voz:     Activo")
    status_lines.append(f"  Palmas:  Activo")
    print("\n".join(status_lines))
    print()

    voice.say(news.get_greeting())
    voice.say("Todos los sistemas operativos. Spotify, Notion y WhatsApp listos.")

    # Si Spotify esta conectado, mostrar que esta sonando
    if spotify.is_connected():
        current = spotify.get_current_track()
        if "Reproduciendo" in current:
            voice.say(f"En Spotify: {current}")

    # Si Notion esta conectado, leer agenda del dia
    if notion.is_connected():
        calendar = notion.get_today_events()
        if "No tienes eventos" not in calendar:
            voice.say(calendar)

    # Iniciar deteccion de palmas
    clap.start()

    print("[Jarvis] Sistema activo. Escuchando palmas y comandos por teclado.")
    print("[Jarvis] Escribe 'salir' para cerrar.\n")

    # --- Bucle principal ---
    while True:
        try:
            user_input = input(f"[{config.ASSISTANT_NAME}] > ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["salir", "exit", "quit", "q"]:
                shutdown()

            elif user_input.lower() == "status":
                print(f"  Spotify: {spotify.get_current_track()}")
                print(f"  Notion:  {'Conectado' if notion.is_connected() else 'No conectado'}")
                print(f"  Sistema: {system.get_quick_status()}")

            elif user_input.lower() == "help":
                print("""
  === COMANDOS SPOTIFY ===
    pon Stronger de Kanye West     Buscar y reproducir cancion
    pon playlist rock en espanol   Reproducir playlist
    pausa / continua / siguiente   Control de reproduccion
    volumen 80                     Ajustar volumen (0-100)
    que suena                      Cancion actual
    mis playlists                  Listar tus playlists

  === COMANDOS NOTION ===
    calendario / que tengo hoy     Eventos de hoy
    manana                         Eventos de manana
    esta semana                    Eventos de la semana
    crear evento reunion lunes     Crear nuevo evento

  === COMANDOS APPS ===
    abre whatsapp                  Abrir WhatsApp Web
    abre notion                    Abrir Notion
    abre youtube / chrome / etc    Abrir cualquier app

  === OTROS ===
    noticias / clima / hora        Informacion
    recuerdame que...              Recordatorios
    informe                        Briefing completo
    status                         Estado de conexiones
    salir                          Cerrar Jarvis
                """)

            else:
                assistant.process_command(user_input)

        except EOFError:
            shutdown()
        except KeyboardInterrupt:
            shutdown()


if __name__ == "__main__":
    main()
