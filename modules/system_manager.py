"""
Modulo de gestion del sistema para Jarvis.
Abre aplicaciones, muestra info del sistema, ejecuta comandos.
"""

import subprocess
import platform
import os
import shutil


class SystemManager:
    """Gestor de sistema de Jarvis. Abre apps, monitoriza recursos."""

    APPS_LINUX = {
        "navegador": ["xdg-open", "https://www.google.com"],
        "browser": ["xdg-open", "https://www.google.com"],
        "chrome": ["google-chrome"],
        "firefox": ["firefox"],
        "terminal": ["x-terminal-emulator"],
        "archivos": ["nautilus"],
        "explorador": ["nautilus"],
        "calculadora": ["gnome-calculator"],
        "editor": ["gedit"],
        "musica": ["rhythmbox"],
        "spotify": ["spotify"],
        "configuracion": ["gnome-control-center"],
        "monitor": ["gnome-system-monitor"],
    }

    APPS_WINDOWS = {
        "navegador": ["start", "https://www.google.com"],
        "browser": ["start", "https://www.google.com"],
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
    }

    APPS_MAC = {
        "navegador": ["open", "https://www.google.com"],
        "browser": ["open", "https://www.google.com"],
        "chrome": ["open", "-a", "Google Chrome"],
        "firefox": ["open", "-a", "Firefox"],
        "safari": ["open", "-a", "Safari"],
        "terminal": ["open", "-a", "Terminal"],
        "archivos": ["open", "-a", "Finder"],
        "explorador": ["open", "-a", "Finder"],
        "calculadora": ["open", "-a", "Calculator"],
        "musica": ["open", "-a", "Music"],
        "spotify": ["open", "-a", "Spotify"],
        "configuracion": ["open", "-a", "System Preferences"],
        "notas": ["open", "-a", "Notes"],
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
        """Abrir una aplicacion por nombre."""
        app_name = app_name.lower().strip()

        if app_name in self.apps:
            cmd = self.apps[app_name]
        else:
            for key in self.apps:
                if key in app_name or app_name in key:
                    cmd = self.apps[key]
                    break
            else:
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

    def run_command(self, command):
        """Ejecutar un comando del sistema y devolver la salida."""
        blocked = ["rm -rf", "mkfs", "dd if=", ":(){", "fork bomb", "format c:"]
        for b in blocked:
            if b in command.lower():
                return "Ese comando esta bloqueado por seguridad."

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10,
            )
            output = result.stdout.strip() or result.stderr.strip()
            return output if output else "Comando ejecutado sin salida."
        except subprocess.TimeoutExpired:
            return "El comando tardo demasiado y fue cancelado."
        except Exception as e:
            return f"Error al ejecutar comando: {e}"

    def list_available_apps(self):
        """Listar aplicaciones disponibles."""
        apps = sorted(self.apps.keys())
        return "Aplicaciones disponibles: " + ", ".join(apps)
