"""
Nova Dragon — النافذة الرئيسية (WebEngine Architecture)
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import logging
from PySide6.QtCore import Qt, QObject, Slot, Signal, QUrl
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel

if TYPE_CHECKING:
    from zzz_od.context.zzz_context import ZContext

class UIWebLogHandler(logging.Handler):
    """مستقبل السجلات الحية لضخها في واجهة الويب"""
    def __init__(self, backend_channel):
        super().__init__()
        self.backend = backend_channel
        self.setFormatter(logging.Formatter('%(message)s'))

    def emit(self, record):
        msg = self.format(record)
        # توجيه الرسالة عبر الـ Signal
        self.backend.logMsg.emit(msg)

class BackendChannel(QObject):
    """الجسر بين JavaScript (الواجهة) والـ Python (المحرك)"""
    logMsg = Signal(str)
    statusUpdate = Signal(str, str, str) # battery, tasks, status

    def __init__(self, ctx: ZContext | None = None):
        super().__init__()
        self._ctx = ctx
        self._bridge = None
        
        if ctx is not None:
            from nova.gui.backend_bridge import NovaBackendBridge
            self._bridge = NovaBackendBridge(ctx)
            self._bridge.on_log(self._on_log)
            self._bridge.on_task_start(self._on_log)
            self._bridge.on_battery_update(self._on_battery)
            self._bridge.on_task_done(self._on_task_done)
            self._bridge.initialize_async()

        self._battery = "180"
        self._tasks = "0"
        self._status = "جاهز"

    @Slot()
    def start_automation(self):
        self.logMsg.emit("🚀 تم طلب بدء الأتمتة من الواجهة...")
        if self._bridge:
            self._bridge.start_one_dragon()
        self._status = "قيد التنفيذ"
        self._emit_status()

    @Slot()
    def stop_automation(self):
        self.logMsg.emit("⏹ تم إيقاف الأتمتة.")
        if self._bridge:
            self._bridge.stop()
        self._status = "متوقف"
        self._emit_status()

    def _on_log(self, msg: str, *args):
        self.logMsg.emit(msg)

    def _on_battery(self, val: int):
        self._battery = str(val)
        self._emit_status()
    
    def _on_task_done(self, name: str, success: bool):
        self._tasks = str(int(self._tasks) + 1)
        self.logMsg.emit(f"✅ اكتملت المهمة: {name}")
        self._emit_status()

    def _emit_status(self):
        self.statusUpdate.emit(self._battery, self._tasks, self._status)


class NovaWebWindow(QMainWindow):
    def __init__(self, ctx: ZContext | None = None):
        super().__init__()
        self.setWindowTitle("Nova Dragon 🐉")
        self.resize(1200, 800)
        self.setMinimumSize(1000, 600)

        # تجهيز WebEngine
        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)

        # إعداد QWebChannel للاتصال بين JS و Python
        self.channel = QWebChannel()
        self.backend = BackendChannel(ctx)
        self.channel.registerObject("backend", self.backend)
        self.browser.page().setWebChannel(self.channel)

        # تحميل مسار الـ HTML المحلي
        web_path = Path(__file__).resolve().parent.parent / "web" / "index.html"
        self.browser.setUrl(QUrl.fromLocalFile(str(web_path)))


def main() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    
    ctx = None
    try:
        from zzz_od.context.zzz_context import ZContext
        ctx = ZContext()
    except Exception:
        pass  # يعمل بدون السياق للمعاينة

    window = NovaWebWindow(ctx=ctx)
    
    # ربط جميع سجلات النظام بالواجهة
    web_logger = UIWebLogHandler(window.backend)
    web_logger.setLevel(logging.INFO)
    logging.getLogger().addHandler(web_logger)
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
