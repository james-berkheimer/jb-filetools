import json
import logging
from pathlib import Path

log = logging.getLogger("filetools")


class AppConfig:
    """Loads settings from a JSON file and provides structured access."""

    def __init__(self, settings_path: Path):
        self.settings_path = settings_path
        self._data = self._load_settings()

        # Parse file-related lists

        self.do_not_delete = self._data.get("do_not_delete", [])
        self.files_to_delete = self._data.get("files_to_delete", [])
        self.file_excludes = self._data.get("file_excludes", [])
        self.file_ignores = self._data.get("file_ignores", [])
        self.name_cleanup_flags = self._data.get("name_cleanup_flags", [])
        self.video_file_extensions = self._data.get("video_file_extensions", [])

        # Load year range from settings
        self.year_min = self._data.get("year_min", 1900)
        self.year_max = self._data.get("year_max", 3000)

        # Parse libraries
        libraries = self._data.get("libraries", {})
        self.shows = {lib["name"]: lib["path"] for lib in libraries.get("shows", [])}
        self.movies = {lib["name"]: lib["path"] for lib in libraries.get("movies", [])}
        self.music = {lib["name"]: lib["path"] for lib in libraries.get("music", [])}

    def _load_settings(self) -> dict:
        """Load and parse the JSON settings file."""
        try:
            log.debug(f"Loading settings from {self.settings_path}")
            with open(self.settings_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            log.warning(f"Unable to load valid settings from '{self.settings_path}'. {e}")
            return {}
