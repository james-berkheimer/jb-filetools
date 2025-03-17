import errno
import logging
import os
import re
import shutil

from filetools.logger import setup_logger
from filetools.questions import ask_bool
from filetools.utils import dir_scan, make_shows_map

log = setup_logger(name="filetools", level=logging.INFO)


def test1() -> None:
    tv = "/media/Television"
    # print(dir_scan(path, get_files=True))
    # print(dir_scan(transmission))
    # print(dir_scan(docs))
    print(dir_scan(tv))


def test2() -> None:
    # answer = ask_bool("Does AI work?")
    answer = input("Does AI work? (y/n): ")
    log.info(f"Answer: {answer}")


def normalize_tv_format(filename: str) -> str:
    """Converts a filename to the 's##e##' or 's####e##' format.

    Args:
        filename (str): A string containing season/episode information.

    Returns:
        str: The normalized filename formatted as 's##e##' or 's####e##'.
    """
    # Regex pattern to extract season and episode numbers from various formats
    pattern = re.compile(
        r"""
        ^s(?P<season>\d{2,4})e(?P<episode>\d{2})$ |  # Matches S##E## or S####E##
        season\s*(?P<season2>\d{2})\s*episode\s*(?P<episode2>\d{2}) |  # Season 01 Episode 01
        season(?P<season3>\d{2})\s*episode(?P<episode3>\d{2}) |  # Season01 Episode01
        season(?P<season4>\d{2})episode(?P<episode4>\d{2})  # Season01Episode01
        """,
        re.I | re.VERBOSE,
    )

    match = pattern.search(filename)
    if match:
        # Extract season and episode numbers from matched groups
        season = (
            match.group("season")
            or match.group("season2")
            or match.group("season3")
            or match.group("season4")
        )
        episode = (
            match.group("episode")
            or match.group("episode2")
            or match.group("episode3")
            or match.group("episode4")
        )

        # Normalize to "s##e##" format
        return f"s{int(season):02}e{int(episode):02}"

    log.debug("No normalization required.")
    return filename


def test3() -> None:
    filenames = [
        "The Mandalorian - S01E01 - Chapter 1.mp4",
        "The Mandalorian - Season 01 Episode 01 - Chapter 1.mp4",
        "The Mandalorian - Season01 Episode01 - Chapter 1.mp4",
        "The Mandalorian - Season01Episode01 - Chapter 1.mp4",
        "The Mandalorian - S2024E01 - Chapter 1.mp4",
    ]
    pattern = re.compile(
        r"""
        (?:
            (?:^|[\W_])                     # Start of string or non-word boundary
            (s\d{2,4})[\W_]*e(\d{2})        # Matches S##E## or S####E##
            (?:$|[\W_])
        ) |
        (?:
            (?:^|[\W_])                     # Start of string or non-word boundary
            season[\W_]*?(\d{2})[\W_]*?episode[\W_]*?(\d{2}) # Matches "season 01 episode 01" or variations
            (?:$|[\W_])
        ) |
        (?:
            (?:^|[\W_])                     # Start of string or non-word boundary
            season(\d{2})episode(\d{2})     # Matches "season01episode01"
            (?:$|[\W_])
        )
        """,
        re.I | re.VERBOSE,
    )
    for filename in filenames:
        match = pattern.search(filename)
        if match:
            season_episode = match.group()
            print(season_episode)
            print(f"Normalized: {normalize_tv_format(season_episode)}\n")
        else:
            print("No match.\n")


def test4() -> None:
    pass


def f(x, y, z):
    """Something about `f`.
    And an example:

    .. code-block:: python

        foo, bar, quux = this_is_a_long_line(lion, hippo, lemur, bear)
    """
    x = [1, 2, 3]
    y = "test string"
    z = {"key": "value"}
    return x, y, z
