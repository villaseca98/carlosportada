"""
Configuracion de Jarvis.
Modifica estos valores para personalizar tu asistente.
"""

# === DETECCION DE PALMAS ===
# Sensibilidad del microfono para detectar palmas.
# Valores mas bajos = mas sensible (puede dar falsos positivos).
# Valores mas altos = menos sensible (puede no detectar palmas suaves).
# Rango recomendado: 1500-5000
CLAP_THRESHOLD = 3000

# Tiempo maximo entre palmas para que cuenten como patron (en segundos).
# Ejemplo: 2 palmas deben ocurrir dentro de este intervalo.
CLAP_INTERVAL = 0.6

# === AUDIO ===
SAMPLE_RATE = 44100
CHUNK_SIZE = 1024

# === VOZ ===
# Idioma del reconocimiento de voz y TTS
VOICE_LANGUAGE = "es"
# Velocidad de habla (palabras por minuto aprox)
VOICE_RATE = 180
# Volumen de voz (0.0 a 1.0)
VOICE_VOLUME = 1.0

# === MUSICA ===
# Carpeta donde Jarvis busca canciones
MUSIC_DIR = "music"
# Volumen inicial de la musica (0.0 a 1.0)
MUSIC_VOLUME = 0.7

# === NOTICIAS ===
# Ciudad por defecto para el clima
DEFAULT_CITY = "Madrid"
# Numero de noticias a mostrar
NEWS_COUNT = 5

# === RECORDATORIOS ===
REMINDERS_FILE = "reminders.json"

# === INTERFAZ ===
# Mostrar ASCII art al iniciar
SHOW_BANNER = True

# Nombre del asistente
ASSISTANT_NAME = "Jarvis"
