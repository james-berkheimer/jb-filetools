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

from filetools import CONFIG

log = logging.getLogger("filetools")

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------

# Season/episode markers. The lookbehind/lookahead require a non-alphanumeric
# neighbour so tags like "1920x1080" or "x264" are never mistaken for "1x01".
TV_PATTERN = re.compile(
    r"""
    (?<![a-z0-9])
    (?:
        s(?P<season>\d{1,4})[\W_]*e(?P<episode>\d{2,3})       # S01E01, S2018E01, s00e201
        (?:(?:[-_]?e|-)(?P<episode_end>\d{2,3}))?             # S01E01E02, S01E01-E02, S01E01-02
      |
        (?P<x_season>\d{1,2})x(?P<x_episode>\d{2,3})          # 1x01
      |
        season[\W_]*(?P<long_season>\d{1,4})                  # season 01 episode 01,
        [\W_]*episode[\W_]*(?P<long_episode>\d{1,3})          # season01episode01
    )
    (?![a-z0-9])
    """,
    re.I | re.VERBOSE,
)

# "Part 1 of 5" style numbering, used when there is no season marker.
ALT_SEASON_PATTERN = re.compile(r"(?<![a-z0-9])(\d{1,2})[\s._-]*of[\s._-]*(\d{1,2})(?![a-z0-9])", re.I)

SHOWS_MAP_FILENAME = "shows_map.ini"

# Leading bytes identifying video containers, for downloads that arrive with no
# extension. Keyed by the extension the file should be given.
VIDEO_SIGNATURES = (
    (".mkv", lambda h: h[:4] == b"\x1a\x45\xdf\xa3"),  # Matroska/WebM (EBML)
    (".mov", lambda h: h[4:8] == b"ftyp" and h[8:10] == b"qt"),  # QuickTime
    (".mp4", lambda h: h[4:8] == b"ftyp"),  # MP4 and friends
    (".avi", lambda h: h[:4] == b"RIFF" and h[8:12] == b"AVI "),  # AVI
    (".mpg", lambda h: h[:4] == b"\x00\x00\x01\xba"),  # MPEG program stream
)

# Leading bytes of Windows, Linux and macOS executables. Fake episodes are often
# executables, whatever the file is named.
EXECUTABLE_SIGNATURES = (
    b"MZ",  # Windows PE
    b"\x7fELF",  # Linux ELF
    b"\xfe\xed\xfa\xce",
    b"\xfe\xed\xfa\xcf",  # Mach-O
    b"\xce\xfa\xed\xfe",
    b"\xcf\xfa\xed\xfe",  # Mach-O, byte-swapped
)

# --------------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------------


def detect_video_extension(file_path: str | Path) -> str | None:
    """Work out which video container a file is from its own first bytes.

    Downloads occasionally arrive with no extension, which would otherwise make
    them invisible to every step of the tool.

    Args:
        file_path: File to inspect

    Returns:
        str | None: The extension the file should have, or None if it is not a
        recognised video container.
    """
    header = _read_header(file_path)
    for extension, matches in VIDEO_SIGNATURES:
        if matches(header):
            return extension
    return None


def is_executable(file_path: str | Path) -> bool:
    """True if a file's first bytes mark it as a Windows, Linux or macOS executable."""
    return _read_header(file_path).startswith(EXECUTABLE_SIGNATURES)


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


def get_show_map() -> configparser.ConfigParser:
    """Read the shows_map.ini file configuration.

    Creates the file if it doesn't exist by calling make_shows_map().

    Returns:
        configparser.ConfigParser: Parsed configuration mapping show names to paths
    """
    shows_map_path = _shows_map_path()

    if not shows_map_path.exists():
        log.info("No show_map.ini found. Creating one now...")
        make_shows_map()

    config = configparser.ConfigParser(interpolation=None)
    config.read(shows_map_path)
    return config


def parse_filename(filename: str) -> tuple[str | None, str | None]:
    """Extract show name and season/episode information from a filename.

    Standard markers (S01E01, 1x01, "season 1 episode 1") take precedence over the
    alternate "1 of 10" format, so "Show.S01E05.Part.1.of.2" is episode 5, not 1.

    Args:
        filename: The filename to parse

    Returns:
        tuple[str | None, str | None]: (show_name, season_episode) or (None, None) if no match

    Example:
        >>> parse_filename("Show.Name.S01E02.mp4")
        ('Show.Name', 's01e02')
    """
    tv_match = TV_PATTERN.search(filename)
    if tv_match:
        show_name = _clean_show_name(filename[: tv_match.start()])
        return show_name, normalize_tv_format(tv_match.group())

    alt_season_match = match_for_altseason(filename)
    if alt_season_match:
        show_name = filename[: alt_season_match.start()]
        show_name = re.split(r"(?<![a-z0-9])series(?![a-z0-9])", show_name, flags=re.I)[0]
        show_name = re.sub(r"[\W_]*(?:part|episode|ep)[\W_]*$", "", show_name, flags=re.I)
        return _clean_show_name(show_name), f"s01e{int(alt_season_match.group(1)):02}"

    return None, None


def match_for_tv(filename: str) -> tuple[bool, str | None]:
    """Match TV show episode patterns in filenames.

    Supports formats:
    - S##E## (e.g., S02E05), including single-digit seasons (S1E05)
    - S##E##E##, S##E##-E##, S##E##-## (multi-episode)
    - S####E## (e.g., S2023E01)
    - S##E### (three-digit episodes, e.g., S00E201)
    - #x## (e.g., 1x01)
    - season 01 episode 01 / season01episode01

    Args:
        filename: Filename to check for TV show patterns

    Returns:
        tuple[bool, str | None]: (True, matched_text) if found, (False, None) if not found
    """
    match = TV_PATTERN.search(filename)
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
        >>> match_for_altseason("Horizon.Part.1.of.5.mp4")
        <re.Match object; span=(13, 19), match='1.of.5'>
    """
    log.debug(f"Matching alternate season format: {filename}")
    return ALT_SEASON_PATTERN.search(filename)


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
    config = configparser.ConfigParser(interpolation=None)
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

    shows_map_path = _shows_map_path()
    with open(shows_map_path, "w") as configfile:
        config.write(configfile)

    log.debug(f"Created show map at {shows_map_path}")


def normalize_tv_format(season_episode: str) -> str:
    """Convert various season/episode formats to standard 's##e##' or 's##e##-e##' format.

    Args:
        season_episode: String containing season/episode information

    Returns:
        str: Normalized format (e.g., 's01e02', 's00e201' or 's03e08-e09')
    """
    match = TV_PATTERN.search(season_episode)
    if not match:
        log.debug("No normalization required.")
        return season_episode

    season = match["season"] or match["x_season"] or match["long_season"]
    episode = match["episode"] or match["x_episode"] or match["long_episode"]
    normalized = f"s{int(season):02}e{int(episode):02}"
    if match["episode_end"]:
        normalized += f"-e{int(match['episode_end']):02}"
    return normalized


def sort_media(files_obj: list[os.DirEntry]) -> tuple[list[Path], list[Path]]:
    """Sort media files into movies and TV shows.

    Args:
        files_obj: List of file entries from os.scandir()

    Returns:
        tuple[list[Path], list[Path]]: Lists of movie and show paths respectively

    Notes:
        - Excludes files matching patterns in CONFIG.excluded_extensions
        - Only processes files with extensions in CONFIG.valid_extensions
    """
    movies = []
    shows = []

    for file_obj in files_obj:
        file_name = file_obj.name
        file_path = Path(file_obj.path)

        if not any(file_name.lower().endswith(ext) for ext in CONFIG.valid_extensions):
            log.debug(f"Skipping invalid file type: {file_path}")
            continue

        if should_exclude(file_name, CONFIG.excluded_extensions):
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
def _read_header(file_path: str | Path) -> bytes:
    """First bytes of a file, or empty if it cannot be read."""
    try:
        with open(file_path, "rb") as f:
            return f.read(12)
    except OSError as e:
        log.debug(f"Could not read {file_path}: {e}")
        return b""


def _clean_show_name(show_name: str) -> str:
    """Trim whitespace and dangling separators left over from splitting a filename."""
    return show_name.strip(" ._-")


def should_exclude(file_name: str, file_ext_excludes: set) -> bool:
    """Check if file should be excluded from processing.

    Exclusions are name endings (".part", "sample.mkv"), so "the.party.1968.mkv"
    is not mistaken for a partial download.

    Args:
        file_name: Name of file to check
        file_ext_excludes: Set of name endings indicating files to exclude

    Returns:
        bool: True if file matches any exclusion pattern
    """
    name = file_name.lower()
    return any(name.endswith(exclude_item.lower()) for exclude_item in file_ext_excludes)


def _shows_map_path() -> Path:
    """Location of shows_map.ini: next to the active settings file."""
    return Path(CONFIG.settings_path).parent.joinpath(SHOWS_MAP_FILENAME)
