"""
Modulo de voz para Jarvis.
- Text-to-Speech: Jarvis habla al usuario
- Speech-to-Text: Reconocimiento de comandos de voz
"""

import threading
import queue


class Voice:
    """Motor de voz de Jarvis: habla y escucha."""

    def __init__(self, language="es", rate=180, volume=1.0):
        self.language = language
        self.rate = rate
        self.volume = volume
        self._speech_queue = queue.Queue()
        self._speaking = False
        self._engine = None
        self._init_engine()
        self._start_speech_worker()

    def _init_engine(self):
        """Inicializar el motor TTS."""
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self.rate)
            self._engine.setProperty("volume", self.volume)

            voices = self._engine.getProperty("voices")
            for voice in voices:
                if "spanish" in voice.name.lower() or "es" in voice.id.lower():
                    self._engine.setProperty("voice", voice.id)
                    break
        except Exception as e:
            print(f"[Jarvis] No se pudo inicializar TTS: {e}")
            self._engine = None

    def _start_speech_worker(self):
        """Hilo que procesa la cola de frases a decir."""
        def worker():
            while True:
                text = self._speech_queue.get()
                if text is None:
                    break
                self._speaking = True
                try:
                    if self._engine:
                        self._engine.say(text)
                        self._engine.runAndWait()
                    else:
                        print(f"[Jarvis dice]: {text}")
                except Exception as e:
                    print(f"[Jarvis] Error al hablar: {e}")
                finally:
                    self._speaking = False
                    self._speech_queue.task_done()

        self._worker = threading.Thread(target=worker, daemon=True)
        self._worker.start()

    def say(self, text):
        """Jarvis dice algo (no bloqueante)."""
        print(f"[Jarvis]: {text}")
        self._speech_queue.put(text)

    def say_sync(self, text):
        """Jarvis dice algo y espera a que termine."""
        print(f"[Jarvis]: {text}")
        self._speech_queue.put(text)
        self._speech_queue.join()

    def listen(self, timeout=5, phrase_time_limit=8):
        """Escuchar un comando de voz y devolver el texto reconocido."""
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 300
            recognizer.dynamic_energy_threshold = True

            with sr.Microphone() as source:
                print("[Jarvis] Escuchando comando...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_time_limit
                )

            print("[Jarvis] Procesando voz...")
            text = recognizer.recognize_google(audio, language="es-ES")
            print(f"[Jarvis] Has dicho: {text}")
            return text.lower()

        except Exception as e:
            error_name = type(e).__name__
            if "WaitTimeoutError" in error_name:
                print("[Jarvis] No se detecto ningun comando.")
            elif "UnknownValueError" in error_name:
                print("[Jarvis] No he entendido lo que has dicho.")
            else:
                print(f"[Jarvis] Error de reconocimiento: {e}")
            return None

    def is_speaking(self):
        """Comprobar si Jarvis esta hablando."""
        return self._speaking

    def shutdown(self):
        """Apagar el motor de voz."""
        self._speech_queue.put(None)
        if self._engine:
            try:
                self._engine.stop()
            except Exception:
                pass
