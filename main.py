"""Main application launcher for the AI Death Clock.

Coordinates onboarding flow, background Gemini actuarial calculation,
and the floating desktop widget.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

# Ensure local libs and paths are in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Ensure bundled libxcb-cursor0 is loaded directly before PyQt6 initialization
LIB_FILE = BASE_DIR / "lib" / "usr" / "lib" / "x86_64-linux-gnu" / "libxcb-cursor.so.0"
if LIB_FILE.exists():
    try:
        import ctypes
        ctypes.cdll.LoadLibrary(str(LIB_FILE))
    except Exception as exc:
        print(f"Notice: bundled libxcb-cursor load note: {exc}")

from cli import run_cli_wizard
from gemini_engine import GeminiEngine
from gui.desktop_widget import DesktopDeathClockWidget
from gui.onboarding_dialog import OnboardingDialog
from models import SavedState, load_saved_profile, save_profile


class DeathClockApp:
    """Manages application lifecycle, dialogs, and desktop widget.

    Attributes:
        app: QApplication instance.
        widget: DesktopDeathClockWidget instance.
        state: Loaded or created SavedState.
    """

    def __init__(self, force_setup: bool = False) -> None:
        """Initialize DeathClockApp.

        Args:
            force_setup: If True, forces questionnaire display.
        """
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("AI Death Clock")
        self.force_setup = force_setup
        self.widget: DesktopDeathClockWidget | None = None
        self.state: SavedState | None = load_saved_profile()

    def run(self) -> int:
        """Run the application event loop.

        Returns:
            int: Application exit code.
        """
        if self.state is None or self.force_setup:
            self._show_onboarding()
        else:
            self._show_widget()

        return self.app.exec()

    def _show_onboarding(self) -> None:
        """Display the interactive questionnaire dialog."""
        existing = self.state.profile if self.state else None
        dialog = OnboardingDialog(existing_profile=existing)
        dialog.assessment_completed.connect(self._on_assessment_completed)
        result = dialog.exec()
        if result != OnboardingDialog.DialogCode.Accepted and self.widget is None:
            sys.exit(0)

    def _on_assessment_completed(self, new_state: SavedState) -> None:
        """Handle completion of the onboarding assessment.

        Args:
            new_state: Updated SavedState from assessment.
        """
        self.state = new_state
        if self.widget:
            self.widget.update_state(new_state)
        else:
            self._show_widget()

    def _show_widget(self) -> None:
        """Launch the persistent desktop widget."""
        if not self.state:
            return
        if self.widget is None:
            self.widget = DesktopDeathClockWidget(self.state)
            self.widget.reassess_requested.connect(self._show_onboarding)
        else:
            self.widget.update_state(self.state)
        self.widget.show()


def main() -> None:
    """Parse CLI arguments and dispatch execution."""
    parser = argparse.ArgumentParser(description="AI Death Clock & Longevity Monitor")
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run terminal questionnaire wizard before starting widget",
    )
    parser.add_argument(
        "--setup",
        "--reassess",
        dest="setup",
        action="store_true",
        help="Force open the assessment questionnaire",
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Benchmark and verify available Gemini models",
    )

    args = parser.parse_args()

    if args.scan:
        print("\n🔍 Scanning available Google Gemini models...")
        engine = GeminiEngine()
        results = engine.scan_models()
        print("-" * 55)
        print(f"{'Model Identifier':<30} | {'Status':<10} | {'Latency':<8}")
        print("-" * 55)
        for r in results:
            status = "ONLINE" if r["available"] else "OFFLINE"
            latency = f"{r['latency_s']}s" if r["available"] else "—"
            print(f"{r['model']:<30} | {status:<10} | {latency:<8}")
            if r["error"]:
                print(f"  ↳ Error: {r['error']}")
        print("-" * 55 + "\n")
        return

    if args.cli:
        run_cli_wizard()

    app_runner = DeathClockApp(force_setup=args.setup)
    sys.exit(app_runner.run())


if __name__ == "__main__":
    main()
