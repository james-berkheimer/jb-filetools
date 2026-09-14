from pathlib import Path

import pytest

from filetools.show_matching import ShowCatalog, normalize_show_name

TV = Path("/library/television")
SHOWS = {
    "ludwig": TV / "bbc/ludwig",
    "the_paper_2025": TV / "nbc/the_paper_2025",
    "1923_(2022)": TV / "paramount+/1923_(2022)",
    "beavis_and_butt-head": TV / "mtv/beavis_and_butt-head",
    "shogun_1980": TV / "nbc/shogun_1980",
    "shogun_2024": TV / "fx/shogun_2024",
    "mammals": TV / "bbc/mammals",
    "mammals_2024": TV / "bbc/mammals_2024",
    "the_venture_brothers": TV / "adult_swim/the_venture_brothers",
}


@pytest.fixture
def catalog():
    return ShowCatalog(SHOWS)


@pytest.mark.parametrize(
    ("show_name", "expected"),
    [
        ("ludwig", "ludwig"),
        ("ludwig_2024", "ludwig"),  # year on the file, not on the folder
        ("the_paper", "the_paper_2025"),  # year on the folder, not on the file
        ("1923", "1923_(2022)"),
        ("1923_2022", "1923_(2022)"),
        ("Beavis and Butt Head", "beavis_and_butt-head"),
        ("shogun_2024", "shogun_2024"),
        ("mammals", "mammals"),
    ],
)
def test_unambiguous_matches(catalog, show_name, expected):
    match = catalog.match(show_name)
    assert match.path == SHOWS[expected]
    assert match.candidates == []


@pytest.mark.parametrize(
    ("show_name", "candidates"),
    [
        ("shogun", ["shogun_1980", "shogun_2024"]),
        ("shogun_2031", ["shogun_1980", "shogun_2024"]),
        ("mammals_2025", ["mammals", "mammals_2024"]),
        ("the_venture_bros", ["the_venture_brothers"]),
    ],
)
def test_ambiguous_or_close_names_are_only_suggested(catalog, show_name, candidates):
    match = catalog.match(show_name)
    assert match.path is None
    assert match.candidates == [SHOWS[c] for c in candidates]


def test_different_year_is_not_matched_automatically():
    match = ShowCatalog({"ghosts_2019": TV / "bbc/ghosts_2019"}).match("ghosts_2021")
    assert match.path is None
    assert match.candidates == [TV / "bbc/ghosts_2019"]


def test_unknown_show(catalog):
    match = catalog.match("grand_designs")
    assert match.path is None
    assert match.candidates == []


def test_added_shows_are_matched(catalog):
    catalog.add("grand_designs", TV / "channel_4/grand_designs")
    assert catalog.match("grand_designs").path == TV / "channel_4/grand_designs"


def test_normalize_show_name():
    assert normalize_show_name("It's Always Sunny!") == "it_s_always_sunny"
    assert normalize_show_name("1923_(2022)") == "1923_2022"
