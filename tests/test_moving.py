import errno
import inspect
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

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


def test_get_files_to_extract(temp_media_dir, mock_config):
    """Test extracting files from working directory."""
    # Create test directory structure
    source_dir = temp_media_dir / "source"
    test_dir = source_dir / "test_dir"
    test_dir.mkdir(parents=True)

    # Create test files in subdirectory
    test_files = [
        "show.s01e01.mkv",
        "movie.2023.mkv",
        "ignore.txt",
        "Sample.mkv",
        "test.part",
    ]

    for filename in test_files:
        file_path = test_dir / filename
        file_path.touch()
        assert file_path.exists(), f"Failed to create {file_path}"
        print(f"Created test file: {file_path}")

    # Mock _process_file
    with patch("filetools.moving_files._process_file") as mock_process:
        processed_files = set()

        def side_effect(file_obj, working_dir):
            print(f"\nProcess file called with: {file_obj.name}")
            processed_files.add(file_obj.name)

            # Return (dest_path, is_downloading)
            if file_obj.name.endswith(".part"):
                print("  Returning do_not_delete file")
                return None, True  # This will stop processing the directory
            if file_obj.name.endswith(".mkv") and file_obj.name not in ["Sample.mkv", "Trailer.mkv"]:
                dest = working_dir / file_obj.name
                print(f"  Returning valid file: ({file_obj.path}, {dest})")
                return Path(file_obj.path), dest
            print("  Returning ignored file")
            return None, False

        mock_process.side_effect = side_effect

        print("\nDirectory structure:")
        print(f"Root dir: {source_dir}")
        for path in source_dir.rglob("*"):
            print(f"  {path.relative_to(source_dir)}")

        result = _get_files_to_extract(source_dir)

        print("\nProcessing Summary:")
        print(f"Files processed: {sorted(processed_files)}")
        print(f"Files missed: {sorted(set(test_files) - processed_files)}")
        print(f"\nResult dictionary: {result}")

    # Expect empty result because test.part indicates downloading
    assert result == {}, "Should return empty dict when .part file is present"

    # Create a new directory without .part files for positive test
    test_dir2 = source_dir / "test_dir2"
    test_dir2.mkdir()
    valid_files = ["show.s01e01.mkv", "movie.2023.mkv"]

    for filename in valid_files:
        file_path = test_dir2 / filename
        file_path.touch()

    # Test again with only valid files
    with patch("filetools.moving_files._process_file") as mock_process:

        def side_effect(file_obj, working_dir):
            if file_obj.name.endswith(".mkv"):
                source_path = str(test_dir2 / file_obj.name)  # Convert to string
                dest_path = str(source_dir / file_obj.name)  # Convert to string
                return source_path, dest_path
            return None, False

        mock_process.side_effect = side_effect
        result = _get_files_to_extract(source_dir)

        # Convert expected paths to strings to match actual result
        expected = {str(test_dir2 / f): str(source_dir / f) for f in valid_files}

        print("\nSecond test:")
        print(f"Result: {result}")
        print(f"Expected: {expected}")

        assert result == expected, "Should extract valid files when no .part files present"
