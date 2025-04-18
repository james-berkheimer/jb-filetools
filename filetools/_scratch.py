if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        globals()[sys.argv[1]]()

import errno
import logging
import os
import re
import shutil
import time
from pathlib import Path
from typing import Optional

import pathspec

from filetools.logger import setup_logger
from filetools.questions import ask_bool
from filetools.utils import dir_scan, make_shows_map

log = setup_logger(name="filetools", level=logging.INFO)


def test1() -> None:
    root_dir = Path(".")  # or specify your project root
    print_directory_tree(root_dir)


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
    src1 = "/mnt/media/transmission/_saved/test_file1.mkv"
    src2 = "/mnt/media/transmission/_saved/test_file2.mkv"
    dest = "/mnt/media/documentaries"

    # shutil.move test
    start = time.perf_counter()
    shutil.move(src1, dest)
    print(f"shutil.move: {time.perf_counter() - start:.6f} seconds")

    # os.rename test
    start = time.perf_counter()
    os.rename(src2, os.path.join(dest, os.path.basename(src2)))
    print(f"os.rename: {time.perf_counter() - start:.6f} seconds")


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


def print_directory_tree(
    directory: Path, indent: str = "", exclude_patterns: Optional[list[str]] = None
) -> None:
    """Print a directory tree structure starting from the given path.

    Args:
        directory: Path object pointing to the directory to print
        indent: String used for indentation (used recursively)
        exclude_patterns: List of patterns to exclude (e.g. ['__pycache__', '.git'])
    """
    if exclude_patterns is None:
        exclude_patterns = [
            ".venv",
            "__pycache__",
            ".git",
            ".ruff_cache",
            ".vscode",
        ]  # Simplified exclude list

    directory = Path(directory)
    if not directory.is_dir():
        return

    print(f"{indent}{directory.name}/")
    indent += "    "

    for path in sorted(directory.iterdir()):
        # Skip excluded directories
        if path.is_dir() and path.name in exclude_patterns:
            continue

        if path.is_dir():
            print_directory_tree(path, indent, exclude_patterns)
        else:
            print(f"{indent}{path.name}")


def test_formatting(a, b) -> int:
    if a == b:
        print("Equal")
    else:
        print("Not Equal")


def unused_function(x, y):
    return x + y
