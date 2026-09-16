import os

import pytest

from filetools.utils import (
    detect_video_extension,
    is_executable,
    match_for_tv,
    parse_filename,
    sort_media,
)


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        # Real torrent names from Transmission
        ("Ludwig 2024 S02E04 1080p iP WEB-DL AAC2 0 H 264-RAWR[EZTVx.to]", ("Ludwig 2024", "s02e04")),
        ("the.paper.2025.s02e01.1080p.web.h264-cakes[EZTVx.to]", ("the.paper.2025", "s02e01")),
        ("Futurama.S11E07.1080p.DSNP.WEB-DL.DDP5.1.H.264-TRB", ("Futurama", "s11e07")),
        (
            "Star Trek Strange New Worlds S04E08 1080p HEVC x265-MeGusta",
            ("Star Trek Strange New Worlds", "s04e08"),
        ),
        # Three-digit episodes (specials)
        ("the_venture_bros_s00e201_deep_inside_astrobase_go!", ("the_venture_bros", "s00e201")),
        ("survivorman_s00e024", ("survivorman", "s00e24")),
        # Multi-episode files keep their episode range
        ("Show.S03E23-E24.720p", ("Show", "s03e23-e24")),
        ("Show.S03E23E24", ("Show", "s03e23-e24")),
        ("Show.S01E01-02.1080p", ("Show", "s01e01-e02")),
        ("Show.S01E01-1080p", ("Show", "s01e01")),
        # Other season/episode styles
        ("Show.S1E05", ("Show", "s01e05")),
        ("Only.Murders.4x02", ("Only.Murders", "s04e02")),
        ("Show Season 02 Episode 03", ("Show", "s02e03")),
        ("frontline - S2018E18", ("frontline", "s2018e18")),
        # "Part N of M" is only used when there is no standard marker
        ("Show.S01E05.Part.1.of.2", ("Show", "s01e05")),
        ("BBC.Horizon.2019.The.Planets.Part.1.of.5.720p", ("BBC.Horizon.2019.The.Planets", "s01e01")),
        ("Show Name Series 2 3 of 6", ("Show Name", "s01e03")),
    ],
)
def test_parse_filename(filename, expected):
    assert parse_filename(filename) == expected


@pytest.mark.parametrize(
    "filename",
    [
        "Alien.Romulus.2024.1920x1080.x264",
        "Movie.2024.1080p.x265-GROUP",
        "The.Party.1968.1080p",
        "Blade.Runner.2049.2017.2160p.UHD",
    ],
)
def test_movies_are_not_mistaken_for_episodes(filename):
    assert parse_filename(filename) == (None, None)
    assert match_for_tv(filename) == (False, None)


def test_sort_media_splits_movies_and_shows_without_deleting(tmp_path):
    for name in [
        "ludwig_2024_s02e04.mkv",
        "alien_romulus_(2024).mp4",
        "notes.txt",
        "show.sample.mkv",
        "the.party.1968.mkv",
    ]:
        (tmp_path / name).touch()

    with os.scandir(tmp_path) as entries:
        movies, shows = sort_media(sorted(entries, key=lambda e: e.name))

    assert [p.name for p in movies] == ["alien_romulus_(2024).mp4", "the.party.1968.mkv"]
    assert [p.name for p in shows] == ["ludwig_2024_s02e04.mkv"]
    assert sorted(p.name for p in tmp_path.iterdir()) == [
        "alien_romulus_(2024).mp4",
        "ludwig_2024_s02e04.mkv",
        "notes.txt",
        "show.sample.mkv",
        "the.party.1968.mkv",
    ]


MKV_HEADER = b"\x1a\x45\xdf\xa3" + b"\x00" * 60
MP4_HEADER = b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 60
AVI_HEADER = b"RIFF\x00\x00\x00\x00AVI LIST" + b"\x00" * 60
PE_HEADER = b"MZ\x90\x00\x03\x00\x00\x00" + b"\x00" * 60
ELF_HEADER = b"\x7fELF\x02\x01\x01\x00" + b"\x00" * 60


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        (MKV_HEADER, ".mkv"),
        (MP4_HEADER, ".mp4"),
        (b"\x00\x00\x00\x18ftypqt  " + b"\x00" * 60, ".mov"),
        (AVI_HEADER, ".avi"),
        (b"\x00\x00\x01\xba" + b"\x00" * 60, ".mpg"),
        (PE_HEADER, None),
        (b"just some text", None),
        (b"", None),
    ],
)
def test_detect_video_extension(tmp_path, header, expected):
    path = tmp_path / "no_extension"
    path.write_bytes(header)
    assert detect_video_extension(path) == expected


def test_is_executable(tmp_path):
    (tmp_path / "pe").write_bytes(PE_HEADER)
    (tmp_path / "elf").write_bytes(ELF_HEADER)
    (tmp_path / "video").write_bytes(MKV_HEADER)
    assert is_executable(tmp_path / "pe")
    assert is_executable(tmp_path / "elf")
    assert not is_executable(tmp_path / "video")
    assert not is_executable(tmp_path / "missing")
