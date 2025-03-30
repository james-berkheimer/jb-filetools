import errno
import inspect
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from filetools import moving_files
from filetools.moving_files import (
    _build_movie_destination,
    _build_show_destination,
    _choose_library,
    _get_files_to_extract,
    _move_file,
    _perform_moves,
    _process_file,
    _should_skip_directory,
    _split_season_episode,
)

# Add this before the test
print("\nFunction implementation:")
print(inspect.getsource(_get_files_to_extract))


@pytest.fixture
def temp_media_dir(tmp_path):
    """Create a temporary directory structure for testing."""
    # Only create the base directory
    src = tmp_path / "source"
    src.mkdir()
    return tmp_path


@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary test file."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    return test_file


@pytest.fixture
def mock_config(tmp_path):  # Add tmp_path parameter here
    """Mock configuration values for testing."""
    with patch("filetools.moving_files.CONFIG") as mock_cfg:
        # File filtering settings
        mock_cfg.video_file_extensions = [".mkv"]
        mock_cfg.do_not_delete = [".part"]
        mock_cfg.files_to_delete = ["Sample.mkv", "Trailer.mkv"]
        mock_cfg.file_extension_excludes = [".part", "Sample.mkv"]
        mock_cfg.file_name_ignores = ["sample", "trailer"]

        # Library paths
        mock_cfg.libraries = {
            "shows": [{"name": "Shows", "path": str(tmp_path / "shows")}],
            "movies": [{"name": "Movies", "path": str(tmp_path / "movies")}],
        }

        # Other settings
        mock_cfg.name_cleanup_flags = []
        mock_cfg.year_min = 1900
        mock_cfg.year_max = 2030
        yield mock_cfg


def test_should_skip_directory():
    mock_dir = MagicMock()
    mock_dir.name = "_in-progress"
    assert _should_skip_directory(mock_dir) is True

    mock_dir.name = "normal_dir"
    assert _should_skip_directory(mock_dir) is False


def test_split_season_episode():
    assert _split_season_episode("s01e01") == ("s01", "e01")
    assert _split_season_episode("s02e10") == ("s02", "e10")
    assert _split_season_episode("_s03e05_") == ("s03", "e05")


def test_move_file_same_filesystem(temp_file, tmp_path):
    """Test moving file within same filesystem using os.rename()."""
    dest = tmp_path / "dest.txt"
    _move_file(temp_file, dest)

    assert not temp_file.exists()
    assert dest.exists()
    assert dest.read_text() == "test content"


def test_move_file_across_filesystems(temp_file, tmp_path, monkeypatch):
    """Test fallback to sendfile when os.rename fails with EXDEV."""
    dest = tmp_path / "dest.txt"

    def mock_rename(*args):
        raise OSError(errno.EXDEV, "Invalid cross-device link")

    monkeypatch.setattr(os, "rename", mock_rename)
    _move_file(temp_file, dest)

    assert not temp_file.exists()
    assert dest.exists()
    assert dest.read_text() == "test content"


def test_move_file_all_methods_fail(temp_file, tmp_path, monkeypatch):
    """Test error handling when all move methods fail."""
    dest = tmp_path / "nonexistent" / "dest.txt"

    with pytest.raises(OSError):
        _move_file(temp_file, dest)


def test_get_files_to_extract_skips_if_part_present(temp_media_dir, mock_config):
    """Test that extraction is skipped when a .part file is present."""
    source_dir = temp_media_dir / "source"
    test_dir = source_dir / "test_dir"
    test_dir.mkdir(parents=True)

    # Create .part file
    (test_dir / "test.part").touch()
    (test_dir / "movie.2023.mkv").touch()

    with patch("filetools.moving_files._process_file") as mock_process:

        def side_effect(file_obj, working_dir):
            if file_obj.name.endswith(".part"):
                return None, True
            return Path(file_obj.path), working_dir / file_obj.name

        mock_process.side_effect = side_effect
        result = _get_files_to_extract(source_dir)

    assert result == {}, "Should skip extracting when .part file is present"


def test_get_files_to_extract_only_valid_files(temp_media_dir, mock_config):
    source_dir = temp_media_dir / "source"
    test_dir = source_dir / "test_dir"
    test_dir.mkdir(parents=True)

    valid_files = ["show.s01e01.mkv", "movie.2023.mkv", "ignore.txt", "Sample.mkv"]
    for filename in valid_files:
        (test_dir / filename).touch()

    with patch("filetools.moving_files._process_file") as mock_process:

        def process_side_effect(file_obj, working_dir):
            name = file_obj.name
            if name.endswith(".mkv") and "sample" not in name.lower():
                return file_obj.path, False
            return None, False

        mock_process.side_effect = process_side_effect
        result = _get_files_to_extract(source_dir)

    expected = {
        str(test_dir / "show.s01e01.mkv"): str(test_dir / "show.s01e01.mkv"),
        str(test_dir / "movie.2023.mkv"): str(test_dir / "movie.2023.mkv"),
    }

    assert result == expected, "Should extract only valid video files"


@patch("filetools.moving_files.ask_multichoice")
def test_choose_library_provides_expected_choices(mock_ask):
    libraries = {"LibraryOne": "/path/one", "LibraryTwo": "/path/two"}
    mock_ask.return_value = "LibraryOne"

    result = _choose_library(libraries, "Pick one:")

    assert result == Path("/path/one")
    mock_ask.assert_called_once_with(["LibraryOne", "LibraryTwo"], "Pick one:")
