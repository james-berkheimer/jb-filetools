import pytest

from filetools.naming_files import (
    _detect_flags,
    _is_properly_formatted,
    _sanitize_show_name,
    _target_name,
    rename_files,
)

REAL_NAMES = [
    ("Ludwig 2024 S02E04 1080p iP WEB-DL AAC2 0 H 264-RAWR[EZTVx.to].mkv", "ludwig_2024_s02e04.mkv"),
    ("the.paper.2025.s02e01.1080p.web.h264-cakes[EZTVx.to].mkv", "the_paper_2025_s02e01.mkv"),
    (
        "Shogun.2024.S01E10.A.Dream.of.a.Dream.2160p.DSNP.WEB-DL.DDP5.1.DV.HDR.H.265-NTb.mkv",
        "shogun_2024_s01e10_[4k_hdr].mkv",
    ),
    ("the.venture.bros.s00e201.deep.inside.astrobase.go.mkv", "the_venture_bros_s00e201.mkv"),
    ("Ch4.Grand.Designs.S24E03.1080p.HDTV.H264-DARKFLiX[eztv.re].mkv", "grand_designs_s24e03.mkv"),
    (
        "Colin from Accounts S03E08 Rum n Raisin 1080p FXTL WEB-DL DDP5 1 H 264-NTb[EZTVx.to].mkv",
        "colin_from_accounts_s03e08.mkv",
    ),
    (
        "It's Always Sunny in Philadelphia S18E05 1080p AI BluRay 60FPS H265 DTS5.mkv",
        "its_always_sunny_in_philadelphia_s18e05.mkv",
    ),
    ("Alien.Romulus.2024.1080p.WEBRip.x264.AAC5.1-[YTS.MX].mp4", "alien_romulus_(2024).mp4"),
    ("www.Tamilblasters.foo - Dune Part Two (2024) [1080p HQ HDRip].mkv", "dune_part_two_(2024).mkv"),
    ("This.Is.England.(2006).1080p.mkv", "this_is_england_(2006).mkv"),
    ("Oppenheimer.2023.2160p.UHD.BluRay.HDR10.x265.mkv", "oppenheimer_(2023)-4K-hdr.mkv"),
    ("Spider-Man.No.Way.Home.2021.1080p.mkv", "spider-man_no_way_home_(2021).mkv"),
    ("1984.1984.1080p.BluRay.mkv", "1984_(1984).mkv"),
    ("The.Party.1968.1080p.mkv", "the_party_(1968).mkv"),
]


@pytest.mark.parametrize(("original", "expected"), REAL_NAMES)
def test_target_name(original, expected):
    assert _target_name(original) == expected


@pytest.mark.parametrize("renamed", [expected for _, expected in REAL_NAMES])
def test_renamed_files_are_left_alone(renamed):
    # Regression: re-running on "movie_(2006).mkv" used to produce "movie_((2006).mkv".
    assert _is_properly_formatted(renamed)
    assert _target_name(renamed) == renamed


@pytest.mark.parametrize(
    "file_name",
    [
        "1923_(2022)_s01e06.mkv",
        "show_name_s01e01_[4k_hdr].mkv",
        "show_name_s03e23-e24.mkv",
        "metalstorm_the_destruction_of_jared-syn_(1983).mkv",
    ],
)
def test_properly_formatted(file_name):
    assert _is_properly_formatted(file_name)


@pytest.mark.parametrize(
    "file_name",
    [
        "pbs_show_name_s01e01.mkv",
        "bbc.show.name.s01e01.mkv",
        "show.name.s01e01.mkv",
        "show_name_101.mkv",
        "this_is_england_((2006).mkv",
    ],
)
def test_not_properly_formatted(file_name):
    assert not _is_properly_formatted(file_name)


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Movie.2024.2160p.HDR10.mkv", (True, True)),
        ("Movie.2024.1080p.DV.mkv", (False, True)),
        ("Movie (2024) [1080p HQ HDRip]", (False, False)),
        ("movie_(2023)-4K-hdr", (True, True)),
    ],
)
def test_detect_flags(name, expected):
    assert _detect_flags(name) == expected


def test_cleanup_flags_only_remove_whole_words():
    assert _sanitize_show_name("bbc.horizon") == "horizon"
    assert _sanitize_show_name("hitv.show") == "hitv_show"


def test_rename_files_debug_changes_nothing(tmp_path):
    names = ["RARBG.txt", "Ludwig 2024 S02E04 1080p iP WEB-DL AAC2 0 H 264-RAWR[EZTVx.to].mkv"]
    for name in names:
        (tmp_path / name).touch()

    rename_files(tmp_path, debug=True)

    assert sorted(p.name for p in tmp_path.iterdir()) == sorted(names)


def test_rename_files(tmp_path):
    (tmp_path / "RARBG.txt").touch()
    (tmp_path / "Ludwig 2024 S02E04 1080p iP WEB-DL AAC2 0 H 264-RAWR[EZTVx.to].mkv").touch()

    rename_files(tmp_path)

    assert [p.name for p in tmp_path.iterdir()] == ["ludwig_2024_s02e04.mkv"]


MKV_HEADER = b"\x1a\x45\xdf\xa3" + b"\x00" * 60


def test_extensionless_video_is_named_from_its_contents(tmp_path):
    (tmp_path / "Lanterns S01E06 1080p WEB-DL DDP5 1 x265 NTb").write_bytes(MKV_HEADER)

    rename_files(tmp_path)

    assert [p.name for p in tmp_path.iterdir()] == ["lanterns_s01e06.mkv"]


def test_non_video_without_extension_is_left_alone(tmp_path):
    (tmp_path / "readme").write_text("nothing to see")
    rename_files(tmp_path)
    assert [p.name for p in tmp_path.iterdir()] == ["readme"]
