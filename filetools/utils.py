#!/usr/bin/env python
#
# modules/utils.py
#
# This file will store globally used functions used in this project
#

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------
import configparser
import logging
import os
import re
from pathlib import Path
from typing import List, Tuple, Union

from . import CONFIG

log = logging.getLogger("filetools")

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------
FILES_TO_DELETE = CONFIG.files_to_delete
FILE_EXCLUDES = CONFIG.file_excludes
# Libraries
MOVIE_LIBRARIES = CONFIG.movies
SHOW_LIBRARIES = CONFIG.shows
MUSIC_LIBRARIES = CONFIG.music


# --------------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------------


def dir_scan(scan_path: Union[str, Path], get_files: bool = False) -> List[os.DirEntry]:
    """
    Scans a directory and returns a list of os.DirEntry objects.

    Args:
        scan_path (Union[str, Path]): The path to the directory to scan.
        get_files (bool, optional): If True, return files; if False, return directories.

    Returns:
        List[os.DirEntry]: A sorted list of os.DirEntry objects (files or directories).
    """
    scan_path = Path(scan_path)

    if not scan_path.exists():
        log.warning(f"Directory scan failed: {scan_path} does not exist.")
        return []

    if not scan_path.is_dir():
        log.warning(f"Provided path is not a directory: {scan_path}")
        return []

    log.debug(f"Scanning directory: {scan_path}, get_files: {get_files}")

    scan_output = []

    try:
        with os.scandir(scan_path) as scan_obj:
            if get_files:
                scan_output = sorted(
                    [entry for entry in scan_obj if entry.is_file()], key=lambda e: e.name
                )
            else:
                scan_output = sorted(
                    [entry for entry in scan_obj if entry.is_dir()], key=lambda e: e.name
                )

    except PermissionError:
        log.warning(f"Permission denied when scanning {scan_path}")
        return []

    log.debug(f"Scan complete. Total entries found: {len(scan_output)}")
    return scan_output


def get_show_map():
    """
    Reads the shows_map.ini file and returns a configparser object.

    If the file doesn't exist, calls make_shows_map() to create it first.
    """
    shows_map_path = Path(CONFIG.settings_path).parent.joinpath("shows_map.ini")

    if not shows_map_path.exists():
        log.info("No show_map.ini found. Creating one now...")
        make_shows_map()

    config = configparser.ConfigParser()
    config.read(shows_map_path)
    return config


def parse_filename(filename: str) -> tuple[str | str]:
    """
    Extracts the season and episode number from a filename.

    Args:
        filename (str): The filename to parse.

    Returns:
        Tuple[str | None, bool]: The extracted season/episode string and a flag indicating if an alternate naming format was detected.
    """
    # Check for alternate season naming (e.g., "1 of 10")
    alt_season_match = match_for_altseason(filename)
    if alt_season_match:
        show_name = filename.split(alt_season_match.group(0))[0].strip()
        try:  # Test for series in name
            show_name = show_name.split("series")[0].strip()
        except IndexError:
            log.error(f"Failed to split series from show name: {show_name}")
        season_episode = _fix_season_episode(alt_season_match.group(0))
        return show_name, season_episode

    # Check for standard S##E## or S####E## format
    match, match_text = match_for_tv(filename)
    if match:
        try:
            show_name = filename.split(match_text)[0].strip()
            season_episode = normalize_tv_format(match_text)
            return show_name, season_episode
        except IndexError:
            log.warning(f"Malformed season/episode structure in filename: {filename}")
            return None, None
    else:
        # No valid match found
        return None, None


def match_for_tv(filename: str) -> re.Match | None:
    """
    Matches TV show filenames in formats like:
    - S##E## (e.g., S02E05)
    - S####E## (e.g., S2023E01)
    - season 01 episode 01
    - season01 episode01
    - season01episode01

    Supports variations with or without delimiters.

    Returns:
        re.Match | None: The match object if found, else None.
    """
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
    log.debug(f"Matching TV show filename: {filename}")
    match = pattern.search(filename)
    log.debug(f"Match: {match}")
    if match:
        return True, match.group()
    else:
        return False, None


def match_for_altseason(filename: str) -> re.Match | None:
    """
    Matches alternate TV episode naming:
    - "# of #"

    Returns:
        re.Match | None: The match object if found, else None.
    """
    log.debug(f"Matching alternate season format: {filename} | Type: {type(filename)}")
    return re.search(r"\b(\d{1,2})\s*of\s*(\d{1,2})\b", filename, re.I)


def make_shows_map():
    """
    Builds an INI file (shows_map.ini) that maps show folder names to their filesystem paths.
    Instead of scanning TELEVISION_PATH and DOCUMENTARIES_PATH, we now scan
    each library path in CONFIG.shows (i.e., all 'shows' libraries).
    """
    config = configparser.ConfigParser()
    shows_dict = {}

    for _, library_path in SHOW_LIBRARIES.items():
        lib_path = Path(library_path)
        if not lib_path.is_dir():
            log.warning(f"Show library path does not exist: {lib_path}")
            continue

        for network_obj in dir_scan(lib_path):
            if network_obj.is_dir():
                network_path = Path(network_obj.path)
                for show_obj in dir_scan(network_path):
                    if show_obj.name.lower() != "empty":
                        shows_dict[show_obj.name] = show_obj.path

    config["Shows"] = shows_dict

    shows_map_path = Path(CONFIG.settings_path).parent.joinpath("shows_map.ini")
    with open(shows_map_path, "w") as configfile:
        config.write(configfile)

    log.debug(f"Created show map at {shows_map_path}")


def normalize_tv_format(season_episode: str) -> str:
    """
    Converts season_episode in a list to the 's##e##' or 's####e##' format.

    Args:
        season_episode (str): List of strings containing season/episode information.

    Returns:
        str: season_episode formatted as 's##e##' or 's####e##'.
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

    match = pattern.search(season_episode)
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
        return season_episode


def sort_media(files_obj: List[os.DirEntry]) -> Tuple[List[Path], List[Path]]:
    """
    Sorts files into movies and shows based on naming conventions.

    Args:
        files_obj (List[os.DirEntry]): List of file objects from os.scandir().

    Returns:
        Tuple[List[Path], List[Path]]: (movies, shows), containing file paths as Path objects.
    """
    movies = []
    shows = []

    files_to_delete = set(CONFIG.files_to_delete)
    file_excludes = set(CONFIG.file_excludes)
    valid_extensions = set(CONFIG.video_file_extensions)

    for file_obj in files_obj:
        file_name = file_obj.name
        file_path = Path(file_obj.path)

        if not any(file_name.lower().endswith(ext) for ext in valid_extensions):
            log.debug(f"Skipping invalid file type: {file_path}")
            continue

        if _should_delete(file_name, files_to_delete):
            log.info(f"Deleting: {file_path}")
            try:
                os.remove(file_path)
            except OSError as e:
                log.warning(f"Failed to delete {file_path}: {e}")
            continue

        if _should_exclude(file_name, file_excludes):
            log.debug(f"Skipping excluded file: {file_path}")
            continue

        if match_for_tv(file_name)[0]:
            log.debug(f"Adding TV show: {file_path}")
            shows.append(file_path)
        else:
            log.debug(f"Adding movie: {file_path}")
            movies.append(file_path)

    return movies, shows


# --------------------------------------------------------------------------------
# Private Methods
# --------------------------------------------------------------------------------
def _fix_season_episode(season_episode: str) -> str:
    """
    Fixes season and episode formatting. Defaults season to 's01' for single-season documentaries.
    """
    episode = f"e{int(season_episode.split('of')[0]):02}"
    return f"s01{episode}"


def _should_delete(file_name: str, files_to_delete: set) -> bool:
    """Returns True if the file should be deleted based on its name."""
    return any(delete_item in file_name for delete_item in files_to_delete)


def _should_exclude(file_name: str, file_excludes: set) -> bool:
    """Returns True if the file should be excluded from processing."""
    return any(exclude_item in file_name for exclude_item in file_excludes)
