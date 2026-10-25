"""Configuration management for the AI Death Clock application.

Loads environment variables, API keys, fallback model definitions,
and file storage paths for user profiles and widget geometry.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
import dotenv

# Base project paths
APP_DIR = Path(__file__).resolve().parent
ENV_FILE = APP_DIR / ".env"
ROBOT_ENV_FILE = Path("/home/ameya/robot/.env")
DATA_DIR = APP_DIR / "data"
PROFILE_PATH = DATA_DIR / "profile.json"
WIDGET_CONFIG_PATH = DATA_DIR / "widget_config.json"
LIB_PATH = APP_DIR / "lib" / "usr" / "lib" / "x86_64-linux-gnu"
LIB_FILE = LIB_PATH / "libxcb-cursor.so.0"
if LIB_FILE.exists():
    try:
        import ctypes
        ctypes.cdll.LoadLibrary(str(LIB_FILE))
    except Exception:
        pass

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Load environment: check local .env first, then robot .env
if ENV_FILE.exists():
    dotenv.load_dotenv(ENV_FILE)
elif ROBOT_ENV_FILE.exists():
    dotenv.load_dotenv(ROBOT_ENV_FILE)


class Config:
    """Application configuration holder.

    Attributes:
        gemini_api_key: Secret API key for Google Gemini.
        gemini_base_url: Base URL for OpenAI-compatible endpoint.
        gemini_model: Preferred Gemini model ID.
        gemini_fallback_models: Ordered list of fallback models.
        app_name: Title of the desktop application.
    """

    def __init__(self) -> None:
        """Initialize configuration from environment variables."""
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "").strip()
        self.gemini_base_url: str = os.getenv(
            "GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai"
        ).rstrip("/")
        self.gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite").strip()
        
        fallbacks_raw = os.getenv(
            "GEMINI_FALLBACK_MODELS", "gemini-flash-lite-latest,gemini-3.5-flash-lite"
        )
        self.gemini_fallback_models: list[str] = [
            m.strip() for m in fallbacks_raw.split(",") if m.strip()
        ]
        self.app_name: str = "AI Death Clock & Longevity Monitor"

    @property
    def all_models(self) -> list[str]:
        """Return full prioritized list of models to attempt.

        Returns:
            list[str]: Model names with primary first, followed by fallbacks.
        """
        models = [self.gemini_model]
        for m in self.gemini_fallback_models:
            if m not in models:
                models.append(m)
        return models


config = Config()
