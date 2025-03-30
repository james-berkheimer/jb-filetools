import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_media_dir():
    """Create a temporary directory for test media files."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
def sample_video_files(temp_media_dir):
    """Create sample video files for testing."""
    files = [
        "Show.Name.S01E01.mkv",
        "Movie.Name.2023.mkv",
        "Sample.Video.mkv",
        "Show.Name.S01E02.HDR.2160p.mkv",
    ]
    for file in files:
        (temp_media_dir / file).touch()
    return temp_media_dir
