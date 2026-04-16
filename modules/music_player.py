"""
Modulo de musica para Jarvis.
Reproduce canciones desde la carpeta /music.
Soporta: play, pause, resume, stop, next, volume, shuffle.
"""

import os
import random
import threading


class MusicPlayer:
    """Reproductor de musica de Jarvis."""

    def __init__(self, music_dir="music"):
        self.music_dir = os.path.abspath(music_dir)
        self.playlist = []
        self.current_index = -1
        self.current_song = None
        self.is_playing = False
        self.is_paused = False
        self.volume = 0.7
        self._initialized = False
        self._init_pygame()
        self._scan_music()

    def _init_pygame(self):
        """Inicializar pygame mixer."""
        try:
            import pygame
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            pygame.mixer.music.set_volume(self.volume)
            self._initialized = True
        except Exception as e:
            print(f"[Musica] No se pudo inicializar pygame mixer: {e}")
            self._initialized = False

    def _scan_music(self):
        """Escanear la carpeta de musica y construir la playlist."""
        extensions = {".mp3", ".wav", ".ogg", ".flac", ".m4a"}
        self.playlist = []

        if not os.path.exists(self.music_dir):
            os.makedirs(self.music_dir, exist_ok=True)
            print(f"[Musica] Carpeta creada: {self.music_dir}")
            print("[Musica] Pon tus canciones ahi para que Jarvis las reproduzca!")
            return

        for f in sorted(os.listdir(self.music_dir)):
            if os.path.splitext(f)[1].lower() in extensions:
                self.playlist.append(os.path.join(self.music_dir, f))

        if self.playlist:
            print(f"[Musica] {len(self.playlist)} canciones encontradas.")
        else:
            print(f"[Musica] No hay canciones en {self.music_dir}")

    def play(self, song_name=None):
        """Reproducir una cancion o la siguiente en la playlist."""
        if not self._initialized:
            return "No puedo reproducir musica, el sistema de audio no esta disponible."

        if not self.playlist:
            return "No hay canciones en la carpeta de musica. Pon archivos MP3 en la carpeta 'music'."

        import pygame

        if song_name:
            match = None
            for path in self.playlist:
                if song_name.lower() in os.path.basename(path).lower():
                    match = path
                    break
            if match:
                self.current_index = self.playlist.index(match)
            else:
                return f"No encontre ninguna cancion con '{song_name}'."
        else:
            if self.is_paused:
                return self.resume()
            self.current_index = (self.current_index + 1) % len(self.playlist)

        song_path = self.playlist[self.current_index]
        self.current_song = os.path.basename(song_path)

        try:
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            return f"Reproduciendo: {self.current_song}"
        except Exception as e:
            return f"Error al reproducir {self.current_song}: {e}"

    def pause(self):
        """Pausar la reproduccion."""
        if not self._initialized:
            return "Sistema de audio no disponible."

        import pygame

        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            return f"Pausado: {self.current_song}"
        return "No hay nada reproduciendose."

    def resume(self):
        """Reanudar la reproduccion."""
        if not self._initialized:
            return "Sistema de audio no disponible."

        import pygame

        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            return f"Reanudando: {self.current_song}"
        return "No hay nada pausado."

    def stop(self):
        """Detener la reproduccion."""
        if not self._initialized:
            return "Sistema de audio no disponible."

        import pygame

        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        return "Musica detenida."

    def next_song(self):
        """Siguiente cancion."""
        self.current_index = (self.current_index + 1) % len(self.playlist) if self.playlist else -1
        return self.play()

    def previous_song(self):
        """Cancion anterior."""
        self.current_index = (self.current_index - 1) % len(self.playlist) if self.playlist else -1
        return self.play()

    def shuffle(self):
        """Mezclar playlist y reproducir."""
        if self.playlist:
            random.shuffle(self.playlist)
            self.current_index = -1
            return self.play()
        return "No hay canciones para mezclar."

    def toggle(self):
        """Alternar entre play y pause (para doble palma)."""
        if self.is_playing and not self.is_paused:
            return self.pause()
        elif self.is_paused:
            return self.resume()
        else:
            return self.play()

    def set_volume(self, level):
        """Ajustar volumen (0.0 a 1.0)."""
        if not self._initialized:
            return "Sistema de audio no disponible."

        import pygame

        self.volume = max(0.0, min(1.0, level))
        pygame.mixer.music.set_volume(self.volume)
        return f"Volumen ajustado a {int(self.volume * 100)}%"

    def get_status(self):
        """Obtener estado actual del reproductor."""
        if not self.is_playing and not self.is_paused:
            return "Sin reproduccion activa."
        state = "En pausa" if self.is_paused else "Reproduciendo"
        return f"{state}: {self.current_song} | Volumen: {int(self.volume * 100)}%"

    def list_songs(self):
        """Listar canciones disponibles."""
        if not self.playlist:
            return "No hay canciones disponibles."
        songs = [os.path.basename(s) for s in self.playlist]
        return "Canciones disponibles:\n" + "\n".join(f"  {i+1}. {s}" for i, s in enumerate(songs))
