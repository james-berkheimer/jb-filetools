from pathlib import Path

import pytest

from filetools.naming_files import (
    _format_movie_name,
    _format_tv_show_name,
    _get_year,
    _is_properly_formatted,
    _sanitize_season_episode,
    _sanitize_show_name,
    _should_delete,
)


# Test cases for _format_tv_show_name
@pytest.mark.parametrize(
    "show_name,season_episode,flags,ext,expected",
    [
        ("show_name", "s01e01", "", ".mkv", "show_name_s01e01.mkv"),
        ("show_name", "s01e01", "_[4k_hdr]", ".mkv", "show_name_s01e01_[4k_hdr].mkv"),
        ("multiple_words", "s02e10", "", ".mp4", "multiple_words_s02e10.mp4"),
    ],
)
def test_format_tv_show_name(show_name, season_episode, flags, ext, expected):
    result = _format_tv_show_name(show_name, season_episode, flags, ext)
    assert result == expected


# Test cases for _get_year
@pytest.mark.parametrize(
    "input_string,expected",
    [
        ("movie.name.2023.mkv", "2023"),
        ("old.movie.1950.mkv", "1950"),
        ("no.year.here.mkv", None),
        ("invalid.year.9999.mkv", None),
        ("multiple.years.2020.2023.mkv", "2023"),  # Should pick latest year
    ],
)
def test_get_year(input_string, expected):
    result = _get_year(input_string)
    assert result == expected


# Test cases for _is_properly_formatted
@pytest.mark.parametrize(
    "filename,expected",
    [
        ("show_name_s01e01.mkv", True),
        ("movie_name_(2023).mkv", True),
        ("bad format.mkv", False),
        ("show.name.s01e01.mkv", False),
        ("show_name_s01e01_[4k_hdr].mkv", True),
    ],
)
def test_is_properly_formatted(filename, expected):
    result = _is_properly_formatted(filename)
    assert result == expected


# Test cases for _sanitize_show_name
@pytest.mark.parametrize(
    "input_name,expected",
    [
        ("Show Name", "show_name"),
        ("Show.Name", "show_name"),
        ("Show-Name", "show_name"),
        ("Show__Name", "show_name"),
        ("Show Name!", "show_name"),
        ("The.Show.Name", "the_show_name"),  # Changed to preserve "the"
    ],
)
def test_sanitize_show_name(input_name, expected):
    result = _sanitize_show_name(input_name)
    assert result == expected


# Test cases for _sanitize_season_episode
@pytest.mark.parametrize(
    "input_se,expected",
    [
        ("S01E01", "s01e01"),
        ("s.01.e.01", "s01e01"),
        ("s_01_e_01", "s01e01"),
        ("S01.E01", "s01e01"),
    ],
)
def test_sanitize_season_episode(input_se, expected):
    result = _sanitize_season_episode(input_se)
    assert result == expected


# Test cases for _should_delete
@pytest.mark.parametrize(
    "filename,expected",
    [
        ("Sample.mkv", True),  # Exact match
        ("Trailer.mkv", True),  # Exact match
        ("RARBG.txt", True),  # Exact match
        ("movie.mkv", False),  # Should not match
        ("some_trailer.mkv", False),  # Should not match partial
    ],
)
def test_should_delete(filename, expected):
    result = _should_delete(filename)
    assert result == expected
