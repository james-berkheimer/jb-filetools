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
import os
import re
from pathlib import Path
from typing import List, Tuple, Union

from . import CONFIG
from .logging import setup_logger

log = setup_logger(__name__)

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


def get_season_episode(filename: str) -> tuple[str | None, bool]:
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
        return alt_season_match.group(0), True  # True indicates alternate naming

    # Check for standard S##E## or S####E## format
    match = match_for_tv(filename)
    if match:
        try:
            season_episode = match.group(1).lower().split("e")
            return f"{season_episode[0]}e{season_episode[1]}", False  # False indicates standard naming
        except IndexError:
            log.warning(f"Malformed season/episode structure in filename: {filename}")
            return None, False

    # No valid match found
    return None, False


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


def get_year(target_string: str) -> str | None:
    """
    Extracts the most recent 4-digit year from a given string.

    Args:
        target_string (str): The string to search.

    Returns:
        str | None: The most recent valid year (within settings range) or None if no match is found.
    """
    year_min = CONFIG.year_min
    year_max = CONFIG.year_max

    matches = [m for m in re.findall(r"\b\d{4}\b", target_string) if year_min <= int(m) <= year_max]

    return matches[-1] if matches else None


def match_for_tv(filename: str) -> re.Match | None:
    """
    Matches TV show filenames in formats like:
    - S##E## (e.g., S02E05)
    - S####E## (e.g., S2023E01)

    Supports variations with or without delimiters.

    Returns:
        re.Match | None: The match object if found, else None.
    """
    return re.search(r"(?i)(?:^|[\W_])(s\d{2,4})[\W_]*e\d{2}(?:$|[\W_])", filename)


def match_for_altseason(filename: str) -> re.Match | None:
    """
    Matches alternate TV episode naming:
    - "# of #"

    Returns:
        re.Match | None: The match object if found, else None.
    """
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

    log.info(f"Created show map at {shows_map_path}")


def sort_media(files_obj: List[os.DirEntry]) -> Tuple[List[str], List[str]]:
    """
    Sorts files into movies and shows based on naming conventions.

    Args:
        files_obj (List[os.DirEntry]): List of file objects from os.scandir().

    Returns:
        Tuple[List[str], List[str]]: (movies, shows), containing file paths as strings.
    """
    movies = []
    shows = []

    files_to_delete = set(CONFIG.files_to_delete)
    file_excludes = set(CONFIG.file_excludes)

    for file_obj in files_obj:
        file_name = file_obj.name
        file_path = file_obj.path  # Using .path ensures the full path is used

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

        if match_for_tv(file_name):
            shows.append(file_path)
        else:
            movies.append(file_path)

    return movies, shows


# --------------------------------------------------------------------------------
# Private Methods
# --------------------------------------------------------------------------------


def _should_delete(file_name: str, files_to_delete: set) -> bool:
    """Returns True if the file should be deleted based on its name."""
    return any(delete_item in file_name for delete_item in files_to_delete)


def _should_exclude(file_name: str, file_excludes: set) -> bool:
    """Returns True if the file should be excluded from processing."""
    return any(exclude_item in file_name for exclude_item in file_excludes)
