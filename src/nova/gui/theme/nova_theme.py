"""
Nova Dragon — Cyberpop Glassmorphism Theme System
نظام الثيم الأساسي المستخرج من Zenless Zone Zero (zenless-ui)
"""

# ═══════════════════════════════════════════════════════
#  لوحة الألوان — ZZZ Original Palette
# ═══════════════════════════════════════════════════════

class NovaColors:
    """ألوان ZZZ الأصلية المستخرجة من نظام التصميم"""

    # الألوان الأساسية
    BLACK = "#000000"
    WHITE = "#ffffff"
    
    # ألوان العناصر (Elements)
    ETHER = "#fe427e"
    FIRE = "#ff5522"
    ELECTRIC = "#2eb6ff"
    ICE = "#98eff0"
    PHYSICAL = "#f0d12a"

    # التدرجات والنيون
    GRADIENT_GREEN = "#91bc00"
    GRADIENT_YELLOW = "#ffea00"

    # الحالات
    SUCCESS = "#00cc0d"
    WARNING = "#ffc300"
    DANGER = "#c01c00"
    INFO = "#cccccc"

    # التوافقية مع المكونات (Aliases)
    STATUS_SUCCESS = SUCCESS
    STATUS_FAIL = DANGER
    STATUS_RUNNING = ELECTRIC
    STATUS_PENDING = INFO

    # الخلفيات (Glassmorphism & CRT)
    BG_DEEP = "#050505"
    BG_PRIMARY = "#0a0a0a"
    BG_SECONDARY = "#141414"
    BG_CARD = "rgba(20, 20, 20, 0.85)"
    BG_GLASS = "rgba(255, 234, 0, 0.08)" # لمسة أصفر نيون
    BG_GLASS_HOVER = "rgba(255, 234, 0, 0.15)"

    # نيون مخصص للواجهة
    NEON_CYAN = ELECTRIC
    NEON_PINK = ETHER
    NEON_GREEN = GRADIENT_GREEN
    NEON_YELLOW = GRADIENT_YELLOW
    NEON_PURPLE = ETHER
    NEON_ORANGE = FIRE

    # النصوص
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "rgba(255, 255, 255, 0.6)"
    TEXT_MUTED = "rgba(255, 255, 255, 0.3)"

    # الحدود
    BORDER_GLASS = "rgba(255, 255, 255, 0.1)"
    BORDER_GLOW = "rgba(145, 188, 0, 0.3)"
    BORDER_ACTIVE = "rgba(145, 188, 0, 0.6)"


# ═══════════════════════════════════════════════════════
#  QSS Stylesheet — ZZZ Cyberpop Theme
# ═══════════════════════════════════════════════════════

NOVA_STYLESHEET = f"""
/* ═══ الخلفية العامة و CRT Effect ═══ */
QMainWindow, QWidget#NovaMainWidget {{
    background-color: {NovaColors.BG_DEEP};
    color: {NovaColors.TEXT_PRIMARY};
    font-family: 'Cairo', 'Inter', sans-serif;
    font-size: 13px;
}}

/* ═══ شريط العنوان المخصص ═══ */
QWidget#NovaTitleBar {{
    background-color: rgba(0, 0, 0, 0.95);
    border-bottom: 2px solid {NovaColors.NEON_YELLOW};
    min-height: 42px;
}}

QLabel#NovaTitleLabel {{
    color: {NovaColors.NEON_YELLOW};
    font-size: 16px;
    font-weight: 800;
    letter-spacing: 2px;
}}

/* ═══ شريط التنقل الجانبي ═══ */
QWidget#NovaNavPanel {{
    background-color: rgba(10, 10, 10, 0.95);
    border-left: 1px solid rgba(255, 234, 0, 0.1);
    min-width: 200px;
    max-width: 200px;
}}

/* أزرار التنقل - Hover Effects */
QPushButton.nav-btn {{
    background-color: transparent;
    color: {NovaColors.TEXT_SECONDARY};
    border: none;
    border-radius: 4px;
    padding: 12px 16px;
    text-align: right;
    font-size: 14px;
    font-weight: 600;
    margin: 2px 8px;
}}

QPushButton.nav-btn:hover {{
    background-color: {NovaColors.BG_GLASS};
    color: {NovaColors.NEON_YELLOW};
}}

QPushButton.nav-btn:checked,
QPushButton.nav-btn[active="true"] {{
    background-color: {NovaColors.BG_GLASS_HOVER};
    color: {NovaColors.NEON_YELLOW};
    border-right: 4px solid {NovaColors.NEON_YELLOW};
}}

/* ═══ بطاقات زجاجية (Glass Cards) ═══ */
QFrame.glass-card {{
    background-color: {NovaColors.BG_CARD};
    border: 1px solid {NovaColors.BORDER_GLASS};
    border-radius: 8px;
    padding: 20px;
}}

QFrame.glass-card:hover {{
    border-color: {NovaColors.BORDER_GLOW};
    background-color: rgba(20, 20, 20, 0.95);
}}

QFrame.glass-card-accent {{
    background-color: rgba(145, 188, 0, 0.05);
    border: 1px solid rgba(145, 188, 0, 0.2);
    border-radius: 8px;
    padding: 20px;
}}

/* ═══ أزرار ZZZ (Slanted Simulation) ═══ */
QPushButton.neon-btn {{
    background-color: {NovaColors.BLACK};
    color: {NovaColors.TEXT_PRIMARY};
    border: 2px solid {NovaColors.NEON_YELLOW};
    border-radius: 0px; /* Sharp edges to match ZZZ */
    padding: 12px 24px;
    font-size: 15px;
    font-weight: 800;
    min-height: 24px;
}}

QPushButton.neon-btn:hover {{
    background-color: {NovaColors.NEON_YELLOW};
    color: {NovaColors.BLACK};
}}

QPushButton.neon-btn:pressed {{
    background-color: {NovaColors.GRADIENT_GREEN};
    border-color: {NovaColors.GRADIENT_GREEN};
    color: {NovaColors.BLACK};
}}

QPushButton.neon-btn-pink {{
    background-color: {NovaColors.BLACK};
    color: {NovaColors.ETHER};
    border: 2px solid {NovaColors.ETHER};
    border-radius: 0px;
    padding: 12px 24px;
    font-size: 15px;
    font-weight: 800;
}}

QPushButton.neon-btn-pink:hover {{
    background-color: {NovaColors.ETHER};
    color: {NovaColors.BLACK};
}}

QPushButton.neon-btn-green {{
    background-color: {NovaColors.BLACK};
    color: {NovaColors.SUCCESS};
    border: 2px solid {NovaColors.SUCCESS};
    border-radius: 0px;
    padding: 12px 24px;
    font-size: 15px;
    font-weight: 800;
}}

QPushButton.neon-btn-green:hover {{
    background-color: {NovaColors.SUCCESS};
    color: {NovaColors.BLACK};
}}

/* ═══ شريط التقدم ═══ */
QProgressBar {{
    background-color: rgba(255, 255, 255, 0.1);
    border: none;
    border-radius: 0px;
    height: 8px;
    text-align: center;
    color: transparent;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {NovaColors.GRADIENT_YELLOW}, stop:1 {NovaColors.GRADIENT_GREEN});
}}

/* ═══ شريط الحالة السفلي ═══ */
QWidget#NovaStatusBar {{
    background-color: {NovaColors.BLACK};
    border-top: 1px solid rgba(255, 234, 0, 0.2);
    min-height: 32px;
    padding: 0px 16px;
}}

QLabel.status-label {{
    color: {NovaColors.TEXT_SECONDARY};
    font-size: 12px;
    font-weight: 600;
}}

QLabel.status-dot-green {{
    color: {NovaColors.SUCCESS};
    font-size: 12px;
}}

QLabel.status-dot-red {{
    color: {NovaColors.DANGER};
    font-size: 12px;
}}

/* ═══ منطقة المحتوى ═══ */
QWidget#NovaContentArea {{
    background-color: transparent;
}}

QScrollArea {{
    background-color: transparent;
    border: none;
}}

QScrollBar:vertical {{
    background-color: rgba(255, 255, 255, 0.05);
    width: 6px;
    margin: 4px 0px;
}}

QScrollBar::handle:vertical {{
    background-color: {NovaColors.NEON_YELLOW};
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {NovaColors.GRADIENT_GREEN};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* ═══ حقول الإدخال ═══ */
QLineEdit, QTextEdit {{
    background-color: rgba(20, 20, 20, 0.8);
    border: 2px solid #323232;
    border-radius: 0px;
    padding: 10px 16px;
    color: {NovaColors.TEXT_PRIMARY};
    font-size: 14px;
    selection-background-color: {NovaColors.NEON_YELLOW};
    selection-color: {NovaColors.BLACK};
}}

QLineEdit:focus, QTextEdit:focus {{
    border-color: {NovaColors.NEON_YELLOW};
}}

/* ═══ القوائم ═══ */
QComboBox {{
    background-color: rgba(20, 20, 20, 0.8);
    border: 2px solid #323232;
    border-radius: 0px;
    padding: 10px 16px;
    color: {NovaColors.TEXT_PRIMARY};
    font-size: 14px;
}}

QComboBox:hover {{
    border-color: {NovaColors.NEON_YELLOW};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox QAbstractItemView {{
    background-color: {NovaColors.BG_PRIMARY};
    border: 2px solid {NovaColors.NEON_YELLOW};
    selection-background-color: {NovaColors.NEON_YELLOW};
    selection-color: {NovaColors.BLACK};
    color: {NovaColors.TEXT_PRIMARY};
}}

/* ═══ العناوين ═══ */
QLabel.section-title {{
    color: {NovaColors.TEXT_PRIMARY};
    font-size: 22px;
    font-weight: 800;
    margin-bottom: 4px;
}}

QLabel.section-subtitle {{
    color: {NovaColors.TEXT_SECONDARY};
    font-size: 13px;
    font-weight: 500;
}}

QLabel.stat-value {{
    color: {NovaColors.NEON_YELLOW};
    font-size: 32px;
    font-weight: 900;
}}

QLabel.stat-label {{
    color: {NovaColors.TEXT_SECONDARY};
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

/* ═══ مؤشر النبض الحي ═══ */
QLabel.pulse-indicator {{
    color: {NovaColors.SUCCESS};
    font-size: 10px;
}}

/* ═══ Tooltips ═══ */
QToolTip {{
    background-color: {NovaColors.BLACK};
    border: 2px solid {NovaColors.NEON_YELLOW};
    color: {NovaColors.TEXT_PRIMARY};
    padding: 8px 12px;
    font-size: 13px;
    font-weight: bold;
}}
"""

