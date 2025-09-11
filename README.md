# LazyBoy — Clipboard‑to‑Speech (Windows, Tray‑only)

**LazyBoy** is a tiny background assistant for Windows: copy text anywhere (`Ctrl + C`) and trigger reading on demand with **`Ctrl + Space`** — or via the tray menu. No visible window, no clutter. Just copy → listen.

> Built for focus: runs in the system tray, stays quiet until you need it, and interrupts ongoing speech when you trigger a new read.

---

## ✨ Features

- **Tray‑only UI** (system tray near the clock) — no main window
- **Global hotkey:** `Ctrl + Space` to read the current clipboard
- **Tray menu:** “Read Now” and “Quit”
- **Interruptible speech:** a new trigger cancels the previous speech immediately
- **Offline & local:** uses Windows SAPI, no cloud required
- **Lightweight & unobtrusive:** starts fast, stays out of your way

> Windows‑only (uses SAPI via `pywin32`).

---

## 🚀 Quick Start

1. Install Python 3.10+ on Windows.
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Run LazyBoy:
   ```powershell
   python lazyboy.py
   ```
4. Copy any text (`Ctrl + C`) and trigger reading with **`Ctrl + Space`** — or right‑click the tray icon and choose **🟢 Read Now**.

> If the hotkey doesn’t fire, start your terminal **as Administrator** (global keyboard hook requirement on some systems).

---

## 🖱️ Tray Menu

- **🟢 Read Now** — Read the current clipboard contents immediately
- **🛑 Quit** — Exit LazyBoy

---

## 🎨 Icons

- `assets/lazyboy.png` and `assets/lazyboy.ico` are generated from your supplied image and are **round** (transparent corners).

---

## 🔧 How it Works (Architecture)

- A **dedicated TTS worker thread** hosts a Windows SAPI voice (COM apartment via `pythoncom.CoInitialize()`).
- All speech requests go through a **Queue** into that single thread.
- Each new request uses **Purge‑Before‑Speak** so the previous speech is cancelled cleanly.
- The tray icon (via `pystray`) runs in the main thread; the **global hotkey** listener runs in a daemon thread.

---

## 🛡️ Privacy & Security

- Everything runs **locally**.
- LazyBoy only reads what **you copied** into the clipboard when you ask it to. No keylogging, no network calls.

---

## 🧪 Troubleshooting

- **Hotkey doesn’t trigger**: Run your shell as **Administrator**; close conflicting global hook tools.
- **No audio output**: Check Windows audio device / volume; ensure SAPI voices are installed.
- **Tray icon hidden**: Click the tray **up‑arrow** and drag LazyBoy into the visible area.

---

## 📁 Project Structure

```
LazyBoy/
├─ assets/
│  ├─ lazyboy.ico
│  └─ lazyboy.png
├─ lazyboy.py
├─ requirements.txt
├─ start_lazyboy.bat
├─ start_lazyboy.ps1
├─ LICENSE
└─ README.md
```

---

## 📝 License

MIT — see `LICENSE`.
