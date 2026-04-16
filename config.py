"""
Configuracion de Jarvis.
Carga las API keys desde .env y define parametros del sistema.

Crea un archivo .env en la raiz del proyecto con:

    SPOTIFY_CLIENT_ID=tu_client_id
    SPOTIFY_CLIENT_SECRET=tu_client_secret
    SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
    NOTION_TOKEN=tu_notion_integration_token
    NOTION_CALENDAR_DB=id_de_tu_base_de_datos_calendario
    WEATHER_CITY=Madrid
"""

import os
from dotenv import load_dotenv

load_dotenv()

# === SPOTIFY ===
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")
SPOTIFY_SCOPE = (
    "user-read-playback-state "
    "user-modify-playback-state "
    "user-read-currently-playing "
    "playlist-read-private "
    "playlist-read-collaborative"
)

# === NOTION ===
NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
NOTION_CALENDAR_DB = os.getenv("NOTION_CALENDAR_DB", "")

# === DETECCION DE PALMAS ===
CLAP_THRESHOLD = int(os.getenv("CLAP_THRESHOLD", "3000"))
CLAP_INTERVAL = float(os.getenv("CLAP_INTERVAL", "0.6"))

# === AUDIO ===
SAMPLE_RATE = 44100
CHUNK_SIZE = 1024

# === VOZ ===
VOICE_LANGUAGE = "es"
VOICE_RATE = 180
VOICE_VOLUME = 1.0

# === NOTICIAS ===
DEFAULT_CITY = os.getenv("WEATHER_CITY", "Madrid")
NEWS_COUNT = 5

# === RECORDATORIOS ===
REMINDERS_FILE = "reminders.json"

# === INTERFAZ ===
SHOW_BANNER = True
ASSISTANT_NAME = "Jarvis"
