"""
Modulo de Notion para Jarvis.
Lee tu calendario y tareas del dia desde una base de datos de Notion.

Requisitos:
  - Integracion creada en https://www.notion.so/my-integrations
  - Base de datos compartida con la integracion
  - La BD debe tener una propiedad tipo "Date" para las fechas

Estructura esperada de la BD de Notion:
  - Nombre/Titulo: Nombre del evento o tarea
  - Date/Fecha: Propiedad de tipo Date con la fecha del evento
  - Status/Estado (opcional): Estado de la tarea
  - Priority/Prioridad (opcional): Prioridad
"""

import datetime


class NotionCalendar:
    """Lectura de calendario y tareas desde Notion."""

    def __init__(self, token, calendar_db_id):
        self.client = None
        self._connected = False
        self._token = token
        self._db_id = calendar_db_id
        self._date_property = None
        self._title_property = None
        self._connect()

    def _connect(self):
        """Conectar con la API de Notion."""
        if not self._token or not self._db_id:
            print("[Notion] Faltan credenciales. Configura NOTION_TOKEN y NOTION_CALENDAR_DB en .env")
            return

        try:
            from notion_client import Client
            self.client = Client(auth=self._token)

            # Verificar conexion obteniendo info de la BD
            db = self.client.databases.retrieve(database_id=self._db_id)
            db_title = ""
            if db.get("title"):
                db_title = db["title"][0]["plain_text"] if db["title"] else "Sin titulo"

            # Detectar automaticamente las propiedades de fecha y titulo
            properties = db.get("properties", {})
            for name, prop in properties.items():
                if prop["type"] == "date" and not self._date_property:
                    self._date_property = name
                if prop["type"] == "title" and not self._title_property:
                    self._title_property = name

            print(f"[Notion] Conectado a: {db_title}")
            if self._date_property:
                print(f"[Notion] Propiedad de fecha detectada: '{self._date_property}'")
            else:
                print("[Notion] No se detecto propiedad de fecha. Las consultas por fecha no funcionaran.")

            self._connected = True
        except Exception as e:
            print(f"[Notion] Error de conexion: {e}")
            self._connected = False

    def is_connected(self):
        return self._connected and self.client is not None

    def get_today_events(self):
        """Obtener los eventos/tareas de hoy desde Notion."""
        if not self.is_connected():
            return "No estoy conectado a Notion. Configura las credenciales en .env"

        if not self._date_property:
            return self._get_all_items_fallback()

        today = datetime.date.today().isoformat()

        try:
            response = self.client.databases.query(
                database_id=self._db_id,
                filter={
                    "property": self._date_property,
                    "date": {
                        "equals": today,
                    },
                },
                sorts=[
                    {
                        "property": self._date_property,
                        "direction": "ascending",
                    }
                ],
            )

            pages = response.get("results", [])
            if not pages:
                return "No tienes eventos programados para hoy en Notion."

            return self._format_events(pages, f"Tu agenda para hoy ({today})")

        except Exception as e:
            return f"Error al consultar Notion: {e}"

    def get_week_events(self):
        """Obtener eventos de esta semana."""
        if not self.is_connected():
            return "No estoy conectado a Notion."

        if not self._date_property:
            return "No hay propiedad de fecha en la base de datos."

        today = datetime.date.today()
        end_of_week = today + datetime.timedelta(days=(6 - today.weekday()))

        try:
            response = self.client.databases.query(
                database_id=self._db_id,
                filter={
                    "and": [
                        {
                            "property": self._date_property,
                            "date": {"on_or_after": today.isoformat()},
                        },
                        {
                            "property": self._date_property,
                            "date": {"on_or_before": end_of_week.isoformat()},
                        },
                    ]
                },
                sorts=[
                    {
                        "property": self._date_property,
                        "direction": "ascending",
                    }
                ],
            )

            pages = response.get("results", [])
            if not pages:
                return "No tienes eventos esta semana en Notion."

            return self._format_events(pages, "Tu agenda de esta semana")

        except Exception as e:
            return f"Error al consultar Notion: {e}"

    def get_tomorrow_events(self):
        """Obtener eventos de manana."""
        if not self.is_connected():
            return "No estoy conectado a Notion."

        if not self._date_property:
            return "No hay propiedad de fecha en la base de datos."

        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()

        try:
            response = self.client.databases.query(
                database_id=self._db_id,
                filter={
                    "property": self._date_property,
                    "date": {"equals": tomorrow},
                },
                sorts=[
                    {
                        "property": self._date_property,
                        "direction": "ascending",
                    }
                ],
            )

            pages = response.get("results", [])
            if not pages:
                return "No tienes eventos para manana."

            return self._format_events(pages, f"Tu agenda para manana ({tomorrow})")

        except Exception as e:
            return f"Error: {e}"

    def _get_all_items_fallback(self):
        """Si no hay campo fecha, devolver los items recientes."""
        try:
            response = self.client.databases.query(
                database_id=self._db_id,
                page_size=10,
            )
            pages = response.get("results", [])
            if not pages:
                return "No hay entradas en tu base de datos de Notion."
            return self._format_events(pages, "Ultimas entradas en Notion")
        except Exception as e:
            return f"Error: {e}"

    def _format_events(self, pages, header):
        """Formatear una lista de paginas de Notion como texto."""
        events = []

        for page in pages:
            props = page.get("properties", {})

            # Obtener titulo
            title = "Sin titulo"
            if self._title_property and self._title_property in props:
                title_prop = props[self._title_property]
                if title_prop.get("title"):
                    title = title_prop["title"][0]["plain_text"] if title_prop["title"] else "Sin titulo"
            else:
                for name, prop in props.items():
                    if prop["type"] == "title" and prop.get("title"):
                        title = prop["title"][0]["plain_text"]
                        break

            # Obtener fecha/hora si existe
            time_str = ""
            if self._date_property and self._date_property in props:
                date_prop = props[self._date_property].get("date")
                if date_prop and date_prop.get("start"):
                    start = date_prop["start"]
                    if "T" in start:
                        # Tiene hora
                        time_str = start.split("T")[1][:5]
                    end = date_prop.get("end")
                    if end and "T" in end:
                        time_str += f" - {end.split('T')[1][:5]}"

            # Obtener estado si existe
            status = ""
            for name, prop in props.items():
                if prop["type"] == "status" and prop.get("status"):
                    status = f" [{prop['status']['name']}]"
                    break
                elif prop["type"] == "select" and "estado" in name.lower() and prop.get("select"):
                    status = f" [{prop['select']['name']}]"
                    break

            event_str = f"  {'[' + time_str + '] ' if time_str else ''}{title}{status}"
            events.append(event_str)

        result = f"{header}:\n" + "\n".join(events)
        return result

    def create_event(self, title, date=None):
        """Crear un nuevo evento/tarea en Notion."""
        if not self.is_connected():
            return "No estoy conectado a Notion."

        if not date:
            date = datetime.date.today().isoformat()

        try:
            properties = {}

            # Titulo
            if self._title_property:
                properties[self._title_property] = {
                    "title": [{"text": {"content": title}}]
                }

            # Fecha
            if self._date_property:
                properties[self._date_property] = {
                    "date": {"start": date}
                }

            self.client.pages.create(
                parent={"database_id": self._db_id},
                properties=properties,
            )
            return f"Evento creado en Notion: '{title}' para el {date}"

        except Exception as e:
            return f"Error al crear evento: {e}"
