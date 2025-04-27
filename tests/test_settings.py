import json
from pathlib import Path

import pytest

from filetools.settings import AppConfig


@pytest.fixture
def sample_settings(tmp_path):
    """Create a sample settings file for testing."""
    settings_file = tmp_path / "settings.json"
    settings_data = {
        "do_not_delete": [".nfo", ".jpg"],
        "files_to_delete": ["sample", "trailer"],
        "file_excludes": [".txt"],
        "file_name_ignores": ["ignore_me"],
        "name_cleanup_flags": ["clean_this"],
        "valid_file_extensions": [".mp4", ".mkv"],
        "year_min": 1900,
        "year_max": 2025,
        "libraries": {
            "shows": [
                {"name": "shows1", "path": "/path/to/shows1"},
                {"name": "shows2", "path": "/path/to/shows2"},
            ],
            "movies": [{"name": "movies1", "path": "/path/to/movies1"}],
            "music": [{"name": "music1", "path": "/path/to/music1"}],
        },
        "default_source": "/default/path",
    }

    settings_file.write_text(json.dumps(settings_data))
    return settings_file


class TestAppConfig:
    """Test suite for AppConfig settings management."""

    def test_load_valid_settings(self, sample_settings):
        """Test loading valid settings file."""
        config = AppConfig(sample_settings)

        assert config.do_not_delete == [".nfo", ".jpg"]
        assert config.files_to_delete == ["sample", "trailer"]
        assert config.valid_file_extensions == [".mp4", ".mkv"]
        assert config.year_min == 1900
        assert config.year_max == 2025
        assert config.shows == {
            "shows1": Path("/path/to/shows1"),
            "shows2": Path("/path/to/shows2"),
        }

    def test_missing_settings_file(self, tmp_path):
        """Test handling of missing settings file."""
        nonexistent_file = tmp_path / "nonexistent.json"
        config = AppConfig(nonexistent_file)

        # Should use default values when file is missing
        assert config.do_not_delete == []
        assert config.files_to_delete == []
        assert config.year_min == 1900
        assert config.year_max == 3000

    def test_invalid_json(self, tmp_path):
        """Test handling of invalid JSON in settings file."""
        invalid_json = tmp_path / "invalid.json"
        invalid_json.write_text("{invalid json")

        config = AppConfig(invalid_json)
        assert config._data == {}  # Should return empty dict for invalid JSON

    def test_missing_optional_settings(self, tmp_path):
        """Test handling of missing optional settings."""
        minimal_settings = tmp_path / "minimal.json"
        minimal_settings.write_text("{}")

        config = AppConfig(minimal_settings)
        assert config.do_not_delete == []
        assert config.files_to_delete == []
        assert config.shows == {}
        assert config.movies == {}
        assert config.music == {}
