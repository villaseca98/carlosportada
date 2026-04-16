#!/bin/bash
# ============================================
#  Instalador de Jarvis - Tu asistente personal
# ============================================

echo ""
echo "  ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗"
echo "  ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝"
echo "  ██║███████║██████╔╝██║   ██║██║███████╗"
echo "  ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║"
echo "  ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║"
echo "   ╚════╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝"
echo ""
echo "  Instalando dependencias..."
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

echo ""
echo "============================================"
echo "  Jarvis instalado correctamente!"
echo ""
echo "  Para ejecutar:"
echo "    source venv/bin/activate"
echo "    python jarvis.py"
echo ""
echo "  Pon tus canciones MP3 en la carpeta 'music/'"
echo "============================================"
echo ""
