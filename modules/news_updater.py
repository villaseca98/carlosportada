"""
Modulo de noticias y actualizaciones para Jarvis.
Obtiene noticias, hora, fecha, clima y recordatorios.
"""

import datetime
import threading
import json
import os


class NewsUpdater:
    """Proveedor de noticias y actualizaciones de Jarvis."""

    # Feeds RSS en espanol
    RSS_FEEDS = {
        "general": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",
        "tecnologia": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/tecnologia/portada",
        "deportes": "https://e00-marca.uecdn.es/rss/portada.xml",
    }

    def __init__(self, reminders_file="reminders.json"):
        self.reminders_file = reminders_file
        self.reminders = self._load_reminders()

    def get_greeting(self):
        """Saludo segun la hora del dia."""
        hour = datetime.datetime.now().hour
        if 6 <= hour < 13:
            greeting = "Buenos dias"
        elif 13 <= hour < 20:
            greeting = "Buenas tardes"
        else:
            greeting = "Buenas noches"

        now = datetime.datetime.now()
        date_str = now.strftime("%A %d de %B de %Y")
        time_str = now.strftime("%H:%M")

        return f"{greeting} senor. Son las {time_str}, {date_str}."

    def get_time(self):
        """Obtener la hora actual."""
        now = datetime.datetime.now()
        return f"Son las {now.strftime('%H:%M')}."

    def get_date(self):
        """Obtener la fecha actual."""
        now = datetime.datetime.now()
        return f"Hoy es {now.strftime('%A %d de %B de %Y')}."

    def get_news(self, category="general", count=5):
        """Obtener titulares de noticias por RSS."""
        try:
            import feedparser

            url = self.RSS_FEEDS.get(category, self.RSS_FEEDS["general"])
            feed = feedparser.parse(url)

            if not feed.entries:
                return "No pude obtener noticias en este momento."

            headlines = []
            for entry in feed.entries[:count]:
                headlines.append(entry.title)

            result = f"Ultimas noticias de {category}:\n"
            result += "\n".join(f"  {i+1}. {h}" for i, h in enumerate(headlines))
            return result

        except ImportError:
            return "El modulo de noticias no esta disponible. Instala feedparser."
        except Exception as e:
            return f"Error al obtener noticias: {e}"

    def get_weather(self, city="Madrid"):
        """Obtener el clima actual (usando wttr.in, no necesita API key)."""
        try:
            import requests
            response = requests.get(
                f"https://wttr.in/{city}?format=j1",
                timeout=5,
                headers={"Accept-Language": "es"},
            )
            data = response.json()
            current = data["current_condition"][0]

            temp = current["temp_C"]
            feels = current["FeelsLikeC"]
            humidity = current["humidity"]
            desc = current.get("lang_es", [{}])
            if desc:
                desc = desc[0].get("value", current.get("weatherDesc", [{}])[0].get("value", ""))
            else:
                desc = current.get("weatherDesc", [{}])[0].get("value", "")

            return (
                f"Clima en {city}: {desc}, "
                f"{temp} grados (sensacion de {feels}), "
                f"humedad del {humidity}%."
            )
        except Exception as e:
            return f"No pude obtener el clima: {e}"

    def get_full_briefing(self):
        """Informe completo para el modo 3 palmas."""
        parts = [
            self.get_greeting(),
            self.get_weather(),
        ]

        pending = self.get_pending_reminders()
        if pending:
            parts.append(pending)

        try:
            parts.append(self.get_news(count=3))
        except Exception:
            pass

        return "\n".join(parts)

    # --- Recordatorios ---

    def _load_reminders(self):
        """Cargar recordatorios del archivo."""
        if os.path.exists(self.reminders_file):
            try:
                with open(self.reminders_file, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_reminders(self):
        """Guardar recordatorios al archivo."""
        try:
            with open(self.reminders_file, "w") as f:
                json.dump(self.reminders, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Jarvis] Error guardando recordatorios: {e}")

    def add_reminder(self, text):
        """Agregar un recordatorio."""
        reminder = {
            "text": text,
            "created": datetime.datetime.now().isoformat(),
            "done": False,
        }
        self.reminders.append(reminder)
        self._save_reminders()
        return f"Recordatorio anadido: {text}"

    def get_pending_reminders(self):
        """Obtener recordatorios pendientes."""
        pending = [r for r in self.reminders if not r["done"]]
        if not pending:
            return ""
        result = f"Tienes {len(pending)} recordatorio(s) pendiente(s):\n"
        result += "\n".join(f"  - {r['text']}" for r in pending)
        return result

    def complete_reminder(self, index):
        """Completar un recordatorio por indice."""
        pending = [r for r in self.reminders if not r["done"]]
        if 0 <= index < len(pending):
            pending[index]["done"] = True
            self._save_reminders()
            return f"Recordatorio completado: {pending[index]['text']}"
        return "Indice de recordatorio no valido."

    def clear_completed(self):
        """Limpiar recordatorios completados."""
        self.reminders = [r for r in self.reminders if not r["done"]]
        self._save_reminders()
        return "Recordatorios completados eliminados."
