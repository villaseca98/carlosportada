"""
Cerebro de Jarvis.
Procesa comandos de voz y ejecuta acciones usando los demas modulos.
"""

import threading


class Assistant:
    """Asistente principal de Jarvis. Interpreta y ejecuta comandos."""

    def __init__(self, voice, music, system, news):
        self.voice = voice
        self.music = music
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
        """Activado por 2 palmas: play/pause musica."""
        result = self.music.toggle()
        self.voice.say(result)

    def full_briefing(self):
        """Activado por 3 palmas: informe completo."""
        self.voice.say("Preparando tu informe, senor.")

        # Estado del sistema
        status = self.system.get_quick_status()
        self.voice.say(status)

        # Briefing completo (saludo, clima, recordatorios, noticias)
        briefing = self.news.get_full_briefing()
        for line in briefing.split("\n"):
            if line.strip():
                self.voice.say(line.strip())

    def process_command(self, command):
        """Procesar un comando de voz y ejecutar la accion correspondiente."""
        command = command.lower().strip()

        # --- Musica ---
        if any(w in command for w in ["pon musica", "reproduce", "play", "ponme musica"]):
            # Buscar nombre de cancion si se especifica
            song = None
            for prefix in ["pon ", "reproduce ", "play ", "ponme "]:
                if prefix in command:
                    song = command.split(prefix, 1)[-1].strip()
                    if song in ["musica", "una cancion", "algo"]:
                        song = None
                    break
            result = self.music.play(song)
            self.voice.say(result)

        elif any(w in command for w in ["para la musica", "para musica", "stop", "detener"]):
            result = self.music.stop()
            self.voice.say(result)

        elif any(w in command for w in ["pausa", "pause"]):
            result = self.music.pause()
            self.voice.say(result)

        elif any(w in command for w in ["siguiente cancion", "next", "siguiente"]):
            result = self.music.next_song()
            self.voice.say(result)

        elif any(w in command for w in ["anterior", "cancion anterior"]):
            result = self.music.previous_song()
            self.voice.say(result)

        elif "mezcla" in command or "shuffle" in command or "aleatorio" in command:
            result = self.music.shuffle()
            self.voice.say(result)

        elif "volumen" in command:
            try:
                words = command.split()
                for w in words:
                    if w.isdigit():
                        level = int(w) / 100.0
                        result = self.music.set_volume(level)
                        self.voice.say(result)
                        return
                if "sube" in command or "mas" in command:
                    result = self.music.set_volume(self.music.volume + 0.1)
                elif "baja" in command or "menos" in command:
                    result = self.music.set_volume(self.music.volume - 0.1)
                else:
                    result = "Dime el nivel de volumen del 0 al 100."
                self.voice.say(result)
            except Exception:
                self.voice.say("No he entendido el nivel de volumen.")

        elif "que canciones" in command or "lista de canciones" in command:
            result = self.music.list_songs()
            self.voice.say(result)

        # --- Sistema ---
        elif any(w in command for w in ["abre ", "abrir ", "abre el ", "abre la ", "open "]):
            app = command
            for prefix in ["abre el ", "abre la ", "abrir ", "abre ", "open "]:
                if prefix in app:
                    app = app.split(prefix, 1)[-1].strip()
                    break
            result = self.system.open_app(app)
            self.voice.say(result)

        elif any(w in command for w in ["estado del sistema", "sistema", "recursos"]):
            result = self.system.get_system_info()
            self.voice.say(result)

        elif "que aplicaciones" in command or "que apps" in command:
            result = self.system.list_available_apps()
            self.voice.say(result)

        # --- Noticias y actualizaciones ---
        elif any(w in command for w in ["noticias", "titulares", "que pasa en el mundo"]):
            if "deporte" in command:
                result = self.news.get_news("deportes", count=5)
            elif "tecnologia" in command or "tech" in command:
                result = self.news.get_news("tecnologia", count=5)
            else:
                result = self.news.get_news("general", count=5)
            self.voice.say(result)

        elif any(w in command for w in ["clima", "tiempo", "temperatura"]):
            city = "Madrid"
            for prefix in ["clima en ", "tiempo en ", "temperatura en "]:
                if prefix in command:
                    city = command.split(prefix, 1)[-1].strip()
                    break
            result = self.news.get_weather(city)
            self.voice.say(result)

        elif any(w in command for w in ["que hora", "hora", "la hora"]):
            result = self.news.get_time()
            self.voice.say(result)

        elif any(w in command for w in ["que dia", "fecha", "la fecha"]):
            result = self.news.get_date()
            self.voice.say(result)

        # --- Recordatorios ---
        elif "recordatorio" in command or "recuerdame" in command or "apunta" in command:
            text = command
            for prefix in ["recuerdame que ", "recuerdame ", "recordatorio ", "apunta que ", "apunta "]:
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

        # --- Jarvis meta ---
        elif any(w in command for w in ["informe", "briefing", "resumen"]):
            self.full_briefing()

        elif any(w in command for w in [
            "callate", "silencio", "calla", "apagar", "adios",
            "hasta luego", "nos vemos"
        ]):
            self.voice.say("Hasta luego, senor. Estare aqui cuando me necesites.")

        elif any(w in command for w in ["gracias", "thank"]):
            self.voice.say("Para eso estoy, senor.")

        elif any(w in command for w in ["como te llamas", "quien eres", "que eres"]):
            self.voice.say(
                "Soy Jarvis, tu asistente personal de inteligencia artificial. "
                "Estoy aqui para lo que necesites."
            )

        elif "ayuda" in command or "que puedes hacer" in command:
            self.voice.say(
                "Puedo hacer lo siguiente: "
                "Reproducir musica, abrir aplicaciones, "
                "darte noticias y el clima, "
                "informarte del estado del sistema, "
                "gestionar recordatorios, "
                "y darte un informe completo con tres palmas. "
                "Con una palma me activas, con dos palmas controlo la musica."
            )

        else:
            self.voice.say(f"No entendi el comando: {command}. Di 'ayuda' para ver que puedo hacer.")
