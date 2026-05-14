"""
Nova Dragon — لوحة المراقبة الحية (Live Dashboard)
الصفحة الرئيسية: إحصائيات + سجل حي + حالة النظام
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from nova.gui.theme.nova_theme import NovaColors
from nova.gui.widgets.nova_widgets import (
    GlassCard,
    LogEntry,
    NeonButton,
    PulseDot,
    StatWidget,
)

if TYPE_CHECKING:
    from zzz_od.context.zzz_context import ZContext


class DashboardView(QWidget):
    """لوحة المراقبة الحية — الصفحة الرئيسية لـ Nova Dragon"""

    def __init__(self, ctx: ZContext | None = None, parent: QWidget | None = None):
        super().__init__(parent)
        self._ctx = ctx
        self.setObjectName("NovaDashboard")

        # عدادات داخلية
        self._battles_count = 0
        self._success_count = 0
        self._session_start = datetime.now()
        self._log_entries: list[LogEntry] = []

        self._build_ui()
        self._start_live_updates()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 12)
        main_layout.setSpacing(16)

        # ═══ العنوان العلوي ═══
        header = QHBoxLayout()
        header.setSpacing(12)

        title = QLabel("لوحة المراقبة")
        title.setStyleSheet(
            f"color: {NovaColors.TEXT_PRIMARY}; font-size: 22px;"
            " font-weight: 800; letter-spacing: 1px;"
        )
        header.addWidget(title, alignment=Qt.AlignmentFlag.AlignRight)

        pulse = PulseDot(NovaColors.NEON_GREEN, size=8)
        header.addWidget(pulse, alignment=Qt.AlignmentFlag.AlignRight)

        live_label = QLabel("LIVE")
        live_label.setStyleSheet(
            f"color: {NovaColors.NEON_GREEN}; font-size: 10px;"
            " font-weight: 700; letter-spacing: 2px;"
        )
        header.addWidget(live_label, alignment=Qt.AlignmentFlag.AlignRight)

        header.addStretch()

        # زر التشغيل
        self._btn_start = NeonButton("▶  تشغيل الأتمتة", color="green")
        self._btn_start.clicked.connect(self._on_start_clicked)
        header.addWidget(self._btn_start)

        self._btn_stop = NeonButton("⏹  إيقاف", color="pink")
        self._btn_stop.clicked.connect(self._on_stop_clicked)
        self._btn_stop.setVisible(False)
        header.addWidget(self._btn_stop)

        main_layout.addLayout(header)

        # ═══ بطاقات الإحصائيات ═══
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)

        self._stat_battery = StatWidget(
            "الطاقة", "240", NovaColors.NEON_CYAN
        )
        stats_layout.addWidget(self._stat_battery)

        self._stat_battles = StatWidget(
            "المعارك", "0", NovaColors.NEON_PURPLE
        )
        stats_layout.addWidget(self._stat_battles)

        self._stat_success = StatWidget(
            "معدل النجاح", "—", NovaColors.NEON_GREEN
        )
        stats_layout.addWidget(self._stat_success)

        self._stat_session = StatWidget(
            "مدة الجلسة", "00:00", NovaColors.NEON_ORANGE
        )
        stats_layout.addWidget(self._stat_session)

        self._stat_tasks = StatWidget(
            "المهام المكتملة", "0", NovaColors.NEON_YELLOW
        )
        stats_layout.addWidget(self._stat_tasks)

        main_layout.addLayout(stats_layout)

        # ═══ المنطقة السفلية: سجل + حالة ═══
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(16)

        # سجل العمليات الحي
        log_card = GlassCard("📋  سجل العمليات")
        self._log_scroll = QScrollArea()
        self._log_scroll.setWidgetResizable(True)
        self._log_scroll.setMinimumHeight(280)
        self._log_scroll.setStyleSheet("background: transparent; border: none;")

        self._log_container = QWidget()
        self._log_layout = QVBoxLayout(self._log_container)
        self._log_layout.setContentsMargins(0, 0, 0, 0)
        self._log_layout.setSpacing(6)
        self._log_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # إضافة بعض العمليات الافتراضية
        self._add_log("تهيئة النظام", "success", "الآن")
        self._add_log("تحميل نماذج YOLO", "success", "الآن")
        self._add_log("في انتظار أمر التشغيل...", "pending", "")

        self._log_scroll.setWidget(self._log_container)
        log_card.content_layout.addWidget(self._log_scroll)
        bottom_layout.addWidget(log_card, stretch=3)

        # بطاقة حالة النظام
        status_card = GlassCard("⚡  حالة النظام", accent=True)

        # حالة اللعبة
        game_row = self._make_status_row("🎮  اللعبة", "غير متصل", NovaColors.TEXT_SECONDARY)
        status_card.content_layout.addLayout(game_row)
        self._game_status_label = game_row.itemAt(1).widget()

        # حالة GPU
        gpu_row = self._make_status_row("🖥️  GPU", "جاهز", NovaColors.NEON_GREEN)
        status_card.content_layout.addLayout(gpu_row)

        # حالة YOLO
        yolo_row = self._make_status_row("👁️  YOLO", "محمّل", NovaColors.NEON_GREEN)
        status_card.content_layout.addLayout(yolo_row)

        # حالة Discord
        discord_row = self._make_status_row("💬  Discord", "غير مفعّل", NovaColors.TEXT_SECONDARY)
        status_card.content_layout.addLayout(discord_row)
        self._discord_status_label = discord_row.itemAt(1).widget()

        # فاصل
        status_card.content_layout.addSpacing(12)

        # شريط تقدم المهمة الحالية
        progress_label = QLabel("المهمة الحالية")
        progress_label.setStyleSheet(
            f"color: {NovaColors.TEXT_SECONDARY}; font-size: 11px;"
        )
        status_card.content_layout.addWidget(progress_label)

        self._progress_bar = QProgressBar()
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setMinimumHeight(8)
        status_card.content_layout.addWidget(self._progress_bar)

        self._current_task_label = QLabel("— في الانتظار —")
        self._current_task_label.setStyleSheet(
            f"color: {NovaColors.NEON_CYAN}; font-size: 12px; font-weight: 600;"
        )
        self._current_task_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_card.content_layout.addWidget(self._current_task_label)

        status_card.content_layout.addStretch()
        bottom_layout.addWidget(status_card, stretch=2)

        main_layout.addLayout(bottom_layout, stretch=1)

    def _make_status_row(
        self, label: str, value: str, color: str
    ) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color: {NovaColors.TEXT_SECONDARY}; font-size: 12px;"
        )
        row.addWidget(lbl)

        val = QLabel(value)
        val.setStyleSheet(
            f"color: {color}; font-size: 12px; font-weight: 600;"
        )
        val.setAlignment(Qt.AlignmentFlag.AlignLeft)
        row.addWidget(val)
        row.addStretch()
        return row

    def _add_log(self, task: str, status: str, time_str: str) -> None:
        entry = LogEntry(task, status, time_str)
        self._log_layout.insertWidget(0, entry)
        self._log_entries.insert(0, entry)
        # الحد الأقصى 50 إدخال
        if len(self._log_entries) > 50:
            old = self._log_entries.pop()
            self._log_layout.removeWidget(old)
            old.deleteLater()

    def _start_live_updates(self) -> None:
        """تحديث مدة الجلسة كل ثانية"""
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_session_time)
        self._timer.start(1000)

    def _update_session_time(self) -> None:
        delta = datetime.now() - self._session_start
        total_seconds = int(delta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if hours > 0:
            self._stat_session.set_value(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        else:
            self._stat_session.set_value(f"{minutes:02d}:{seconds:02d}")

    def _on_start_clicked(self) -> None:
        self._btn_start.setVisible(False)
        self._btn_stop.setVisible(True)
        self._session_start = datetime.now()
        self._add_log("بدء الأتمتة", "running", datetime.now().strftime("%H:%M"))
        self._current_task_label.setText("⏳ جاري التحميل...")

        if self._ctx is not None:
            try:
                self._ctx.run_context.start_running()
            except Exception:
                pass

    def _on_stop_clicked(self) -> None:
        self._btn_start.setVisible(True)
        self._btn_stop.setVisible(False)
        self._add_log("إيقاف الأتمتة", "fail", datetime.now().strftime("%H:%M"))
        self._current_task_label.setText("— متوقف —")
        self._progress_bar.setValue(0)

        if self._ctx is not None:
            try:
                self._ctx.run_context.stop_running()
            except Exception:
                pass

    # ─── واجهة برمجية للتحديث من الخارج ───

    def update_battery(self, value: int) -> None:
        self._stat_battery.set_value(str(value))

    def update_battles(self, count: int) -> None:
        self._battles_count = count
        self._stat_battles.set_value(str(count))

    def update_success_rate(self, rate: float) -> None:
        self._stat_success.set_value(f"{rate:.0f}%")

    def update_tasks_done(self, count: int) -> None:
        self._stat_tasks.set_value(str(count))

    def update_current_task(self, name: str, progress: int) -> None:
        self._current_task_label.setText(name)
        self._progress_bar.setValue(min(progress, 100))

    def log_task(self, name: str, status: str) -> None:
        self._add_log(name, status, datetime.now().strftime("%H:%M"))
