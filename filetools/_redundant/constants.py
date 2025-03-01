#!/usr/bin/env python
#
# modules/const.py
#
# This file will store globally used variables that don't change.
#

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------
import json
import os
from pathlib import Path


# --------------------------------------------------------------------------------
# Utilities
# --------------------------------------------------------------------------------
class AppConfig:
    def __init__(self, settings_path: Path):
        """
        Initialize the configuration object by loading a JSON file
        from the given path.
        """
        data = self._load_settings(settings_path)

        # Parse file-related lists
        self.files_to_delete = data.get("files_to_delete", [])
        self.do_not_delete = data.get("do_not_delete", [])
        self.video_file_extensions = data.get("video_file_extensions", [])
        self.file_excludes = data.get("file_excludes", [])

        # Parse libraries
        libraries = data.get("libraries", {})
        self.shows = {lib["name"]: lib["path"] for lib in libraries.get("shows", [])}
        self.movies = {lib["name"]: lib["path"] for lib in libraries.get("movies", [])}
        self.music = {lib["name"]: lib["path"] for lib in libraries.get("music", [])}

        # Any other top-level settings
        self.default_source = data.get("default_source", "")

    def _load_settings(self, settings_path: Path) -> dict:
        """
        Load and parse the JSON settings file.
        Returns an empty dict if the file isn't found or is invalid.
        """
        try:
            print(f"Loading settings from {settings_path}")
            with open(settings_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Unable to load valid settings from '{settings_path}'. {e}")
            return {}

    # ----------------------------------------------------------------------
    # Shows
    # ----------------------------------------------------------------------
    @property
    def show_names(self) -> list[str]:
        """Returns a list of show library names (attribute-style)."""
        return list(self.shows.keys())

    @property
    def show_paths(self) -> list[str]:
        """Returns a list of show library paths (attribute-style)."""
        return list(self.shows.values())

    def get_show_path(self, name: str) -> str | None:
        """Returns the path for the given show library name."""
        return self.shows.get(name)

    # ----------------------------------------------------------------------
    # Movies
    # ----------------------------------------------------------------------
    @property
    def movie_names(self) -> list[str]:
        """Returns a list of movie library names (attribute-style)."""
        return list(self.movies.keys())

    @property
    def movie_paths(self) -> list[str]:
        """Returns a list of movie library paths (attribute-style)."""
        return list(self.movies.values())

    def get_movie_path(self, name: str) -> str | None:
        """Returns the path for the given movie library name."""
        return self.movies.get(name)

    # ----------------------------------------------------------------------
    # Music
    # ----------------------------------------------------------------------
    @property
    def music_names(self) -> list[str]:
        """Returns a list of music library names (attribute-style)."""
        return list(self.music.keys())

    @property
    def music_paths(self) -> list[str]:
        """Returns a list of music library paths (attribute-style)."""
        return list(self.music.values())

    def get_music_path(self, name: str) -> str | None:
        """Returns the path for the given music library name."""
        return self.music.get(name)


# --------------------------------------------------------------------------------
# Initialization
# --------------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Load settings from JSON file
try:
    print(f"Loading {PROJECT_ROOT}/settings.json")
    with open(PROJECT_ROOT / "settings.json", "r") as f:
        settings = json.load(f)
except FileNotFoundError:
    settings = {}

# Settings consts
CURRENT_WORKING_DIR = Path.cwd()

# Settings environment variables with fallback to settings file
FILES_TO_DELETE = os.getenv("FT_FILES_TO_DELETE", ",".join(settings.get("files_to_delete", []))).split(
    ","
)
DO_NOT_DELETE = os.getenv("FT_DO_NOT_DELETE", ",".join(settings.get("do_not_delete", [".part"]))).split(
    ","
)
VIDEO_FILE_EXTENSIONS = os.getenv(
    "FT_VIDEO_FILE_EXTENSIONS", ",".join(settings.get("video_file_extensions", []))
).split(",")
FILE_EXCLUDES = os.getenv("FT_FILE_EXCLUDES", ",".join(settings.get("file_excludes", []))).split(",")
FILE_IGNORES = ["sample", "trailer"]

# SHOW_LIBRARIES = {
#     library["name"]: library["path"] for library in settings.get("libraries", {}).get("shows", [])
# }
# MOVIE_LIBRARIES = {
#     library["name"]: library["path"] for library in settings.get("libraries", {}).get("movies", [])
# }
# MUSIC_LIBRARIES = {
#     library["name"]: library["path"] for library in settings.get("libraries", {}).get("music", [])
# }


# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------
CURRENT_WORKING_DIR = Path.cwd()
LIBRARIES = MediaLibraries(PROJECT_ROOT / "settings.json")
