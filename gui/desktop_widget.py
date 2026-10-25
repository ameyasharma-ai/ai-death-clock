"""Draggable glassmorphic desktop death clock widget.

Features real-time countdown ticking, circular vector gauge,
persistent screen geometry, compact/expanded modes, and Memento Mori reflections.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any
from PyQt6.QtCore import QPoint, QRect, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QContextMenuEvent, QFont, QIcon, QMouseEvent
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMenu,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from config import WIDGET_CONFIG_PATH
from gui.gauge_widget import CircularGaugeWidget
from gui.styles import (
    ACCENT_AMBER,
    ACCENT_CYAN,
    ACCENT_GREEN,
    ACCENT_ROSE,
    BORDER_GLASS,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    WIDGET_STYLE,
)
from models import SavedState, save_profile
from quotes import get_random_quote


class DesktopDeathClockWidget(QWidget):
    """Floating desktop widget displaying real-time lifespan countdown.

    Attributes:
        state: SavedState containing user profile and Gemini estimate.
    """

    reassess_requested = pyqtSignal()

    def __init__(self, state: SavedState, parent: QWidget | None = None) -> None:
        """Initialize desktop widget.

        Args:
            state: Hydrated application state.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.state = state
        self._drag_pos: QPoint | None = None
        self._is_expanded: bool = False
        self._always_on_top: bool = False
        self._current_quote: dict[str, str] = get_random_quote()

        # Frameless and transparent attributes
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet(WIDGET_STYLE)

        self._build_ui()
        self._load_geometry()

        # High-frequency timer for real-time countdown tick (every 100ms)
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self._update_clock)
        self.timer.start()

        # Quote rotation timer (every 10 minutes)
        self.quote_timer = QTimer(self)
        self.quote_timer.setInterval(600000)
        self.quote_timer.timeout.connect(self._rotate_quote)
        self.quote_timer.start()

        # Initial clock update
        self._update_clock()

    def _build_ui(self) -> None:
        """Construct the widget's layout and controls."""
        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(10, 10, 10, 10)

        # Central glass container
        self.container = QWidget(self)
        self.container.setObjectName("CentralWidget")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(18, 14, 18, 16)
        self.container_layout.setSpacing(10)

        # Header Bar (Drag handle, Title, Controls)
        header = QHBoxLayout()
        header.setSpacing(8)

        # Small pulsating indicator
        self.pulse_dot = QLabel("●")
        self.pulse_dot.setStyleSheet(f"color: {ACCENT_ROSE}; font-size: 11px;")
        header.addWidget(self.pulse_dot)

        self.title_label = QLabel("MEMENTO MORI")
        self.title_label.setObjectName("TitleLabel")
        header.addWidget(self.title_label)

        header.addStretch()

        # Expand/Collapse toggle button
        self.btn_toggle_expand = QPushButton("▾")
        self.btn_toggle_expand.setObjectName("IconButton")
        self.btn_toggle_expand.setToolTip("Toggle AI Longevity Protocol Details")
        self.btn_toggle_expand.clicked.connect(self._toggle_expand)
        header.addWidget(self.btn_toggle_expand)

        # Edit/Reassess button
        self.btn_reassess = QPushButton("⚙")
        self.btn_reassess.setObjectName("IconButton")
        self.btn_reassess.setToolTip("Edit Life Details / Reassess")
        self.btn_reassess.clicked.connect(self.reassess_requested.emit)
        header.addWidget(self.btn_reassess)

        # Close button
        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("IconButton")
        self.btn_close.setToolTip("Close Death Clock")
        self.btn_close.clicked.connect(self.close)
        header.addWidget(self.btn_close)

        self.container_layout.addLayout(header)

        # Main HUD: Gauge on left, Countdown Clock on right
        hud_layout = QHBoxLayout()
        hud_layout.setSpacing(16)

        # Circular Gauge
        self.gauge = CircularGaugeWidget(progress=0.0, subtitle="LIVED")
        hud_layout.addWidget(self.gauge)

        # Countdown details column
        clock_col = QVBoxLayout()
        clock_col.setSpacing(4)

        clock_title = QLabel("TIME REMAINING")
        clock_title.setStyleSheet(f"font-size: 9px; font-weight: 700; color: {TEXT_MUTED}; letter-spacing: 1px;")
        clock_col.addWidget(clock_title)

        self.label_clock = QLabel("00y : 000d : 00h : 00m : 00s")
        self.label_clock.setObjectName("ClockDisplay")
        clock_col.addWidget(self.label_clock)

        # Life Days summary chips
        chips_layout = QHBoxLayout()
        chips_layout.setSpacing(12)

        self.chip_lived = QLabel("Lived: 0 days")
        self.chip_lived.setStyleSheet(f"font-size: 11px; color: {TEXT_SECONDARY}; font-weight: 600;")
        chips_layout.addWidget(self.chip_lived)

        self.chip_rem = QLabel("Remaining: 0 days")
        self.chip_rem.setStyleSheet(f"font-size: 11px; color: {ACCENT_CYAN}; font-weight: 600;")
        chips_layout.addWidget(self.chip_rem)
        chips_layout.addStretch()

        clock_col.addLayout(chips_layout)
        hud_layout.addLayout(clock_col)
        self.container_layout.addLayout(hud_layout)

        # Progress Bar Line
        self.life_bar = QProgressBar()
        self.life_bar.setRange(0, 1000)
        self.life_bar.setTextVisible(False)
        self.container_layout.addWidget(self.life_bar)

        # Memento Mori Quote Box
        self.quote_box = QFrame()
        self.quote_box.setMaximumHeight(75)
        self.quote_box.setStyleSheet(
            f"background-color: rgba(255, 255, 255, 0.04); border-radius: 8px; padding: 6px 10px;"
        )
        quote_layout = QVBoxLayout(self.quote_box)
        quote_layout.setContentsMargins(6, 4, 6, 4)
        quote_layout.setSpacing(2)

        self.label_quote = QLabel(f'"{self._current_quote["quote"]}"')
        self.label_quote.setObjectName("QuoteText")
        self.label_quote.setWordWrap(True)
        quote_layout.addWidget(self.label_quote)

        self.label_author = QLabel(f'— {self._current_quote["author"]}')
        self.label_author.setObjectName("QuoteAuthor")
        self.label_author.setAlignment(Qt.AlignmentFlag.AlignRight)
        quote_layout.addWidget(self.label_author)

        self.container_layout.addWidget(self.quote_box)

        # Expandable AI Insights Section
        self.expandable_section = QWidget()
        self.expand_layout = QVBoxLayout(self.expandable_section)
        self.expand_layout.setContentsMargins(0, 8, 0, 0)
        self.expand_layout.setSpacing(8)

        self._populate_expandable_section()

        self.expandable_section.setVisible(False)
        self.container_layout.addWidget(self.expandable_section)

        self.root_layout.addWidget(self.container)

    def _populate_expandable_section(self) -> None:
        """Populate the expandable details drawer with current estimates and personal factors."""
        # Clear existing layout items
        while self.expand_layout.count():
            child = self.expand_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"color: {BORDER_GLASS};")
        self.expand_layout.addWidget(divider)

        # AI Longevity Heading
        longevity_head = QLabel("GEMINI AI LONGEVITY DECOMPOSITION")
        longevity_head.setStyleSheet(f"font-size: 10px; font-weight: 800; color: {ACCENT_CYAN}; letter-spacing: 1px;")
        self.expand_layout.addWidget(longevity_head)

        # Actuarial comparison
        exp = self.state.estimate
        act_info = QLabel(
            f"Expected Lifespan: {exp.estimated_lifespan_years:.1f} yrs | "
            f"National Baseline: {exp.baseline_country_expectancy:.1f} yrs | "
            f"Net Modifier: {exp.net_lifestyle_modifier_years:+.1f} yrs"
        )
        act_info.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {TEXT_PRIMARY};")
        self.expand_layout.addWidget(act_info)

        # Boosters list
        if exp.top_boosters:
            b_label = QLabel("✦ Longevity Boosters:")
            b_label.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {ACCENT_GREEN};")
            self.expand_layout.addWidget(b_label)
            for b in exp.top_boosters:
                item = QLabel(f"  • {b}")
                item.setWordWrap(True)
                item.setStyleSheet(f"font-size: 10px; color: {TEXT_SECONDARY};")
                self.expand_layout.addWidget(item)

        # Risks list
        if exp.top_risks:
            r_label = QLabel("⚠ Risk Dampeners:")
            r_label.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {ACCENT_AMBER};")
            self.expand_layout.addWidget(r_label)
            for r in exp.top_risks:
                item = QLabel(f"  • {r}")
                item.setWordWrap(True)
                item.setStyleSheet(f"font-size: 10px; color: {TEXT_SECONDARY};")
                self.expand_layout.addWidget(item)

        # Actionable recommendations
        if exp.longevity_recommendations:
            rec_label = QLabel("⚡ Lifespan Expansion Protocol:")
            rec_label.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {ACCENT_CYAN};")
            self.expand_layout.addWidget(rec_label)
            for rec in exp.longevity_recommendations:
                item = QLabel(f"  ➜ {rec}")
                item.setWordWrap(True)
                item.setStyleSheet(f"font-size: 10px; color: #E0E7FF;")
                self.expand_layout.addWidget(item)

        # Personal custom factors and notes indicator
        prof = self.state.profile
        if prof.personal_notes or prof.custom_fields:
            pers_label = QLabel("✦ Personal Factors & Context Analyzed:")
            pers_label.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {ACCENT_ROSE};")
            self.expand_layout.addWidget(pers_label)
            if prof.custom_fields:
                for k, v in prof.custom_fields.items():
                    c_item = QLabel(f"  • {k}: {v}")
                    c_item.setWordWrap(True)
                    c_item.setStyleSheet(f"font-size: 10px; color: {TEXT_MUTED};")
                    self.expand_layout.addWidget(c_item)
            if prof.personal_notes:
                preview = prof.personal_notes[:140] + ("..." if len(prof.personal_notes) > 140 else "")
                p_item = QLabel(f"  ✎ \"{preview}\"")
                p_item.setWordWrap(True)
                p_item.setStyleSheet(f"font-size: 10px; font-style: italic; color: {TEXT_MUTED};")
                self.expand_layout.addWidget(p_item)

    def _toggle_expand(self) -> None:
        """Toggle detailed AI insights visibility."""
        self._is_expanded = not self._is_expanded
        self.expandable_section.setVisible(self._is_expanded)
        self.btn_toggle_expand.setText("▴" if self._is_expanded else "▾")
        self.adjustSize()
        self._save_geometry()

    def update_state(self, new_state: SavedState) -> None:
        """Update widget with a newly calculated state.

        Args:
            new_state: Updated SavedState instance.
        """
        self.state = new_state
        self._populate_expandable_section()
        self._update_clock()
        self.adjustSize()

        self.root_layout.addWidget(self.container)

    def _update_clock(self) -> None:
        """Update live countdown metrics, gauge, and progress bar."""
        now = datetime.now(timezone.utc)
        progress, total_sec, elapsed_sec, rem_sec = self.state.calculate_progress(now)

        # Update gauge and progress bar
        self.gauge.set_progress(progress)
        self.life_bar.setValue(int(progress * 10))

        # Calculate time components for countdown
        rem_total_sec = int(rem_sec)
        rem_days = rem_total_sec // 86400
        rem_years = rem_days // 365
        rem_days_remainder = rem_days % 365
        rem_hours = (rem_total_sec % 86400) // 3600
        rem_minutes = (rem_total_sec % 3600) // 60
        rem_seconds = rem_total_sec % 60

        # Formatted string: 55y : 194d : 14h : 22m : 41s
        clock_str = (
            f"{rem_years:02d}y : {rem_days_remainder:03d}d : "
            f"{rem_hours:02d}h : {rem_minutes:02d}m : {rem_seconds:02d}s"
        )
        self.label_clock.setText(clock_str)

        # Days lived vs remaining chips
        lived_days = int(elapsed_sec // 86400)
        self.chip_lived.setText(f"Lived: {lived_days:,} days")
        self.chip_rem.setText(f"Remaining: {rem_days:,} days")

    def _rotate_quote(self) -> None:
        """Rotate to a new Memento Mori quote."""
        self._current_quote = get_random_quote()
        self.label_quote.setText(f'"{self._current_quote["quote"]}"')
        self.label_author.setText(f'— {self._current_quote["author"]}')

    def _toggle_expand(self) -> None:
        """Toggle detailed AI insights visibility."""
        self._is_expanded = not self._is_expanded
        self.expandable_section.setVisible(self._is_expanded)
        self.btn_toggle_expand.setText("▴" if self._is_expanded else "▾")
        self.adjustSize()
        self._save_geometry()

    def update_state(self, new_state: SavedState) -> None:
        """Update widget with a newly calculated state.

        Args:
            new_state: Updated SavedState instance.
        """
        self.state = new_state
        self._update_clock()
        # Rebuild expandable section with new recommendations
        # (Simply toggle and let next refresh display)

    # ─── Mouse Dragging & Screen Geometry Persistence ───────────────────────
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Record drag start point on mouse press.

        Args:
            event: Mouse press event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Move widget according to cursor drag.

        Args:
            event: Mouse move event.
        """
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Save new widget position on release.

        Args:
            event: Mouse release event.
        """
        self._drag_pos = None
        self._save_geometry()
        event.accept()

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        """Display right-click context menu.

        Args:
            event: Context menu event.
        """
        menu = QMenu(self)
        menu.setStyleSheet(
            f"QMenu {{ background-color: #161f30; color: #FFFFFF; border: 1px solid rgba(255,255,255,0.15); border-radius: 8px; padding: 6px; }} "
            f"QMenu::item:selected {{ background-color: {ACCENT_CYAN}; color: #000000; border-radius: 4px; }}"
        )

        action_expand = menu.addAction("Collapse Details" if self._is_expanded else "Expand Longevity Protocol")
        action_expand.triggered.connect(self._toggle_expand)

        action_quote = menu.addAction("Next Memento Mori Quote")
        action_quote.triggered.connect(self._rotate_quote)

        action_reassess = menu.addAction("⚙ Edit Life Details / Retake Assessment")
        action_reassess.triggered.connect(self.reassess_requested.emit)

        menu.addSeparator()

        action_ontop = menu.addAction("Pin to Top" if not self._always_on_top else "Unpin from Top")
        action_ontop.triggered.connect(self._toggle_always_on_top)

        menu.addSeparator()

        action_close = menu.addAction("✕ Close Widget")
        action_close.triggered.connect(self.close)

        menu.exec(event.globalPos())

    def _toggle_always_on_top(self) -> None:
        """Toggle floating on top vs regular desktop behavior."""
        self._always_on_top = not self._always_on_top
        flags = self.windowFlags()
        if self._always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()

    def _save_geometry(self) -> None:
        """Persist widget position and expanded state to JSON."""
        data = {
            "x": self.x(),
            "y": self.y(),
            "is_expanded": self._is_expanded,
            "always_on_top": self._always_on_top,
        }
        try:
            WIDGET_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(WIDGET_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def _load_geometry(self) -> None:
        """Restore saved widget position from JSON."""
        if not WIDGET_CONFIG_PATH.exists():
            # Default to top right corner of screen
            screen = QApplication.primaryScreen()
            if screen:
                geom = screen.availableGeometry()
                self.move(geom.width() - 480, 60)
            return

        try:
            with open(WIDGET_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            x = data.get("x", 100)
            y = data.get("y", 100)
            self.move(x, y)
            if data.get("is_expanded", False):
                self._toggle_expand()
        except Exception:
            pass
