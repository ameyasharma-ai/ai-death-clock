"""Interactive onboarding and life assessment questionnaire dialog.

Presents a multi-step form collecting demographic, geographic, habit,
and psychological parameters, querying Gemini AI to compute lifespan estimates.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from PyQt6.QtCore import QDate, QObject, QThread, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSlider,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from gemini_engine import GeminiEngine
from gui.styles import (
    ACCENT_CYAN,
    ACCENT_GREEN,
    ACCENT_ROSE,
    DIALOG_STYLE,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from models import LifespanEstimate, SavedState, UserProfile, save_profile


class GeminiWorker(QObject):
    """Background worker thread for Gemini API inference.

    Signals:
        finished: Emitted on completion with LifespanEstimate.
        error: Emitted on failure with error message string.
    """

    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, engine: GeminiEngine, profile: UserProfile) -> None:
        """Initialize worker with engine and profile data.

        Args:
            engine: Gemini client instance.
            profile: User questionnaire data.
        """
        super().__init__()
        self.engine = engine
        self.profile = profile

    def run(self) -> None:
        """Execute Gemini API call in background thread."""
        try:
            estimate = self.engine.estimate_lifespan(self.profile)
            self.finished.emit(estimate)
        except Exception as exc:
            self.error.emit(str(exc))


class OnboardingDialog(QDialog):
    """Interactive questionnaire dialog for lifespan assessment.

    Signals:
        assessment_completed: Emitted when profile is successfully created and saved.
    """

    assessment_completed = pyqtSignal(object)

    def __init__(
        self,
        existing_profile: UserProfile | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize questionnaire dialog.

        Args:
            existing_profile: Optional existing profile to prefill.
            parent: Optional parent QWidget.
        """
        super().__init__(parent)
        self.existing_profile = existing_profile
        self.gemini_engine = GeminiEngine()
        self.worker_thread: QThread | None = None
        self.worker: GeminiWorker | None = None

        self.setWindowTitle("AI Death Clock — Life & Geography Assessment")
        self.setMinimumSize(720, 580)
        self.setStyleSheet(DIALOG_STYLE)

        self._build_ui()
        if existing_profile:
            self._prefill(existing_profile)

    def _build_ui(self) -> None:
        """Construct the tabbed form layout and action controls."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 22, 28, 22)
        main_layout.setSpacing(16)

        # Header Banner
        header = QVBoxLayout()
        title = QLabel("AI Lifespan & Longevity Assessment")
        title.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {TEXT_PRIMARY};")
        subtitle = QLabel(
            "Powered by Google Gemini. Provide your life details, geography, and habits "
            "to estimate your life expectancy and progress."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(f"font-size: 13px; color: {TEXT_SECONDARY}; line-height: 1.4;")
        header.addWidget(title)
        header.addWidget(subtitle)
        main_layout.addLayout(header)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_demographics_tab(), "1. Geography")
        self.tabs.addTab(self._create_lifestyle_tab(), "2. Habits")
        self.tabs.addTab(self._create_health_tab(), "3. Health")
        self.tabs.addTab(self._create_mind_tab(), "4. Mind & Tribe")
        main_layout.addWidget(self.tabs)

        # Status and Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {ACCENT_CYAN};")
        main_layout.addWidget(self.status_label)

        # Button Bar
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        btn_layout.addStretch()

        self.btn_submit = QPushButton("🔮 Calculate Lifespan with Gemini AI")
        self.btn_submit.setObjectName("PrimaryButton")
        self.btn_submit.setStyleSheet(
            f"background-color: {ACCENT_ROSE}; color: white; padding: 10px 20px; font-size: 13px; font-weight: 700; border-radius: 8px;"
        )
        self.btn_submit.clicked.connect(self._on_submit)
        btn_layout.addWidget(self.btn_submit)

        main_layout.addLayout(btn_layout)

    def _create_demographics_tab(self) -> QWidget:
        """Create tab for birth date, sex, and geographic location.

        Returns:
            QWidget: Configured tab widget.
        """
        page = QWidget()
        layout = QFormLayout(page)
        layout.setSpacing(14)
        layout.setContentsMargins(10, 14, 10, 10)

        self.input_birth = QDateEdit()
        self.input_birth.setCalendarPopup(True)
        self.input_birth.setDisplayFormat("yyyy-MM-dd")
        self.input_birth.setDate(QDate(1998, 5, 15))
        layout.addRow("Date of Birth:", self.input_birth)

        self.input_sex = QComboBox()
        self.input_sex.addItems(["Male", "Female", "Other"])
        layout.addRow("Biological Sex:", self.input_sex)

        self.input_country = QLineEdit("India")
        layout.addRow("Country of Residence:", self.input_country)

        self.input_city = QLineEdit("Pune")
        layout.addRow("City / Region:", self.input_city)

        self.input_living_area = QComboBox()
        self.input_living_area.addItems(["Urban", "Suburban", "Rural"])
        layout.addRow("Living Environment:", self.input_living_area)

        self.input_air_quality = QComboBox()
        self.input_air_quality.addItems(
            ["Clean / Mountain / Forest", "Moderate Urban", "High Air Pollution / Smog"]
        )
        self.input_air_quality.setCurrentIndex(1)
        layout.addRow("Air Quality / Pollution:", self.input_air_quality)

        return page

    def _create_lifestyle_tab(self) -> QWidget:
        """Create tab for sleep, exercise, and dietary patterns.

        Returns:
            QWidget: Configured tab widget.
        """
        page = QWidget()
        layout = QFormLayout(page)
        layout.setSpacing(14)
        layout.setContentsMargins(10, 14, 10, 10)

        # Sleep hours slider & label
        sleep_box = QHBoxLayout()
        self.slider_sleep = QSlider(Qt.Orientation.Horizontal)
        self.slider_sleep.setRange(4, 12)
        self.slider_sleep.setValue(7)
        self.label_sleep = QLabel("7.0 hours/night")
        self.slider_sleep.valueChanged.connect(
            lambda val: self.label_sleep.setText(f"{val}.0 hours/night")
        )
        sleep_box.addWidget(self.slider_sleep)
        sleep_box.addWidget(self.label_sleep)
        layout.addRow("Average Daily Sleep:", sleep_box)

        self.input_sleep_quality = QComboBox()
        self.input_sleep_quality.addItems(
            ["Poor / Fragmented", "Moderate", "Deep / Restorative"]
        )
        self.input_sleep_quality.setCurrentIndex(1)
        layout.addRow("Sleep Quality:", self.input_sleep_quality)

        self.input_exercise = QComboBox()
        self.input_exercise.addItems([
            "Sedentary (Rarely exercise)",
            "Light (1-2x per week)",
            "Moderate (3-4x/wk cardio/resistance)",
            "Athletic / High Performance (5+x/wk)",
        ])
        self.input_exercise.setCurrentIndex(2)
        layout.addRow("Physical Activity:", self.input_exercise)

        self.input_diet = QComboBox()
        self.input_diet.addItems([
            "Balanced Home-cooked (Whole foods)",
            "Mediterranean Diet (Olive oil, fish, greens)",
            "Vegetarian / Plant-focused",
            "Keto / Low-Carb",
            "Processed / Fast Food Frequent",
        ])
        layout.addRow("Primary Nutrition Pattern:", self.input_diet)

        return page

    def _create_health_tab(self) -> QWidget:
        """Create tab for smoking, alcohol, genetics, and conditions.

        Returns:
            QWidget: Configured tab widget.
        """
        page = QWidget()
        layout = QFormLayout(page)
        layout.setSpacing(14)
        layout.setContentsMargins(10, 14, 10, 10)

        self.input_smoking = QComboBox()
        self.input_smoking.addItems([
            "Non-smoker (Never smoked)",
            "Former smoker (Quit >2 years ago)",
            "Vaper / E-cigarette user",
            "Regular smoker (Daily tobacco)",
        ])
        layout.addRow("Smoking / Inhalation:", self.input_smoking)

        self.input_alcohol = QSpinBox()
        self.input_alcohol.setRange(0, 50)
        self.input_alcohol.setValue(1)
        self.input_alcohol.setSuffix(" drinks/wk")
        layout.addRow("Alcohol Intake:", self.input_alcohol)

        self.input_caffeine = QSpinBox()
        self.input_caffeine.setRange(0, 10)
        self.input_caffeine.setValue(2)
        self.input_caffeine.setSuffix(" cups/day")
        layout.addRow("Caffeine Intake:", self.input_caffeine)

        self.input_family = QComboBox()
        self.input_family.addItems([
            "Exceptional (Parents/Grandparents lived 85+)",
            "Average (~70-80 years)",
            "Below average (<70 years or early cardiac history)",
        ])
        layout.addRow("Family Longevity History:", self.input_family)

        self.input_conditions = QLineEdit("None")
        layout.addRow("Chronic Health Conditions:", self.input_conditions)

        return page

    def _create_mind_tab(self) -> QWidget:
        """Create tab for stress, work, social connection, and life mission.

        Returns:
            QWidget: Configured tab widget.
        """
        page = QWidget()
        layout = QFormLayout(page)
        layout.setSpacing(14)
        layout.setContentsMargins(10, 14, 10, 10)

        # Stress level slider
        stress_box = QHBoxLayout()
        self.slider_stress = QSlider(Qt.Orientation.Horizontal)
        self.slider_stress.setRange(1, 10)
        self.slider_stress.setValue(5)
        self.label_stress = QLabel("5 / 10 (Moderate)")
        self.slider_stress.valueChanged.connect(self._update_stress_label)
        stress_box.addWidget(self.slider_stress)
        stress_box.addWidget(self.label_stress)
        layout.addRow("Daily Stress Level:", stress_box)

        self.input_work = QComboBox()
        self.input_work.addItems([
            "Desk / Sedentary (Software / Office)",
            "Active / Walking / Standing",
            "Heavy Physical Labor",
        ])
        layout.addRow("Work Nature:", self.input_work)

        self.input_social = QComboBox()
        self.input_social.addItems([
            "Strong Family & Lifelong Friends (Tight tribe)",
            "Moderate (A few close friends)",
            "Isolated / Limited Social Contact",
        ])
        layout.addRow("Social Connections:", self.input_social)

        self.input_purpose = QComboBox()
        self.input_purpose.addItems([
            "High / Clear Life Mission & Passion (Ikigai)",
            "Moderate (Content with daily life)",
            "Unclear / Searching for Purpose",
        ])
        layout.addRow("Sense of Life Purpose:", self.input_purpose)

        return page

    def _update_stress_label(self, val: int) -> None:
        """Update stress caption based on slider value.

        Args:
            val: Numeric score 1 to 10.
        """
        desc = "Low" if val <= 3 else "Moderate" if val <= 6 else "High / Chronic"
        self.label_stress.setText(f"{val} / 10 ({desc})")

    def _prefill(self, p: UserProfile) -> None:
        """Prefill UI controls from an existing profile.

        Args:
            p: UserProfile instance.
        """
        try:
            d = date.fromisoformat(p.birth_date)
            self.input_birth.setDate(QDate(d.year, d.month, d.day))
        except Exception:
            pass

        self.input_country.setText(p.country)
        self.input_city.setText(p.city)
        self.slider_sleep.setValue(int(p.sleep_hours))
        self.input_alcohol.setValue(p.alcohol_units_per_week)
        self.input_caffeine.setValue(p.caffeine_daily_cups)
        self.slider_stress.setValue(p.stress_level)
        self.input_conditions.setText(p.chronic_conditions)

    def _collect_profile(self) -> UserProfile:
        """Extract user inputs into a validated UserProfile instance.

        Returns:
            UserProfile: Aggregated questionnaire answers.
        """
        qdate = self.input_birth.date()
        birth_str = f"{qdate.year():04d}-{qdate.month():02d}-{qdate.day():02d}"

        return UserProfile(
            birth_date=birth_str,
            biological_sex=self.input_sex.currentText(),
            country=self.input_country.text().strip() or "Global",
            city=self.input_city.text().strip() or "City",
            living_area=self.input_living_area.currentText(),
            air_quality=self.input_air_quality.currentText(),
            sleep_hours=float(self.slider_sleep.value()),
            sleep_quality=self.input_sleep_quality.currentText(),
            exercise_frequency=self.input_exercise.currentText(),
            diet_type=self.input_diet.currentText(),
            smoking_status=self.input_smoking.currentText(),
            alcohol_units_per_week=self.input_alcohol.value(),
            caffeine_daily_cups=self.input_caffeine.value(),
            stress_level=self.slider_stress.value(),
            work_nature=self.input_work.currentText(),
            social_connection=self.input_social.currentText(),
            sense_of_purpose=self.input_purpose.currentText(),
            family_longevity=self.input_family.currentText(),
            chronic_conditions=self.input_conditions.text().strip() or "None",
        )

    def _on_submit(self) -> None:
        """Handle submit action: trigger background Gemini analysis."""
        profile = self._collect_profile()

        # UI state transition
        self.btn_submit.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Querying Google Gemini AI Longevity Engine...")

        self.worker_thread = QThread()
        self.worker = GeminiWorker(self.gemini_engine, profile)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_analysis_success)
        self.worker.error.connect(self._on_analysis_error)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.error.connect(self.worker_thread.quit)

        self.worker_thread.start()

    def _on_analysis_success(self, estimate: LifespanEstimate) -> None:
        """Handle successful Gemini response, save state, and emit signal.

        Args:
            estimate: Calculated LifespanEstimate object.
        """
        profile = self._collect_profile()
        state = SavedState(profile=profile, estimate=estimate)
        save_profile(state)

        self.progress_bar.setVisible(False)
        self.status_label.setText("Longevity estimation complete!")

        # Show brief summary message
        QMessageBox.information(
            self,
            "Actuarial Analysis Complete",
            f"Estimated Lifespan: {estimate.estimated_lifespan_years:.1f} years\n\n"
            f"Baseline Country Expectancy: {estimate.baseline_country_expectancy:.1f} years\n"
            f"Net Lifestyle Modifier: {estimate.net_lifestyle_modifier_years:+.1f} years\n\n"
            f"Summary:\n{estimate.summary}\n\n"
            "Launching your desktop death clock widget now!",
        )

        self.assessment_completed.emit(state)
        self.accept()

    def _on_analysis_error(self, err_msg: str) -> None:
        """Handle API failure by alerting the user.

        Args:
            err_msg: Error message details.
        """
        self.btn_submit.setEnabled(True)
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Estimation failed.")

        QMessageBox.critical(
            self,
            "Gemini Analysis Error",
            f"Could not calculate lifespan with Gemini API:\n\n{err_msg}\n\n"
            "Please check your internet connection or API key configuration in .env.",
        )
