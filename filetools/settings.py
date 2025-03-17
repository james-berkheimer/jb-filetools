import json
import logging
from pathlib import Path

log = logging.getLogger("filetools")


class AppConfig:
    """Load and manage application settings from a JSON configuration file.

    Provides structured access to configuration settings including:
    - File patterns for deletion/exclusion
    - Video file extensions
    - Year range validation
    - Media library paths

    Args:
        settings_path: Path to the JSON settings file

    Attributes:
        settings_path: Path to the configuration file
        do_not_delete: List of file patterns to never delete
        files_to_delete: List of file patterns to delete
        file_excludes: List of file patterns to exclude from processing
        file_ignores: List of file patterns to ignore during processing
        name_cleanup_flags: List of words to remove from filenames
        video_file_extensions: List of valid video file extensions
        year_min: Minimum valid year for media (default: 1900)
        year_max: Maximum valid year for media (default: 3000)
        shows: Dict mapping show library names to paths
        movies: Dict mapping movie library names to paths
        music: Dict mapping music library names to paths

    Example JSON structure:
        {
            "do_not_delete": ["*.nfo", "*.srt"],
            "files_to_delete": ["*.txt", "*.nfo"],
            "libraries": {
                "shows": [
                    {"name": "main", "path": "/media/shows"}
                ]
            }
        }
    """

    def __init__(self, settings_path: Path):
        """Initialize AppConfig with settings from JSON file.

        Args:
            settings_path: Path to the JSON settings file
        """
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
        """Load and parse the JSON settings file.

        Returns:
            dict: Parsed settings data or empty dict if loading fails

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
