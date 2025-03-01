import errno
import logging
import os
import re
import shutil

from .logger import setup_logger
from .questions import ask_bool
from .utils import dir_scan, make_shows_map

log = setup_logger(name="filetools", level=logging.INFO)


def test1():
    transmission = "/torrents/Transmission"
    docs = "/media/Documentaries"
    tv = "/media/Television"
    # print(dir_scan(path, get_files=True))
    # print(dir_scan(transmission))
    # print(dir_scan(docs))
    print(dir_scan(tv))


def test2():
    # answer = ask_bool("Does AI work?")
    answer = input("Does AI work? (y/n): ")
    log.info(f"Answer: {answer}")


def normalize_tv_format(filename):
    """
    Converts all items in a list to the 's##e##' or 's####e##' format.

    Args:
        tv_list (list): List of strings containing season/episode information.

    Returns:
        list: A new list with all items formatted as 's##e##' or 's####e##'.
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

    else:
        log.debug("No normalization required.")
        return filename


def test3():
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


def move_file(src, dest):
    """
    Move a file reliably across any filesystem in a Linux-based Docker container.
    - Uses os.rename() if possible (fastest).
    - Falls back to sendfile() (zero-copy, Linux-only).
    - Uses shutil.copyfile() + unlink() as a last resort.
    """

    # Try os.rename() first (fastest if on the same filesystem)
    try:
        os.rename(src, dest)
        print(f"Moved {src} -> {dest} using os.rename()")
        return
    except OSError as e:
        if e.errno != errno.EXDEV:  # EXDEV means "cross-device link not permitted"
            raise  # Re-raise other errors

    # If os.rename() fails due to cross-filesystem move, try sendfile()
    try:
        with open(src, "rb") as fsrc, open(dest, "wb") as fdst:
            os.sendfile(fdst.fileno(), fsrc.fileno(), 0, os.stat(src).st_size)
        os.unlink(src)  # Remove source after copy
        print(f"Moved {src} -> {dest} using sendfile()")
        return
    except OSError:
        pass  # If sendfile() fails, continue to shutil

    # Final fallback: Use shutil.copyfile() and remove source manually
    shutil.copyfile(src, dest)
    os.unlink(src)  # Remove source after copying
    print(f"Moved {src} -> {dest} using shutil.copyfile() + unlink()")


def test4():
    import os
    import shutil

    src = "/transmission/test_file.mkv"
    dest = "/media/movies/test_file.mkv"

    move_file(src, dest)
