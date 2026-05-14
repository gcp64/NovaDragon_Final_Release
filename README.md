# Nova Dragon - Automation Framework

An advanced, fully-automated assistant and graphical user interface for Zenless Zone Zero (ZZZ), built upon the robust OneDragon core. Nova Dragon introduces a modern, high-performance WebEngine architecture featuring a Cyberpop Glassmorphism aesthetic that matches the game's original visual identity.

Developed and maintained by **bob**.

## Architecture & Features
- **WebEngine Core:** Utilizing PySide6 `QWebEngineView` coupled with `QWebChannel` for high-performance frontend-backend communication.
- **Cyberpop UI:** Authentic game aesthetics implemented in pure HTML/CSS, featuring geometric elements, CRT scanlines, and CSS `clip-path` chamfered edges.
- **Live Bridge:** Real-time log interception and status monitoring from the underlying Python automation scripts injected directly into the Web DOM.
- **Zero Local Footprint:** Designed dynamically using relative paths (`Path(__file__)`) to ensure the repository can be cloned and run on any machine without hardcoded local environment variables.

## Prerequisites
- Python 3.11+
- Windows OS (Required for direct memory/screen capturing protocols)
- Game must run in Windowed or Borderless mode at 1920x1080 resolution.

## Installation
1. Clone this repository to your local machine:
   ```bash
   git clone <your-github-repo-url>
   cd NovaDragon
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Ensure PySide6 and standard OpenCV libraries are included as per the pyproject.toml specifications).*

## Usage
To launch the Nova Dragon dashboard, execute the main entry point:
```bash
python src/nova/gui/app.py
```
1. Open Zenless Zone Zero and ensure the game is focused.
2. From the Nova Dragon dashboard, navigate to the Main View.
3. Click "Start Automation" to initialize the hook.
4. Monitor live execution logs and intelligent resource prediction metrics via the embedded terminal.

## Legal & Disclaimer
This software is provided "as-is" for educational and personal use. Automating game interactions may violate the Terms of Service of certain software. The developer (bob) assumes no liability for account suspensions or damages resulting from the use of this tool.

---
**Developer:** bob
**License:** MIT License (See LICENSE file for details)
