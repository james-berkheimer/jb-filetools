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
    do_not_delete: list[str]
    files_to_delete: list[str]
    file_extension_excludes: list[str]
    file_name_ignores: list[str]
    name_cleanup_flags: list[str]
    video_file_extensions: list[str]
    year_min: int
    year_max: int
    shows: dict[str, str]
    movies: dict[str, str]
    music: dict[str, str]
    default_source: str
    _data: dict[str, Any]

    def __init__(self: "AppConfig", settings_path: Path | None = None) -> None:
        """Initialize AppConfig with settings from JSON file.

        Args:
            settings_path: Path to the JSON settings file

        Raises:
            FileNotFoundError: If settings file doesn't exist
            json.JSONDecodeError: If settings file contains invalid JSON
        """
        env_path = os.getenv("FILETOOLS_SETTINGS")
        if settings_path is not None:
            self.settings_path = Path(settings_path)
        elif env_path:
            self.settings_path = Path(env_path)
        else:
            self.settings_path = Path(__file__).resolve().parents[1] / "settings.json"

        self._data = self._load_settings()

        # Parse file-related lists with explicit types
        self.do_not_delete = self._data.get("do_not_delete", [])
        self.files_to_delete = self._data.get("files_to_delete", [])
        self.file_extension_excludes = self._data.get("file_extension_excludes", [])
        self.file_name_ignores = self._data.get("file_name_ignores", [])
        self.name_cleanup_flags = self._data.get("name_cleanup_flags", [])
        self.video_file_extensions = self._data.get("video_file_extensions", [])

        # Load year range with explicit types
        self.year_min = int(self._data.get("year_min", 1900))
        self.year_max = int(self._data.get("year_max", 3000))

        # Parse libraries section and convert all paths to Path objects
        libraries = self._data.get("libraries", {})
        self.shows = {lib["name"]: Path(lib["path"]) for lib in libraries.get("shows", [])}
        self.movies = {lib["name"]: Path(lib["path"]) for lib in libraries.get("movies", [])}
        self.music = {lib["name"]: Path(lib["path"]) for lib in libraries.get("music", [])}

        # Convert default_source to Path
        default_source = self._data.get("default_source", "")
        self.default_source = Path(default_source) if default_source else Path.cwd()

        # Load the application version
        self.version = self._load_version()

    def _load_settings(self: "AppConfig") -> dict[str, any]:
        """Load and parse the JSON settings file.

        Returns:
            Dict[str, any]: Parsed settings data or empty dict if loading fails

        Raises:
            FileNotFoundError: If settings file doesn't exist
            json.JSONDecodeError: If settings file contains invalid JSON
        """
        try:
            log.debug(f"Loading settings from {self.settings_path}")
            with open(self.settings_path) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            log.warning(f"Unable to load valid settings from '{self.settings_path}'. {e}")
            return {}

    def _load_version(self: "AppConfig") -> str:
        """Load the application version from the VERSION file.

        Returns:
            str: The application version as a string.

        Raises:
            FileNotFoundError: If the VERSION file doesn't exist.
        """
        version_file = self.settings_path.parent / "VERSION"
        try:
            with open(version_file) as f:
                return f.read().strip()
        except FileNotFoundError:
            log.warning(f"VERSION file not found at {version_file}")
            return "unknown"
