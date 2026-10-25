"""Design system, color tokens, and stylesheets for AI Death Clock.

Implements a dark obsidian glassmorphism aesthetic with neon cyan and rose accents.
"""

from __future__ import annotations

# Color Palette Constants
BG_DARK = "#0d1117"
BG_GLASS = "rgba(18, 22, 34, 0.90)"
BG_GLASS_LIGHT = "rgba(30, 38, 58, 0.75)"
BORDER_GLASS = "rgba(255, 255, 255, 0.12)"
BORDER_GLOW = "rgba(0, 240, 255, 0.40)"

TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#A0AEC0"
TEXT_MUTED = "#64748B"

ACCENT_CYAN = "#00F0FF"
ACCENT_ROSE = "#FF2E63"
ACCENT_GREEN = "#00E676"
ACCENT_AMBER = "#FFB300"
ACCENT_PURPLE = "#9D4EDD"

# Glassmorphic Widget QSS Stylesheet
WIDGET_STYLE = f"""
QWidget#CentralWidget {{
    background-color: {BG_GLASS};
    border: 1px solid {BORDER_GLASS};
    border-radius: 18px;
}}

QWidget#CompactWidget {{
    background-color: {BG_GLASS};
    border: 1px solid {BORDER_GLASS};
    border-radius: 14px;
}}

QLabel {{
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', 'Ubuntu', 'DejaVu Sans', sans-serif;
}}

QLabel#TitleLabel {{
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 1px;
    color: {TEXT_PRIMARY};
}}

QLabel#ClockDisplay {{
    font-family: 'Courier New', 'DejaVu Sans Mono', monospace;
    font-size: 26px;
    font-weight: 700;
    color: {ACCENT_CYAN};
    letter-spacing: 1px;
}}

QLabel#ClockUnit {{
    font-size: 10px;
    font-weight: 600;
    color: {TEXT_MUTED};
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QLabel#StatValue {{
    font-size: 16px;
    font-weight: 700;
    color: {TEXT_PRIMARY};
}}

QLabel#StatCaption {{
    font-size: 10px;
    color: {TEXT_SECONDARY};
    text-transform: uppercase;
}}

QLabel#QuoteText {{
    font-size: 11px;
    font-style: italic;
    color: {TEXT_SECONDARY};
}}

QLabel#QuoteAuthor {{
    font-size: 10px;
    font-weight: 600;
    color: {ACCENT_AMBER};
}}

QPushButton {{
    background-color: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    color: {TEXT_PRIMARY};
    padding: 6px 12px;
    font-size: 11px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: rgba(0, 240, 255, 0.18);
    border: 1px solid {ACCENT_CYAN};
    color: #FFFFFF;
}}

QPushButton:pressed {{
    background-color: rgba(0, 240, 255, 0.30);
}}

QPushButton#PrimaryButton {{
    background-color: {ACCENT_ROSE};
    border: none;
    color: #FFFFFF;
    font-weight: 700;
}}

QPushButton#PrimaryButton:hover {{
    background-color: #ff477e;
}}

QPushButton#IconButton {{
    background: transparent;
    border: none;
    color: {TEXT_MUTED};
    font-size: 14px;
    padding: 2px 6px;
}}

QPushButton#IconButton:hover {{
    color: {TEXT_PRIMARY};
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 6px;
}}

QProgressBar {{
    background-color: rgba(255, 255, 255, 0.08);
    border: none;
    border-radius: 4px;
    height: 7px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {ACCENT_CYAN}, stop:1 {ACCENT_ROSE});
    border-radius: 4px;
}}

QScrollArea {{
    background: transparent;
    border: none;
}}

QScrollBar:vertical {{
    background: rgba(255, 255, 255, 0.04);
    width: 6px;
    border-radius: 3px;
}}

QScrollBar::handle:vertical {{
    background: rgba(255, 255, 255, 0.2);
    border-radius: 3px;
}}
"""

# Questionnaire Dialog Styling
DIALOG_STYLE = f"""
QDialog {{
    background-color: #0b0f19;
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', 'Ubuntu', 'DejaVu Sans', sans-serif;
}}

QLabel {{
    color: {TEXT_PRIMARY};
}}

QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {{
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    color: #FFFFFF;
    padding: 8px 12px;
    font-size: 13px;
}}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus {{
    border: 1px solid {ACCENT_CYAN};
    background-color: rgba(0, 240, 255, 0.05);
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: #161f30;
    color: #FFFFFF;
    selection-background-color: {ACCENT_CYAN};
    selection-color: #000000;
    border: 1px solid rgba(255, 255, 255, 0.2);
}}

QTabWidget::pane {{
    border: 1px solid rgba(255, 255, 255, 0.1);
    background-color: rgba(20, 26, 40, 0.6);
    border-radius: 12px;
    padding: 12px;
}}

QTabBar::tab {{
    background-color: transparent;
    color: {TEXT_MUTED};
    padding: 10px 16px;
    font-weight: 600;
    border-bottom: 2px solid transparent;
}}

QTabBar::tab:selected {{
    color: {ACCENT_CYAN};
    border-bottom: 2px solid {ACCENT_CYAN};
}}

QTabBar::tab:hover {{
    color: {TEXT_PRIMARY};
}}

QSlider::groove:horizontal {{
    height: 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
}}

QSlider::sub-page:horizontal {{
    background: {ACCENT_CYAN};
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: #FFFFFF;
    border: 2px solid {ACCENT_CYAN};
    width: 16px;
    margin: -5px 0;
    border-radius: 8px;
}}

QGroupBox {{
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 10px;
    margin-top: 14px;
    padding-top: 14px;
    font-weight: 700;
    color: {ACCENT_CYAN};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}}
"""
