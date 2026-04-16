"""
Modulo de deteccion de palmas para Jarvis.
Escucha el microfono y detecta patrones de palmas (claps).
- 1 palma: Activar modo escucha (Jarvis espera comando de voz)
- 2 palmas rapidas: Reproducir/pausar musica
- 3 palmas rapidas: Informe de estado del sistema + noticias
"""

import numpy as np
import time
import threading


class ClapDetector:
    """Detecta palmas usando el microfono."""

    def __init__(self, threshold=3000, clap_interval=0.6, sample_rate=44100, chunk_size=1024):
        self.threshold = threshold
        self.clap_interval = clap_interval
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.running = False
        self.clap_times = []
        self.callbacks = {1: None, 2: None, 3: None}
        self._stream = None
        self._audio = None
        self._thread = None

    def on_clap(self, count, callback):
        """Registrar callback para N palmas."""
        if count in self.callbacks:
            self.callbacks[count] = callback

    def _is_clap(self, audio_data):
        """Detectar si el audio contiene una palma (pico de amplitud corto)."""
        data = np.frombuffer(audio_data, dtype=np.int16)
        peak = np.max(np.abs(data))
        return peak > self.threshold

    def _process_claps(self):
        """Procesar palmas acumuladas y disparar el callback correspondiente."""
        if not self.clap_times:
            return

        now = time.time()
        last_clap = self.clap_times[-1]

        if now - last_clap > self.clap_interval:
            count = len(self.clap_times)
            self.clap_times.clear()

            count = min(count, 3)

            if self.callbacks.get(count):
                try:
                    self.callbacks[count]()
                except Exception as e:
                    print(f"[Jarvis] Error en callback de {count} palma(s): {e}")

    def _listen_loop(self):
        """Bucle principal de escucha del microfono."""
        import pyaudio

        self._audio = pyaudio.PyAudio()
        self._stream = self._audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
        )

        print("[Jarvis] Detector de palmas activado. Escuchando...")
        cooldown = 0.15
        last_clap_time = 0

        while self.running:
            try:
                audio_data = self._stream.read(self.chunk_size, exception_on_overflow=False)
                now = time.time()

                if self._is_clap(audio_data) and (now - last_clap_time) > cooldown:
                    self.clap_times.append(now)
                    last_clap_time = now
                    print(f"[Jarvis] Palma detectada! ({len(self.clap_times)})")

                self._process_claps()

            except Exception as e:
                if self.running:
                    print(f"[Jarvis] Error en escucha: {e}")
                break

        self._cleanup()

    def _cleanup(self):
        """Limpiar recursos de audio."""
        if self._stream:
            try:
                self._stream.stop_stream()
                self._stream.close()
            except Exception:
                pass
        if self._audio:
            try:
                self._audio.terminate()
            except Exception:
                pass

    def start(self):
        """Iniciar deteccion de palmas en un hilo separado."""
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Detener deteccion de palmas."""
        self.running = False
        if self._thread:
            self._thread.join(timeout=2)
