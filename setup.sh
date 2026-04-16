#!/bin/bash
# ============================================
#  Instalador de Jarvis
#  Spotify + Notion + WhatsApp + Voz + Palmas
# ============================================

set -e

echo ""
echo "  ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗"
echo "  ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝"
echo "  ██║███████║██████╔╝██║   ██║██║███████╗"
echo "  ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║"
echo "  ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║"
echo "   ╚════╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝"
echo ""
echo "  Instalando Jarvis con Spotify + Notion..."
echo ""

# Detectar sistema operativo
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "[*] Sistema Linux detectado"
    echo "[*] Instalando dependencias del sistema..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq portaudio19-dev python3-pyaudio espeak ffmpeg 2>/dev/null
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "[*] Sistema macOS detectado"
    echo "[*] Instalando dependencias con Homebrew..."
    brew install portaudio espeak ffmpeg 2>/dev/null
fi

# Crear entorno virtual
echo "[*] Creando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias Python
echo "[*] Instalando paquetes Python..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Crear .env si no existe
if [ ! -f .env ]; then
    echo "[*] Creando archivo .env desde .env.example..."
    cp .env.example .env
    echo ""
    echo "  *** IMPORTANTE ***"
    echo "  Edita el archivo .env con tus credenciales:"
    echo "    - Spotify: https://developer.spotify.com/dashboard"
    echo "    - Notion:  https://www.notion.so/my-integrations"
    echo ""
fi

echo ""
echo "============================================"
echo "  Jarvis instalado correctamente!"
echo ""
echo "  CONFIGURACION:"
echo "    1. Edita .env con tus API keys"
echo "    2. Spotify: crea app en developer.spotify.com"
echo "    3. Notion: crea integracion y comparte tu BD"
echo ""
echo "  EJECUTAR:"
echo "    source venv/bin/activate"
echo "    python jarvis.py"
echo ""
echo "  CONTROLES:"
echo "    1 palma  = Escuchar comando"
echo "    2 palmas = Play/Pause Spotify"
echo "    3 palmas = Informe del dia"
echo "============================================"
echo ""
