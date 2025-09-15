import threading,queue
import pythoncom
import win32com.client

class TSSWorker(threading.Thread):
    """Dedicated TTS thread (own COM apartment). New 'speak' purges previous output."""
    def __init__(self):
        super().__init__(daemon=True)
        self.q = queue.Queue()
        self._stop_event = threading.Event()
        self.voice = None

    def run(self):
        pythonicom.CoInitialize()
        self.voice = win32com.client.Dispatch("SAPI.SpVoice")
        FLAGS_PURGE_ASYNC = 3  # 1=Async, 2=PurgeBeforeSpeak, 3=Async+Purge
        try:
            while not self._stop_event.is_set():
                try:
                    cmd, payload = self.q.get(timeout=0.1)
                except queue.Empty:
                    continue

                if cmd == "speak":
                    text = (payload or "").strip()
                    if text:
                        self.voice.Speak(text, FLAGS_PURGE_ASYNC)
                elif cmd == "stop":
                    self.voice.Speak("", 2)  # purge only
                elif cmd == "quit":
                    self.voice.Speak("", 2)
                    break
        finally:
            try:
                self.voice.Speak("", 2)
            except Exception:
                pass
            pythonicom.CoUninitialize()

    def speak(self,text:str):
        self._drain()
        self.q.put(("speak",text),block=False)

    def stop_speaking(self):
        self._drain()
        self.q.put(("stop",None),block=False)

    def shutdown(self):
        self._drain()
        self.q.put(("quit",None),block=False)
        self._stop_event.set()

    def _drain(self):
        try:
            while True:
                self.q.get_nowait()
        except queue.Empty:
            pass
