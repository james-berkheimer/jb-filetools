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
from typing import Union

from filetools import CONFIG

log = logging.getLogger("filetools")

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------------


def dir_scan(scan_path: str | Path, get_files: bool = False) -> list[os.DirEntry]:
    """Scan a directory and return a list of sorted entries.

    Args:
        scan_path: Path to the directory to scan
        get_files: If True, return files; if False, return directories

    Returns:
        list[os.DirEntry]: Sorted list of directory entries

    Raises:
        PermissionError: If access to the directory is denied
    """
    scan_path = Path(scan_path)

    if not scan_path.exists():
        log.warning(f"Directory scan failed: {scan_path} does not exist.")
        return []

    if not scan_path.is_dir():
        log.warning(f"Provided path is not a directory: {scan_path}")
        return []

    # log.debug(f"Scanning directory: {scan_path}, get_files: {get_files}")

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


def get_show_map() -> configparser.ConfigParser:
    """Read the shows_map.ini file configuration.

    Creates the file if it doesn't exist by calling make_shows_map().

    Returns:
        configparser.ConfigParser: Parsed configuration mapping show names to paths
    """
    shows_map_path = Path(CONFIG.settings_path).parent.joinpath("shows_map.ini")

    if not shows_map_path.exists():
        log.info("No show_map.ini found. Creating one now...")
        make_shows_map()

    config = configparser.ConfigParser()
    config.read(shows_map_path)
    return config


def parse_filename(filename: str) -> tuple[str | None, str | None]:
    """Extract show name and season/episode information from a filename.

    Handles both standard (S01E01) and alternate (1 of 10) naming formats.

    Args:
        filename: The filename to parse

    Returns:
        tuple[str | None, str | None]: (show_name, season_episode) or (None, None) if no match

    Example:
        >>> parse_filename("Show.Name.S01E02.mp4")
        ('Show Name', 's01e02')
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


def match_for_tv(filename: str) -> tuple[bool, str | None]:
    """Match TV show episode patterns in filenames.

    Supports formats:
    - S##E## (e.g., S02E05)
    - S####E## (e.g., S2023E01)
    - #x## (e.g., 1x01)
    - season 01 episode 01
    - season01 episode01
    - season01episode01

    Args:
        filename: Filename to check for TV show patterns

    Returns:
        tuple[bool, str | None]: (True, matched_text) if found, (False, None) if not found
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
            (\d{1,2})x(\d{2})              # Matches #x## format
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
    match = pattern.search(filename)
    if match:
        return True, match.group()
    return False, None


def match_for_altseason(filename: str) -> re.Match | None:
    """Match alternate TV episode format "# of #".

    Args:
        filename: Filename to check for alternate format

    Returns:
        re.Match | None: Match object if pattern found, None otherwise

    Example:
        >>> match_for_altseason("Episode 1 of 10.mp4")
        <re.Match object; span=(8, 14), match='1 of 10'>
    """
    log.debug(f"Matching alternate season format: {filename} | Type: {type(filename)}")
    return re.search(r"\b(\d{1,2})\s*of\s*(\d{1,2})\b", filename, re.I)


def make_shows_map() -> None:
    """Create or update the shows_map.ini file mapping show names to filesystem paths.

    Scans all show library paths defined in CONFIG.shows and creates a mapping of
    show folder names to their full filesystem paths. The mapping is stored in
    shows_map.ini in the same directory as the settings file.

    Directory structure expected:
    library_path/
        network_folder/
            show_folder/
                episode files

    Notes:
        - Skips folders named 'empty' (case-insensitive)
        - Creates shows_map.ini next to the settings file
        - Overwrites existing shows_map.ini if present
        - Logs warnings for invalid library paths

    Example structure in shows_map.ini:
        [Shows]
        Show Name = /path/to/library/network/show_name
        Another Show = /path/to/library/network/another_show
    """
    config = configparser.ConfigParser()
    show_libraries = CONFIG.shows
    shows_dict = {}

    for _, library_path in show_libraries.items():
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
    """Convert various season/episode formats to standard 's##e##' format.

    Args:
        season_episode: String containing season/episode information

    Returns:
        str: Normalized format (e.g., 's01e02')

    Example:
        >>> normalize_tv_format("1x02")
        's01e02'
    """
    pattern = re.compile(
        r"""
        s(?P<season>\d{2,4})e(?P<episode>\d{2}) |
        (?P<season2>\d{1,2})x(?P<episode2>\d{2}) |
        season\s*(?P<season3>\d{1,4})\s*episode\s*(?P<episode3>\d{1,3}) |
        season(?P<season4>\d{1,4})\s*episode(?P<episode4>\d{1,3}) |
        season(?P<season5>\d{1,4})episode(?P<episode5>\d{1,3})
        """,
        re.I | re.VERBOSE,
    )

    match = pattern.search(season_episode)
    if match:
        season = next(
            (match.group(g) for g in match.groupdict() if "season" in g and match.group(g)), None
        )
        episode = next(
            (match.group(g) for g in match.groupdict() if "episode" in g and match.group(g)), None
        )

        if season and episode:
            return f"s{int(season):02}e{int(episode):02}"

    log.debug("No normalization required.")
    return season_episode


def sort_media(files_obj: list[os.DirEntry]) -> tuple[list[Path], list[Path]]:
    """Sort media files into movies and TV shows.

    Args:
        files_obj: List of file entries from os.scandir()

    Returns:
        tuple[list[Path], list[Path]]: Lists of movie and show paths respectively

    Notes:
        - Deletes files matching patterns in CONFIG.files_to_delete
        - Excludes files matching patterns in CONFIG.FILE_EXT_EXCLUDES
        - Only processes files with extensions in CONFIG.video_file_extensions
    """
    movies = []
    shows = []

    files_to_delete = set(CONFIG.files_to_delete)
    file_ext_excludes = set(CONFIG.file_extension_excludes)
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

        if _should_exclude(file_name, file_ext_excludes):
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
    """Convert "# of #" format to 's01e##' format.

    Args:
        season_episode: String containing "# of #" pattern

    Returns:
        str: Formatted as 's01e##' where ## is the first number
    """
    episode = f"e{int(season_episode.split('of')[0]):02}"
    return f"s01{episode}"


def _should_delete(file_name: str, files_to_delete: set) -> bool:
    """Check if file should be deleted based on name patterns.

    Args:
        file_name: Name of file to check
        files_to_delete: Set of patterns indicating files to delete

    Returns:
        bool: True if file matches any deletion pattern
    """
    return any(delete_item in file_name for delete_item in files_to_delete)


def _should_exclude(file_name: str, file_ext_excludes: set) -> bool:
    """Check if file should be excluded from processing.

    Args:
        file_name: Name of file to check
        FILE_EXT_EXCLUDES: Set of patterns indicating files to exclude

    Returns:
        bool: True if file matches any exclusion pattern
    """
    return any(exclude_item in file_name for exclude_item in file_ext_excludes)
