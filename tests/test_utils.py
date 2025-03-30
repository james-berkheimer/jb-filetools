import os
import re
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from filetools.utils import (
    _fix_season_episode,
    _should_delete,
    _should_exclude,
    dir_scan,
    match_for_altseason,
    match_for_tv,
    normalize_tv_format,
    parse_filename,
    sort_media,
)


@pytest.fixture
def temp_dir_structure(tmp_path):
    """Create a temporary directory structure for testing."""
    # Create test directories
    dir1 = tmp_path / "dir1"
    dir2 = tmp_path / "dir2"
    dir1.mkdir()
    dir2.mkdir()

    # Create test files
    (dir1 / "file1.txt").touch()
    (dir1 / "file2.mp4").touch()
    return tmp_path


@pytest.fixture
def mock_dir_entry():
    """Create a mock DirEntry object."""

    def _create_entry(name, is_file=True, is_dir=False):
        entry = Mock()
        entry.name = name
        entry.path = f"/fake/path/{name}"
        entry.is_file = Mock(return_value=is_file)
        entry.is_dir = Mock(return_value=is_dir)
        return entry

    return _create_entry


class TestDirScan:
    def test_scan_nonexistent_directory(self):
        result = dir_scan("/nonexistent/path")
        assert result == []

    def test_scan_file_instead_of_directory(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.touch()
        result = dir_scan(test_file)
        assert result == []

    def test_scan_directories(self, temp_dir_structure):
        result = dir_scan(temp_dir_structure, get_files=False)
        assert len(result) == 2
        assert all(entry.is_dir() for entry in result)

    def test_scan_files(self, temp_dir_structure):
        result = dir_scan(temp_dir_structure / "dir1", get_files=True)
        assert len(result) == 2
        assert all(entry.is_file() for entry in result)


class TestParseFilename:
    @pytest.mark.parametrize(
        "filename,expected",
        [
            ("Show.Name.S01E02.mp4", ("Show.Name", "s01e02")),
            ("Show.Name.1x02.mp4", ("Show.Name", "s01e02")),
            ("Show Name 1 of 10.mp4", ("Show Name", "s01e01")),
            ("Invalid.File.mp4", (None, None)),
        ],
    )
    def test_parse_filename(self, filename, expected):
        assert parse_filename(filename) == expected


class TestMatchForTV:
    @pytest.mark.parametrize(
        "filename,expected_match",
        [
            ("Show.S01E02.mp4", True),
            ("Show.1x02.mp4", True),
            ("Show.S2023E01.mp4", True),
            ("Show season 01 episode 02.mp4", True),
            ("Show.season01episode02.mp4", True),
            ("Show.NoMatch.mp4", False),
        ],
    )
    def test_match_for_tv(self, filename, expected_match):
        match, _ = match_for_tv(filename)
        assert match == expected_match


class TestMatchForAltseason:
    @pytest.mark.parametrize(
        "filename,expected_match",
        [
            ("Episode 1 of 10.mp4", True),
            ("Show 2 of 8.mp4", True),
            ("Regular.Show.S01E02.mp4", False),
        ],
    )
    def test_match_for_altseason(self, filename, expected_match):
        match = match_for_altseason(filename)
        assert bool(match) == expected_match


class TestNormalizeTVFormat:
    @pytest.mark.parametrize(
        "input_format,expected",
        [
            ("S01E02", "s01e02"),
            ("1x02", "s01e02"),
            ("season 1 episode 2", "s01e02"),
            ("season01episode02", "s01e02"),
            ("S2023E01", "s2023e01"),
        ],
    )
    def test_normalize_tv_format(self, input_format, expected):
        assert normalize_tv_format(input_format) == expected


class TestSortMedia:
    @pytest.fixture
    def mock_config(self):
        return {
            "files_to_delete": ["sample", "trailer"],
            "file_extension_excludes": [".nfo", ".txt"],
            "video_file_extensions": [".mp4", ".mkv"],
        }

    def test_sort_media(self, mock_dir_entry, mock_config):
        with patch("filetools.utils.CONFIG") as mock_cfg:
            mock_cfg.files_to_delete = mock_config["files_to_delete"]
            mock_cfg.file_extension_excludes = mock_config["file_extension_excludes"]
            mock_cfg.video_file_extensions = mock_config["video_file_extensions"]

            files = [
                mock_dir_entry("movie.mp4"),
                mock_dir_entry("show.s01e01.mp4"),
                mock_dir_entry("sample.mp4"),
                mock_dir_entry("video.txt"),
            ]

            movies, shows = sort_media(files)
            assert len(movies) == 1
            assert len(shows) == 1
            assert str(movies[0]).endswith("movie.mp4")
            assert str(shows[0]).endswith("show.s01e01.mp4")


class TestHelperFunctions:
    def test_fix_season_episode(self):
        assert _fix_season_episode("1 of 10") == "s01e01"
        assert _fix_season_episode("2 of 8") == "s01e02"

    @pytest.mark.parametrize(
        "filename,patterns,expected",
        [
            ("sample.mp4", {"sample"}, True),
            ("trailer.mp4", {"sample", "trailer"}, True),
            ("show.mp4", {"sample"}, False),
        ],
    )
    def test_should_delete(self, filename, patterns, expected):
        assert _should_delete(filename, patterns) == expected

    @pytest.mark.parametrize(
        "filename,patterns,expected",
        [
            ("file.nfo", {".nfo"}, True),
            ("file.txt", {".nfo", ".txt"}, True),
            ("file.mp4", {".nfo"}, False),
        ],
    )
    def test_should_exclude(self, filename, patterns, expected):
        assert _should_exclude(filename, patterns) == expected
