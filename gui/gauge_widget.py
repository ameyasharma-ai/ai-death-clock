"""Custom circular progress gauge widget.

Renders an antialiased neon arc representing life elapsed percentage
using QPainter vector graphics.
"""

from __future__ import annotations

import math
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QConicalGradient, QFont, QPaintEvent, QPainter, QPen
from PyQt6.QtWidgets import QWidget

from gui.styles import ACCENT_CYAN, ACCENT_ROSE, TEXT_MUTED, TEXT_PRIMARY


class CircularGaugeWidget(QWidget):
    """Custom vector-drawn circular dial for life elapsed percentage.

    Attributes:
        progress: Float percentage value between 0.0 and 100.0.
        subtitle: Small label shown below percentage (e.g., 'ELAPSED').
    """

    def __init__(
        self,
        progress: float = 0.0,
        subtitle: str = "LIVED",
        parent: QWidget | None = None,
    ) -> None:
        """Initialize circular gauge widget.

        Args:
            progress: Initial percentage (0.0 to 100.0).
            subtitle: Label text under percentage.
            parent: Optional parent QWidget.
        """
        super().__init__(parent)
        self._progress: float = max(0.0, min(100.0, progress))
        self._subtitle: str = subtitle
        self.setMinimumSize(95, 95)

    def set_progress(self, value: float) -> None:
        """Update progress value and request repaint.

        Args:
            value: Life elapsed percentage (0.0 to 100.0).
        """
        self._progress = max(0.0, min(100.0, value))
        self.update()

    def set_subtitle(self, text: str) -> None:
        """Update subtitle label text.

        Args:
            text: Caption string.
        """
        self._subtitle = text
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Render the antialiased circular arc and percentage text.

        Args:
            event: Paint event.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        size = min(w, h)
        thickness = max(6.0, size * 0.09)

        # Center rect
        margin = thickness / 2.0 + 4.0
        rect = QRectF(
            (w - size) / 2.0 + margin,
            (h - size) / 2.0 + margin,
            size - 2.0 * margin,
            size - 2.0 * margin,
        )

        center = QPointF(w / 2.0, h / 2.0)

        # 1. Background circle track
        bg_pen = QPen(QColor(255, 255, 255, 22), thickness)
        bg_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(bg_pen)
        painter.drawArc(rect, 0, 360 * 16)

        # 2. Foreground active arc
        span_angle = -int((self._progress / 100.0) * 360.0 * 16.0)
        start_angle = 90 * 16  # Top of circle (12 o'clock)

        # Neon gradient pen
        gradient = QConicalGradient(center, 90.0)
        gradient.setColorAt(0.0, QColor(ACCENT_CYAN))
        gradient.setColorAt(0.6, QColor(ACCENT_ROSE))
        gradient.setColorAt(1.0, QColor(ACCENT_CYAN))

        active_pen = QPen(gradient, thickness)
        active_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(active_pen)
        painter.drawArc(rect, start_angle, span_angle)

        # 3. Center percentage text
        painter.setPen(QColor(TEXT_PRIMARY))
        font_pct = QFont("Segoe UI", int(size * 0.17), QFont.Weight.Bold)
        painter.setFont(font_pct)
        pct_text = f"{self._progress:.1f}%"

        text_rect = QRectF(rect.x(), rect.y() + (rect.height() * 0.15), rect.width(), rect.height() * 0.4)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, pct_text)

        # 4. Center subtitle text
        painter.setPen(QColor(TEXT_MUTED))
        font_sub = QFont("Segoe UI", max(7, int(size * 0.09)), QFont.Weight.DemiBold)
        painter.setFont(font_sub)

        sub_rect = QRectF(rect.x(), rect.y() + (rect.height() * 0.52), rect.width(), rect.height() * 0.3)
        painter.drawText(sub_rect, Qt.AlignmentFlag.AlignCenter, self._subtitle)

        painter.end()
