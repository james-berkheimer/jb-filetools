import errno
import os
from pathlib import Path

import pytest

from filetools import moving_files
from filetools.moving_files import _episode_filename, _move_file, _season_dir_name, move_show_files


@pytest.mark.parametrize(
    ("existing", "season", "expected"),
    [
        ([], 2, "season_02"),
        (["season 01"], 1, "season 01"),  # legacy spaced folder is reused
        (["Season_1"], 1, "Season_1"),
        (["season 01", "season_01"], 1, "season_01"),  # canonical wins when both exist
        (["season 01"], 2, "season_02"),
        (["Specials"], 0, "Specials"),
        ([], 0, "specials"),
    ],
)
def test_season_dir_name(tmp_path, existing, season, expected):
    for name in existing:
        (tmp_path / name).mkdir()
    assert _season_dir_name(tmp_path, season) == expected


def test_season_dir_name_for_new_show(tmp_path):
    assert _season_dir_name(tmp_path / "missing", 3) == "season_03"


def test_move_file_across_filesystems_copies_everything(tmp_path, monkeypatch):
    src, dest = tmp_path / "src.mkv", tmp_path / "dest.mkv"
    payload = os.urandom(3 * 1024 * 1024)
    src.write_bytes(payload)

    def cross_device(*_args):
        raise OSError(errno.EXDEV, "Invalid cross-device link")

    monkeypatch.setattr(moving_files.os, "rename", cross_device)
    _move_file(src, dest)

    assert dest.read_bytes() == payload
    assert not src.exists()


@pytest.fixture
def library(tmp_path, monkeypatch):
    """A working directory plus a one-show library, with prompts answered 'yes'."""
    work = tmp_path / "transmission"
    ludwig = tmp_path / "television/bbc/ludwig"
    (ludwig / "season 02").mkdir(parents=True)
    work.mkdir()
    monkeypatch.setattr(moving_files, "get_show_map", lambda: {"Shows": {"ludwig": str(ludwig)}})
    monkeypatch.setattr(moving_files, "ask_bool", lambda *_args, **_kwargs: True)
    return work, ludwig


def test_show_with_year_moves_into_existing_folder(library):
    # Regression from a real session: "ludwig_2024" must land in the existing "ludwig" folder.
    work, ludwig = library
    shows = [work / f"ludwig_2024_s02e0{n}.mkv" for n in (4, 5, 6)]
    for show in shows:
        show.touch()

    move_show_files(shows, work)

    # The file is renamed to match the folder, as the rest of the season is.
    assert sorted(p.name for p in (ludwig / "season 02").iterdir()) == [
        "ludwig_s02e04.mkv",
        "ludwig_s02e05.mkv",
        "ludwig_s02e06.mkv",
    ]
    assert list(work.iterdir()) == []


def test_debug_move_creates_nothing(library):
    work, ludwig = library
    show = work / "ludwig_s03e01.mkv"
    show.touch()

    move_show_files([show], work, debug=True)

    assert show.exists()
    assert not (ludwig / "season_03").exists()


def test_ambiguous_show_is_asked_once(library, monkeypatch):
    work, _ = library
    monkeypatch.setattr(
        moving_files,
        "get_show_map",
        lambda: {
            "Shows": {
                "shogun_1980": str(work.parent / "nbc/shogun_1980"),
                "shogun_2024": str(work.parent / "fx/shogun_2024"),
            }
        },
    )
    questions = []

    def choose_skip(choices, prompt):
        questions.append((choices, prompt))
        return "Skip"

    monkeypatch.setattr(moving_files, "ask_multichoice", choose_skip)
    shows = [work / "shogun_s01e01.mkv", work / "shogun_s01e02.mkv"]
    for show in shows:
        show.touch()

    move_show_files(shows, work)

    root = work.parent.name
    choices = [f"{root}/nbc/shogun_1980", f"{root}/fx/shogun_2024", "Add 'shogun' as a new show", "Skip"]
    assert questions == [(choices, "Where should 'shogun' go?")]
    assert all(show.exists() for show in shows)


@pytest.mark.parametrize(
    ("filename", "show_name", "folder", "expected"),
    [
        ("lanterns_2026_s01e05.mkv", "lanterns_2026", "lanterns", "lanterns_s01e05.mkv"),
        ("the_paper_s02e01.mkv", "the_paper", "the_paper_2025", "the_paper_2025_s02e01.mkv"),
        ("1923_s01e06.mkv", "1923", "1923_(2022)", "1923_(2022)_s01e06.mkv"),
        (
            "shogun_2024_s01e10_[4k_hdr].mkv",
            "shogun_2024",
            "shogun_2024",
            "shogun_2024_s01e10_[4k_hdr].mkv",
        ),
        ("american_dad_s22e12.mkv", "american_dad", "american_dad", "american_dad_s22e12.mkv"),
    ],
)
def test_episode_filename_matches_show_folder(filename, show_name, folder, expected):
    assert (
        _episode_filename(filename, show_name, Path("/library/television/network") / folder) == expected
    )
