import sys, os, threading, queue
import pyperclip, keyboard
import pystray
from PIL import Image, ImageOps

# --- Windows SAPI via pywin32 ---
import pythoncom
import win32com.client

HOTKEY = 'ctrl+space'  # Read trigger

class TTSWorker(threading.Thread):
    """Dedicated TTS thread (own COM apartment). New 'speak' purges previous output."""
    def __init__(self):
        super().__init__(daemon=True)
        self.q = queue.Queue()
        self._stop_event = threading.Event()
        self.voice = None

    def run(self):
        pythoncom.CoInitialize()
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
            pythoncom.CoUninitialize()

    def speak(self, text: str):
        self._drain()
        self.q.put(("speak", text), block=False)

    def stop_speaking(self):
        self._drain()
        self.q.put(("stop", None), block=False)

    def shutdown(self):
        self._drain()
        self.q.put(("quit", None), block=False)
        self._stop_event.set()

    def _drain(self):
        try:
            while True:
                self.q.get_nowait()
        except queue.Empty:
            pass

# --- App logic ---
tts = TTSWorker(); tts.start()

def read_from_clipboard():
    text = pyperclip.paste()
    if text and text.strip():
        tts.speak(text)
        print("🔊 Reading...")
    else:
        print("ℹ️ Clipboard is empty. Nothing to read.")

def on_hotkey():
    read_from_clipboard()

def start_hotkey_listener():
    keyboard.add_hotkey(HOTKEY, on_hotkey)
    print(f"🎧 LazyBoy is listening for {HOTKEY} ...")
    keyboard.wait()  # blocks this thread only

# --- Tray UI ---
def make_tray_icon_img():
    # Use assets/lazyboy.png if available
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "lazyboy.png")
    size = 64
    try:
        if os.path.exists(icon_path):
            img = Image.open(icon_path).convert("RGBA")
            img = ImageOps.fit(img, (size, size), method=Image.LANCZOS)
            return img
    except Exception:
        pass
    # Fallback: simple neutral circle (dark)
    img = Image.new("RGBA", (size, size), (0,0,0,0))
    return img

def tray_read_now(icon, item):
    read_from_clipboard()

def tray_quit(icon, item):
    print("🛑 Quitting...")
    try:
        tts.shutdown()
    except Exception:
        pass
    icon.stop()
    os._exit(0)

def run_tray():
    menu = pystray.Menu(
        pystray.MenuItem("🟢 Read Now", tray_read_now),
        pystray.MenuItem("🛑 Quit", tray_quit),
    )
    icon = pystray.Icon("LazyBoy", make_tray_icon_img(), "LazyBoy", menu)
    icon.run()

if __name__ == "__main__":
    threading.Thread(target=start_hotkey_listener, daemon=True).start()
    run_tray()
