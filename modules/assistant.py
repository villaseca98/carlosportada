"""
Cerebro de Jarvis.
Procesa comandos de voz y ejecuta acciones:
  - Spotify: reproducir canciones, artistas, playlists
  - Notion: calendario del dia, semana, crear eventos
  - WhatsApp: abrir WhatsApp Web
  - Sistema: abrir apps, estado del sistema
  - Noticias: titulares, clima, hora
"""

import threading


class Assistant:
    """Asistente principal de Jarvis. Interpreta y ejecuta comandos."""

    def __init__(self, voice, spotify, notion, system, news):
        self.voice = voice
        self.spotify = spotify
        self.notion = notion
        self.system = system
        self.news = news
        self._listening = False

    def activate_listening(self):
        """Activado por 1 palma: escuchar un comando de voz."""
        if self._listening:
            return

        self._listening = True
        self.voice.say("Dime, senor.")

        def listen_and_process():
            try:
                command = self.voice.listen(timeout=6, phrase_time_limit=10)
                if command:
                    self.process_command(command)
                else:
                    self.voice.say("No he captado ningun comando.")
            finally:
                self._listening = False

        thread = threading.Thread(target=listen_and_process, daemon=True)
        thread.start()

    def toggle_music(self):
        """Activado por 2 palmas: play/pause Spotify."""
        result = self.spotify.toggle()
        self.voice.say(result)

    def full_briefing(self):
        """Activado por 3 palmas: informe completo del dia."""
        self.voice.say("Preparando tu informe, senor.")

        # Saludo + hora
        self.voice.say(self.news.get_greeting())

        # Estado del sistema
        status = self.system.get_quick_status()
        self.voice.say(status)

        # Clima
        weather = self.news.get_weather()
        self.voice.say(weather)

        # Calendario de Notion
        calendar = self.notion.get_today_events()
        self.voice.say(calendar)

        # Noticias
        try:
            headlines = self.news.get_news(count=3)
            self.voice.say(headlines)
        except Exception:
            pass

        # Recordatorios
        reminders = self.news.get_pending_reminders()
        if reminders:
            self.voice.say(reminders)

        self.voice.say("Eso es todo, senor. A tu disposicion.")

    def process_command(self, command):
        """Procesar un comando de voz y ejecutar la accion correspondiente."""
        command = command.lower().strip()

        # ======================
        # SPOTIFY
        # ======================
        if any(w in command for w in [
            "pon ", "reproduce ", "play ", "ponme ", "pon la cancion",
            "quiero escuchar", "quiero oir",
        ]):
            query = command
            for prefix in [
                "pon la cancion ", "ponme la cancion ",
                "reproduce la cancion ", "quiero escuchar ",
                "quiero oir ", "ponme ", "pon ", "reproduce ", "play ",
            ]:
                if prefix in query:
                    query = query.split(prefix, 1)[-1].strip()
                    break

            # Detectar si es playlist o artista
            if "playlist" in query:
                query = query.replace("playlist", "").strip()
                result = self.spotify.play_playlist(query)
            elif any(w in command for w in ["de ", "artista"]):
                result = self.spotify.play_song(query)
            else:
                result = self.spotify.play_song(query)
            self.voice.say(result)

        elif any(w in command for w in [
            "para la musica", "stop musica", "stop spotify", "detener musica",
            "para spotify",
        ]):
            result = self.spotify.pause()
            self.voice.say(result)

        elif any(w in command for w in ["pausa", "pause"]):
            result = self.spotify.pause()
            self.voice.say(result)

        elif any(w in command for w in ["continua", "resume", "reanuda", "sigue"]):
            result = self.spotify.resume()
            self.voice.say(result)

        elif any(w in command for w in ["siguiente cancion", "next", "siguiente"]):
            result = self.spotify.next_track()
            self.voice.say(result)

        elif any(w in command for w in ["anterior", "cancion anterior", "previous"]):
            result = self.spotify.previous_track()
            self.voice.say(result)

        elif "aleatorio" in command or "shuffle" in command or "mezcla" in command:
            result = self.spotify.shuffle(True)
            self.voice.say(result)

        elif "volumen" in command:
            words = command.split()
            for w in words:
                if w.isdigit():
                    result = self.spotify.set_volume(int(w))
                    self.voice.say(result)
                    return
            if "sube" in command or "mas" in command:
                result = self.spotify.set_volume(80)
            elif "baja" in command or "menos" in command:
                result = self.spotify.set_volume(30)
            else:
                result = "Dime el volumen del 0 al 100."
            self.voice.say(result)

        elif any(w in command for w in [
            "que suena", "que cancion", "que esta sonando", "que escucho",
        ]):
            result = self.spotify.get_current_track()
            self.voice.say(result)

        elif "mis playlist" in command or "mis listas" in command:
            result = self.spotify.get_my_playlists()
            self.voice.say(result)

        # ======================
        # NOTION / CALENDARIO
        # ======================
        elif any(w in command for w in [
            "calendario", "agenda", "que tengo hoy",
            "eventos de hoy", "tareas de hoy", "mi dia",
        ]):
            result = self.notion.get_today_events()
            self.voice.say(result)

        elif any(w in command for w in ["manana", "eventos de manana", "agenda de manana"]):
            result = self.notion.get_tomorrow_events()
            self.voice.say(result)

        elif any(w in command for w in [
            "esta semana", "semana", "eventos de la semana",
        ]):
            result = self.notion.get_week_events()
            self.voice.say(result)

        elif any(w in command for w in ["crear evento", "nuevo evento", "agendar"]):
            text = command
            for prefix in [
                "crear evento ", "nuevo evento ", "agendar ",
                "anade al calendario ",
            ]:
                if prefix in text:
                    text = text.split(prefix, 1)[-1].strip()
                    break
            result = self.notion.create_event(text)
            self.voice.say(result)

        # ======================
        # WHATSAPP
        # ======================
        elif any(w in command for w in ["whatsapp", "whaticket", "wasa", "wasap"]):
            result = self.system.open_whatsapp()
            self.voice.say(result)

        # ======================
        # ABRIR APPS
        # ======================
        elif any(w in command for w in ["abre ", "abrir ", "open "]):
            app = command
            for prefix in [
                "abre el ", "abre la ", "abrir el ", "abrir la ",
                "abrir ", "abre ", "open ",
            ]:
                if prefix in app:
                    app = app.split(prefix, 1)[-1].strip()
                    break
            result = self.system.open_app(app)
            self.voice.say(result)

        # ======================
        # SISTEMA
        # ======================
        elif any(w in command for w in ["estado del sistema", "sistema", "recursos"]):
            result = self.system.get_system_info()
            self.voice.say(result)

        elif "que aplicaciones" in command or "que apps" in command:
            result = self.system.list_available_apps()
            self.voice.say(result)

        # ======================
        # NOTICIAS / CLIMA / HORA
        # ======================
        elif any(w in command for w in ["noticias", "titulares", "que pasa en el mundo"]):
            if "deporte" in command:
                result = self.news.get_news("deportes", count=5)
            elif "tecnologia" in command or "tech" in command:
                result = self.news.get_news("tecnologia", count=5)
            else:
                result = self.news.get_news("general", count=5)
            self.voice.say(result)

        elif any(w in command for w in ["clima", "tiempo", "temperatura"]):
            city = None
            for prefix in ["clima en ", "tiempo en ", "temperatura en "]:
                if prefix in command:
                    city = command.split(prefix, 1)[-1].strip()
                    break
            result = self.news.get_weather(city) if city else self.news.get_weather()
            self.voice.say(result)

        elif any(w in command for w in ["que hora", "hora", "la hora"]):
            result = self.news.get_time()
            self.voice.say(result)

        elif any(w in command for w in ["que dia", "fecha", "la fecha"]):
            result = self.news.get_date()
            self.voice.say(result)

        # ======================
        # RECORDATORIOS
        # ======================
        elif "recordatorio" in command or "recuerdame" in command or "apunta" in command:
            text = command
            for prefix in [
                "recuerdame que ", "recuerdame ", "recordatorio ",
                "apunta que ", "apunta ",
            ]:
                if prefix in text:
                    text = text.split(prefix, 1)[-1].strip()
                    break
            result = self.news.add_reminder(text)
            self.voice.say(result)

        elif "recordatorios" in command or "pendientes" in command:
            result = self.news.get_pending_reminders()
            if result:
                self.voice.say(result)
            else:
                self.voice.say("No tienes recordatorios pendientes.")

        # ======================
        # JARVIS META
        # ======================
        elif any(w in command for w in ["informe", "briefing", "resumen del dia"]):
            self.full_briefing()

        elif any(w in command for w in [
            "callate", "silencio", "calla", "adios",
            "hasta luego", "nos vemos",
        ]):
            self.voice.say("Hasta luego, senor. Estare aqui cuando me necesites.")

        elif any(w in command for w in ["gracias", "thank"]):
            self.voice.say("Para eso estoy, senor.")

        elif any(w in command for w in ["como te llamas", "quien eres", "que eres"]):
            self.voice.say(
                "Soy Jarvis, tu asistente personal. "
                "Controlo Spotify, leo tu agenda de Notion, "
                "abro WhatsApp y lo que necesites."
            )

        elif "ayuda" in command or "que puedes hacer" in command:
            self.voice.say(
                "Puedo hacer lo siguiente: "
                "Poner canciones en Spotify, por ejemplo 'pon Stronger de Kanye West'. "
                "Leer tu calendario de Notion. "
                "Abrir WhatsApp, Chrome, Notion y mas. "
                "Darte noticias, el clima y la hora. "
                "Gestionar recordatorios. "
                "Con una palma me activas. "
                "Con dos palmas pauso o reanudo Spotify. "
                "Con tres palmas te doy el informe completo del dia."
            )

        else:
            self.voice.say(
                f"No entendi el comando: {command}. "
                "Di 'ayuda' para ver que puedo hacer."
            )
