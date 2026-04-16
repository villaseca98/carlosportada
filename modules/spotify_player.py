"""
Modulo de Spotify para Jarvis.
Conecta con la API real de Spotify via spotipy.
Reproduce canciones, controla playback, busca artistas, etc.

Requisitos:
  - Cuenta de Spotify Premium (para controlar playback)
  - App creada en https://developer.spotify.com/dashboard
  - Variables en .env: SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI
  - Un dispositivo Spotify activo (movil, PC, web player)
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth


class SpotifyPlayer:
    """Reproductor de Spotify de Jarvis."""

    def __init__(self, client_id, client_secret, redirect_uri, scope):
        self.sp = None
        self._connected = False
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._scope = scope
        self._connect()

    def _connect(self):
        """Autenticarse con Spotify OAuth."""
        if not self._client_id or not self._client_secret:
            print("[Spotify] Faltan credenciales. Configura SPOTIFY_CLIENT_ID y SPOTIFY_CLIENT_SECRET en .env")
            return

        try:
            auth_manager = SpotifyOAuth(
                client_id=self._client_id,
                client_secret=self._client_secret,
                redirect_uri=self._redirect_uri,
                scope=self._scope,
                cache_path=".spotify_cache",
                open_browser=True,
            )
            self.sp = spotipy.Spotify(auth_manager=auth_manager)

            user = self.sp.current_user()
            print(f"[Spotify] Conectado como: {user['display_name']}")
            self._connected = True
        except Exception as e:
            print(f"[Spotify] Error de conexion: {e}")
            self._connected = False

    def is_connected(self):
        return self._connected and self.sp is not None

    def _get_active_device(self):
        """Obtener un dispositivo activo de Spotify."""
        try:
            devices = self.sp.devices()
            if not devices["devices"]:
                return None
            # Buscar dispositivo activo, o usar el primero disponible
            for d in devices["devices"]:
                if d["is_active"]:
                    return d["id"]
            return devices["devices"][0]["id"]
        except Exception:
            return None

    def play_song(self, query):
        """Buscar y reproducir una cancion en Spotify.

        Args:
            query: Nombre de la cancion, ej: "Stronger Kanye West"

        Returns:
            Mensaje con el resultado.
        """
        if not self.is_connected():
            return "No estoy conectado a Spotify. Configura las credenciales en .env"

        try:
            results = self.sp.search(q=query, type="track", limit=1, market="ES")
            tracks = results["tracks"]["items"]

            if not tracks:
                return f"No encontre '{query}' en Spotify."

            track = tracks[0]
            track_name = track["name"]
            artist = track["artists"][0]["name"]
            uri = track["uri"]

            device_id = self._get_active_device()
            if not device_id:
                return (
                    f"Encontre '{track_name}' de {artist}, pero no hay ningun dispositivo "
                    "de Spotify activo. Abre Spotify en tu movil o PC."
                )

            self.sp.start_playback(device_id=device_id, uris=[uri])
            return f"Reproduciendo '{track_name}' de {artist}"

        except spotipy.SpotifyException as e:
            if e.http_status == 403:
                return "Necesitas Spotify Premium para controlar la reproduccion."
            return f"Error de Spotify: {e.msg}"
        except Exception as e:
            return f"Error al reproducir: {e}"

    def play_playlist(self, query):
        """Buscar y reproducir una playlist."""
        if not self.is_connected():
            return "No estoy conectado a Spotify."

        try:
            results = self.sp.search(q=query, type="playlist", limit=1, market="ES")
            playlists = results["playlists"]["items"]

            if not playlists:
                return f"No encontre playlist '{query}'."

            playlist = playlists[0]
            name = playlist["name"]
            uri = playlist["uri"]

            device_id = self._get_active_device()
            if not device_id:
                return f"Encontre la playlist '{name}' pero no hay dispositivo activo."

            self.sp.start_playback(device_id=device_id, context_uri=uri)
            return f"Reproduciendo playlist: {name}"

        except spotipy.SpotifyException as e:
            if e.http_status == 403:
                return "Necesitas Spotify Premium para controlar la reproduccion."
            return f"Error de Spotify: {e.msg}"
        except Exception as e:
            return f"Error al reproducir playlist: {e}"

    def play_artist(self, artist_name):
        """Reproducir lo mas popular de un artista."""
        if not self.is_connected():
            return "No estoy conectado a Spotify."

        try:
            results = self.sp.search(q=f"artist:{artist_name}", type="artist", limit=1)
            artists = results["artists"]["items"]

            if not artists:
                return f"No encontre al artista '{artist_name}'."

            artist = artists[0]
            uri = artist["uri"]

            device_id = self._get_active_device()
            if not device_id:
                return f"Encontre a {artist['name']} pero no hay dispositivo activo."

            self.sp.start_playback(device_id=device_id, context_uri=uri)
            return f"Reproduciendo lo mejor de {artist['name']}"

        except spotipy.SpotifyException as e:
            if e.http_status == 403:
                return "Necesitas Spotify Premium."
            return f"Error: {e.msg}"
        except Exception as e:
            return f"Error: {e}"

    def pause(self):
        """Pausar la reproduccion."""
        if not self.is_connected():
            return "No estoy conectado a Spotify."
        try:
            self.sp.pause_playback()
            return "Spotify en pausa."
        except Exception as e:
            return f"Error al pausar: {e}"

    def resume(self):
        """Reanudar la reproduccion."""
        if not self.is_connected():
            return "No estoy conectado a Spotify."
        try:
            device_id = self._get_active_device()
            self.sp.start_playback(device_id=device_id)
            return "Reanudando Spotify."
        except Exception as e:
            return f"Error al reanudar: {e}"

    def next_track(self):
        """Siguiente cancion."""
        if not self.is_connected():
            return "No estoy conectado a Spotify."
        try:
            self.sp.next_track()
            # Esperar un momento y obtener la nueva cancion
            import time
            time.sleep(0.5)
            current = self.get_current_track()
            return f"Siguiente: {current}"
        except Exception as e:
            return f"Error: {e}"

    def previous_track(self):
        """Cancion anterior."""
        if not self.is_connected():
            return "No estoy conectado a Spotify."
        try:
            self.sp.previous_track()
            import time
            time.sleep(0.5)
            current = self.get_current_track()
            return f"Anterior: {current}"
        except Exception as e:
            return f"Error: {e}"

    def toggle(self):
        """Alternar play/pause."""
        if not self.is_connected():
            return "No estoy conectado a Spotify."
        try:
            playback = self.sp.current_playback()
            if playback and playback["is_playing"]:
                return self.pause()
            else:
                return self.resume()
        except Exception as e:
            return f"Error: {e}"

    def set_volume(self, level):
        """Ajustar volumen (0-100)."""
        if not self.is_connected():
            return "No estoy conectado a Spotify."
        try:
            level = max(0, min(100, int(level)))
            self.sp.volume(level)
            return f"Volumen de Spotify al {level}%"
        except Exception as e:
            return f"Error al cambiar volumen: {e}"

    def get_current_track(self):
        """Obtener cancion actual."""
        if not self.is_connected():
            return "No estoy conectado a Spotify."
        try:
            current = self.sp.current_playback()
            if current and current["item"]:
                track = current["item"]
                name = track["name"]
                artist = track["artists"][0]["name"]
                is_playing = "Reproduciendo" if current["is_playing"] else "En pausa"
                return f"{is_playing}: '{name}' de {artist}"
            return "No hay nada reproduciendose en Spotify."
        except Exception as e:
            return f"Error: {e}"

    def shuffle(self, state=True):
        """Activar/desactivar modo aleatorio."""
        if not self.is_connected():
            return "No estoy conectado a Spotify."
        try:
            self.sp.shuffle(state)
            return f"Modo aleatorio {'activado' if state else 'desactivado'}."
        except Exception as e:
            return f"Error: {e}"

    def get_my_playlists(self, limit=10):
        """Listar las playlists del usuario."""
        if not self.is_connected():
            return "No estoy conectado a Spotify."
        try:
            playlists = self.sp.current_user_playlists(limit=limit)
            if not playlists["items"]:
                return "No tienes playlists."
            result = "Tus playlists:\n"
            for i, p in enumerate(playlists["items"]):
                result += f"  {i+1}. {p['name']} ({p['tracks']['total']} canciones)\n"
            return result.strip()
        except Exception as e:
            return f"Error: {e}"
