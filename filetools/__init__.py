from pathlib import Path

from .settings import AppConfig

# Global settings instance (loaded once)
PROJECT_ROOT = Path(__file__).parent.parent
SETTINGS_PATH = Path(PROJECT_ROOT, "settings.json")
CONFIG = AppConfig(SETTINGS_PATH)
