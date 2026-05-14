"""
Nova Dragon — مكونات الواجهة المخصصة
بطاقات زجاجية، أزرار نيون، مؤشرات حية
"""
from __future__ import annotations

from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QSize,
    Qt,
    QTimer,
    Property,
)
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from nova.gui.theme.nova_theme import NovaColors


# ═══════════════════════════════════════════════════════
#  بطاقة زجاجية (Glass Card)
# ═══════════════════════════════════════════════════════

class GlassCard(QFrame):
    """بطاقة بتأثير الزجاج الشفاف مع حدود متوهجة"""

    def __init__(
        self,
        title: str = "",
        accent: bool = False,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setProperty("class", "glass-card-accent" if accent else "glass-card")

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 16, 20, 16)
        self._layout.setSpacing(12)

        if title:
            self._title_label = QLabel(title)
            self._title_label.setProperty("class", "section-title")
            font = QFont("Cairo", 15, QFont.Weight.Bold)
            self._title_label.setFont(font)
            self._title_label.setStyleSheet(f"color: {NovaColors.TEXT_PRIMARY};")
            self._layout.addWidget(self._title_label)

        # تأثير الظل
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

    @property
    def content_layout(self) -> QVBoxLayout:
        return self._layout


# ═══════════════════════════════════════════════════════
#  زر نيون (Neon Button)
# ═══════════════════════════════════════════════════════

class NeonButton(QPushButton):
    """زر بتأثير النيون المتوهج"""

    def __init__(
        self,
        text: str,
        color: str = "cyan",
        parent: QWidget | None = None,
    ):
        super().__init__(text, parent)

        class_map = {
            "cyan": "neon-btn",
            "pink": "neon-btn-pink",
            "green": "neon-btn-green",
        }
        self.setProperty("class", class_map.get(color, "neon-btn"))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(40)

        # تأثير توهج
        self._glow = QGraphicsDropShadowEffect(self)
        self._glow.setBlurRadius(20)
        color_map = {
            "cyan": QColor(0, 240, 255, 60),
            "pink": QColor(255, 45, 120, 60),
            "green": QColor(57, 255, 20, 60),
        }
        self._glow.setColor(color_map.get(color, QColor(0, 240, 255, 60)))
        self._glow.setOffset(0, 0)
        self.setGraphicsEffect(self._glow)


# ═══════════════════════════════════════════════════════
#  مؤشر إحصائيات (Stat Widget)
# ═══════════════════════════════════════════════════════

class StatWidget(QFrame):
    """مؤشر إحصائيات مع قيمة كبيرة وعنوان صغير"""

    def __init__(
        self,
        label: str,
        value: str = "0",
        color: str = NovaColors.NEON_CYAN,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setProperty("class", "glass-card")
        self.setMinimumWidth(150)
        self.setMinimumHeight(90)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # القيمة الكبيرة
        self._value_label = QLabel(value)
        self._value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._value_label.setStyleSheet(
            f"color: {color}; font-size: 28px; font-weight: 800;"
        )
        layout.addWidget(self._value_label)

        # العنوان الصغير
        self._label = QLabel(label)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setStyleSheet(
            f"color: {NovaColors.TEXT_SECONDARY}; font-size: 11px;"
            " font-weight: 500; letter-spacing: 1px;"
        )
        layout.addWidget(self._label)

    def set_value(self, value: str) -> None:
        self._value_label.setText(value)


# ═══════════════════════════════════════════════════════
#  مؤشر الحالة النابض (Pulse Dot)
# ═══════════════════════════════════════════════════════

class PulseDot(QWidget):
    """نقطة متحركة تنبض لإظهار الحالة الحية"""

    def __init__(
        self,
        color: str = NovaColors.NEON_GREEN,
        size: int = 8,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._color = QColor(color)
        self._size = size
        self._opacity = 1.0
        self.setFixedSize(size * 3, size * 3)

        # أنيميشن النبض
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._toggle_pulse)
        self._timer.start(1000)
        self._pulse_state = True

    def _toggle_pulse(self) -> None:
        self._pulse_state = not self._pulse_state
        self._opacity = 1.0 if self._pulse_state else 0.4
        self.update()

    def set_color(self, color: str) -> None:
        self._color = QColor(color)
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # الهالة الخارجية
        glow_color = QColor(self._color)
        glow_color.setAlphaF(0.15 * self._opacity)
        painter.setBrush(glow_color)
        painter.setPen(Qt.PenStyle.NoPen)
        center = self.rect().center()
        painter.drawEllipse(center, self._size * 1.3, self._size * 1.3)

        # النقطة الداخلية
        dot_color = QColor(self._color)
        dot_color.setAlphaF(self._opacity)
        painter.setBrush(dot_color)
        painter.drawEllipse(center, self._size // 2, self._size // 2)

        painter.end()


# ═══════════════════════════════════════════════════════
#  سجل العمليات الحي (Live Log Entry)
# ═══════════════════════════════════════════════════════

class LogEntry(QFrame):
    """عنصر واحد في سجل العمليات الحي"""

    STATUS_ICONS = {
        "success": ("✅", NovaColors.STATUS_SUCCESS),
        "fail": ("❌", NovaColors.STATUS_FAIL),
        "running": ("⏳", NovaColors.STATUS_RUNNING),
        "pending": ("⬜", NovaColors.STATUS_PENDING),
    }

    def __init__(
        self,
        task_name: str,
        status: str = "pending",
        time_str: str = "",
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setStyleSheet(
            "background-color: rgba(15, 15, 35, 0.4);"
            " border-radius: 8px; padding: 8px 12px;"
            " border: 1px solid rgba(255, 255, 255, 0.04);"
        )
        self.setMinimumHeight(40)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(10)

        # الأيقونة
        icon, color = self.STATUS_ICONS.get(status, ("⬜", NovaColors.STATUS_PENDING))
        icon_label = QLabel(icon)
        icon_label.setFixedWidth(24)
        icon_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(icon_label)

        # اسم المهمة
        name_label = QLabel(task_name)
        name_label.setStyleSheet(
            f"color: {NovaColors.TEXT_PRIMARY}; font-size: 13px; font-weight: 500;"
        )
        layout.addWidget(name_label, 1)

        # الوقت
        if time_str:
            time_label = QLabel(time_str)
            time_label.setStyleSheet(
                f"color: {NovaColors.TEXT_SECONDARY}; font-size: 11px;"
            )
            layout.addWidget(time_label)

    def update_status(self, status: str) -> None:
        icon, _ = self.STATUS_ICONS.get(status, ("⬜", NovaColors.STATUS_PENDING))
        # يمكن تحديث الأيقونة لاحقاً


# ═══════════════════════════════════════════════════════
#  زر التنقل الجانبي (Nav Button)
# ═══════════════════════════════════════════════════════

class NavButton(QPushButton):
    """زر في شريط التنقل الجانبي"""

    def __init__(
        self,
        text: str,
        icon_text: str = "",
        parent: QWidget | None = None,
    ):
        super().__init__(f"  {icon_text}  {text}" if icon_text else f"  {text}", parent)
        self.setProperty("class", "nav-btn")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(44)
