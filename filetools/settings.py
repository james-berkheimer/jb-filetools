import importlib.metadata
import json
import logging
import os
from pathlib import Path
from typing import Any

log = logging.getLogger("filetools")


class AppConfig:
    """Load and manage application settings from a JSON configuration file."""

    # Define class-level type hints for all attributes
    settings_path: Path
    valid_extensions: set[str]
    excluded_extensions: set[str]
    deletable_extensions: set[str]
    downloading_indicators: set[str]
    ignore_keywords: set[str]
    name_cleanup_flags: list[str]
    year_min: int
    year_max: int
    shows: dict[str, str]
    movies: dict[str, str]
    music: dict[str, str]
    default_source: Path
    _data: dict[str, Any]

    def __init__(self: "AppConfig", settings_path: Path | None = None) -> None:
        """Initialize AppConfig with settings from JSON file."""
        # Set settings path
        env_path = os.getenv("FILETOOLS_SETTINGS")
        if settings_path is not None:
            self.settings_path = Path(settings_path)
        elif env_path:
            self.settings_path = Path(env_path)
        else:
            self.settings_path = Path(__file__).resolve().parents[1] / "settings.json"

        self._data = self._load_settings()

        # File Processing Settings
        file_processing = self._data.get("file_processing", {})
        extensions = file_processing.get("extensions", {})
        keywords = file_processing.get("keywords", {})

        # Convert lists to sets for O(1) lookups
        self.valid_extensions = set(extensions.get("valid", []))
        self.excluded_extensions = set(extensions.get("excluded", []))
        self.deletable_extensions = set(extensions.get("deletable", []))
        self.downloading_indicators = set(keywords.get("downloading", []))
        self.ignore_keywords = set(keywords.get("ignore", []))

        # Metadata Settings
        metadata = self._data.get("metadata", {})
        year_range = metadata.get("year_range", {})
        name_cleanup = metadata.get("name_cleanup", {})

        self.year_min = int(year_range.get("min", 1900))
        self.year_max = int(year_range.get("max", 2030))
        self.name_cleanup_flags = name_cleanup.get("flags", [])

        # Library Settings
        libraries = self._data.get("libraries", {})
        self.shows = {lib["name"]: Path(lib["path"]) for lib in libraries.get("shows", [])}
        self.movies = {lib["name"]: Path(lib["path"]) for lib in libraries.get("movies", [])}
        self.music = {lib["name"]: Path(lib["path"]) for lib in libraries.get("music", [])}

        # Path Settings
        paths = self._data.get("paths", {})
        default_source = paths.get("default_source", "")
        self.default_source = Path(default_source) if default_source else Path.cwd()

        # Load version
        self.version = self._load_version()

    def _load_settings(self: "AppConfig") -> dict[str, Any]:
        """Load and parse the JSON settings file."""
        try:
            log.debug(f"Loading settings from {self.settings_path}")
            with open(self.settings_path) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            log.warning(f"Unable to load valid settings from '{self.settings_path}'. {e}")
            return {}

    def _load_version(self: "AppConfig") -> str:
        """Load the application version from installed package metadata."""
        try:
            return importlib.metadata.version("filetools")
        except importlib.metadata.PackageNotFoundError:
            log.warning("Unable to load filetools package version.")
            return "unknown"
