"""
Modulo de gestion del sistema para Jarvis.
Abre aplicaciones (incluyendo WhatsApp y Notion), muestra info del sistema.
"""

import subprocess
import platform
import webbrowser


class SystemManager:
    """Gestor de sistema de Jarvis. Abre apps, monitoriza recursos."""

    # URLs de webapps conocidas
    WEB_APPS = {
        "whatsapp": "https://web.whatsapp.com",
        "whaticket": "https://web.whatsapp.com",
        "notion": "https://www.notion.so",
        "gmail": "https://mail.google.com",
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "twitter": "https://twitter.com",
        "x": "https://x.com",
        "instagram": "https://www.instagram.com",
        "github": "https://github.com",
        "chatgpt": "https://chat.openai.com",
        "drive": "https://drive.google.com",
        "calendar": "https://calendar.google.com",
        "maps": "https://maps.google.com",
        "trello": "https://trello.com",
        "slack": "https://slack.com",
        "discord": "https://discord.com/app",
        "linkedin": "https://www.linkedin.com",
        "tiktok": "https://www.tiktok.com",
        "twitch": "https://www.twitch.tv",
        "netflix": "https://www.netflix.com",
    }

    APPS_LINUX = {
        "chrome": ["google-chrome"],
        "firefox": ["firefox"],
        "terminal": ["x-terminal-emulator"],
        "archivos": ["nautilus"],
        "explorador": ["nautilus"],
        "calculadora": ["gnome-calculator"],
        "editor": ["gedit"],
        "spotify": ["spotify"],
        "configuracion": ["gnome-control-center"],
        "monitor": ["gnome-system-monitor"],
        "code": ["code"],
        "vscode": ["code"],
    }

    APPS_WINDOWS = {
        "chrome": ["start", "chrome"],
        "firefox": ["start", "firefox"],
        "terminal": ["cmd"],
        "archivos": ["explorer"],
        "explorador": ["explorer"],
        "calculadora": ["calc"],
        "editor": ["notepad"],
        "bloc de notas": ["notepad"],
        "configuracion": ["start", "ms-settings:"],
        "spotify": ["start", "spotify:"],
        "word": ["start", "winword"],
        "excel": ["start", "excel"],
        "powerpoint": ["start", "powerpnt"],
        "code": ["start", "code"],
        "vscode": ["start", "code"],
    }

    APPS_MAC = {
        "chrome": ["open", "-a", "Google Chrome"],
        "firefox": ["open", "-a", "Firefox"],
        "safari": ["open", "-a", "Safari"],
        "terminal": ["open", "-a", "Terminal"],
        "archivos": ["open", "-a", "Finder"],
        "explorador": ["open", "-a", "Finder"],
        "calculadora": ["open", "-a", "Calculator"],
        "spotify": ["open", "-a", "Spotify"],
        "configuracion": ["open", "-a", "System Preferences"],
        "notas": ["open", "-a", "Notes"],
        "code": ["open", "-a", "Visual Studio Code"],
        "vscode": ["open", "-a", "Visual Studio Code"],
    }

    def __init__(self):
        self.system = platform.system().lower()
        if "linux" in self.system:
            self.apps = self.APPS_LINUX
        elif "windows" in self.system:
            self.apps = self.APPS_WINDOWS
        elif "darwin" in self.system:
            self.apps = self.APPS_MAC
        else:
            self.apps = self.APPS_LINUX

    def open_app(self, app_name):
        """Abrir una aplicacion por nombre. Detecta webapps automaticamente."""
        app_name = app_name.lower().strip()

        # Primero comprobar si es una webapp conocida
        for key, url in self.WEB_APPS.items():
            if key in app_name or app_name in key:
                try:
                    webbrowser.open(url)
                    return f"Abriendo {key} en el navegador..."
                except Exception as e:
                    return f"Error al abrir {key}: {e}"

        # Luego buscar en apps nativas
        cmd = None
        if app_name in self.apps:
            cmd = self.apps[app_name]
        else:
            for key in self.apps:
                if key in app_name or app_name in key:
                    cmd = self.apps[key]
                    break

        if not cmd:
            if self.system == "linux":
                cmd = [app_name]
            elif self.system == "darwin":
                cmd = ["open", "-a", app_name]
            else:
                cmd = ["start", app_name]

        try:
            if self.system == "windows":
                subprocess.Popen(cmd, shell=True)
            else:
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Abriendo {app_name}..."
        except FileNotFoundError:
            return f"No pude encontrar la aplicacion '{app_name}'."
        except Exception as e:
            return f"Error al abrir {app_name}: {e}"

    def open_whatsapp(self):
        """Abrir WhatsApp Web directamente."""
        try:
            webbrowser.open("https://web.whatsapp.com")
            return "Abriendo WhatsApp Web..."
        except Exception as e:
            return f"Error al abrir WhatsApp: {e}"

    def open_notion(self):
        """Abrir Notion directamente."""
        try:
            webbrowser.open("https://www.notion.so")
            return "Abriendo Notion..."
        except Exception as e:
            return f"Error al abrir Notion: {e}"

    def get_system_info(self):
        """Obtener informacion completa del sistema."""
        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            battery = psutil.sensors_battery()

            info = []
            info.append(f"CPU al {cpu_percent}%")
            info.append(f"Memoria: {memory.percent}% usada de {memory.total // (1024**3)} GB")
            info.append(f"Disco: {disk.percent}% usado de {disk.total // (1024**3)} GB")

            if battery:
                charging = "cargando" if battery.power_plugged else "en bateria"
                info.append(f"Bateria: {battery.percent}% ({charging})")

            net = psutil.net_io_counters()
            info.append(
                f"Red: {net.bytes_sent // (1024**2)} MB enviados, "
                f"{net.bytes_recv // (1024**2)} MB recibidos"
            )

            return "Estado del sistema: " + ". ".join(info)

        except ImportError:
            return self._basic_system_info()
        except Exception as e:
            return f"Error al obtener info del sistema: {e}"

    def _basic_system_info(self):
        """Info basica del sistema sin psutil."""
        info = [
            f"Sistema: {platform.system()} {platform.release()}",
            f"Maquina: {platform.machine()}",
            f"Procesador: {platform.processor() or 'desconocido'}",
            f"Python: {platform.python_version()}",
        ]
        return "Sistema: " + ". ".join(info)

    def get_quick_status(self):
        """Estado rapido del sistema (para informe con 3 palmas)."""
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory().percent
            battery = psutil.sensors_battery()

            status = f"CPU al {cpu}%, memoria al {mem}%"
            if battery:
                status += f", bateria al {battery.percent}%"
            return status
        except ImportError:
            return "Sistema operativo: " + platform.system()

    def list_available_apps(self):
        """Listar aplicaciones disponibles."""
        native = sorted(self.apps.keys())
        web = sorted(self.WEB_APPS.keys())
        result = "Apps nativas: " + ", ".join(native)
        result += "\nWebapps: " + ", ".join(web)
        return result
