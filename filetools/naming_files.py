import logging
import os
import re
import traceback
from pathlib import Path
from typing import Union

from filetools import CONFIG
from filetools.utils import dir_scan, parse_filename

log = logging.getLogger("filetools")

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Public Functions
# --------------------------------------------------------------------------------


def rename_files(target_dir: Path, debug: bool = False) -> None:
    """Scan and rename files in target directory using standardized naming conventions.

    Args:
        target_dir: Directory containing files to be renamed
        debug: If True, run in simulation mode without making actual changes

    Raises:
        OSError: If file operations fail
    """
    for file_obj in dir_scan(target_dir, get_files=True):
        # Update to use correct config attribute
        if _should_delete(file_obj.name):
            log.info(f"Deleting.....{file_obj.name}")
            os.remove(file_obj.path)
            continue

        # Update to use correct config attributes
        file_ext = os.path.splitext(file_obj.name)[1]
        if file_ext in CONFIG.valid_extensions and file_ext not in CONFIG.excluded_extensions:
            try:
                _rename(file_obj, debug)
            except Exception as e:
                log.error(f"Failed to rename {file_obj.name}: {e}\n{traceback.format_exc()}")


# --------------------------------------------------------------------------------
# Private Functions
# --------------------------------------------------------------------------------


def _format_tv_show_name(
    sanitized_episode_name: str, season_episode: str, flags_name: str, file_ext: str
) -> str:
    """Format TV show filename with season and episode information.

    Args:
        sanitized_episode_name: Clean show name without special characters
        season_episode: Season and episode identifier (e.g. 's01e01')
        flags_name: Additional flags like 4K or HDR
        file_ext: File extension including dot

    Returns:
        str: Formatted filename in the pattern: show_name_s01e01[flags].ext
    """
    log.debug(f"\tsanitized_episode_name: {sanitized_episode_name}")
    log.debug(f"\tseason_episode: {season_episode}")
    log.debug(f"\tflags_name: {flags_name}")
    log.debug(f"\tfile_ext: {file_ext}")
    return f"{sanitized_episode_name}_{season_episode}{flags_name}{file_ext}".lower()


def _format_movie_name(filename_wo_ext: str, file_ext: str) -> str:
    """Format movie filename with year and quality flags.

    Args:
        filename_wo_ext: Movie name without extension
        file_ext: File extension including dot

    Returns:
        str: Formatted filename in the pattern: movie_name(year)-4K-hdr.ext
    """
    fk, hdr = "", ""
    if "2160p" in filename_wo_ext:
        fk = "-4K"
    if any(hdr_tag in filename_wo_ext for hdr_tag in ["hdr", "hdr10plus"]):
        hdr = "-hdr"

    if "." in filename_wo_ext:
        filename_wo_ext = "_".join(filename_wo_ext.split(".")).lower()
    filename_wo_ext = filename_wo_ext.replace(" (", "_").replace(" ", "_").replace("'", "").lower()
    year = _get_year(filename_wo_ext)
    if year:
        filename_wo_ext_split = filename_wo_ext.split(year)[0]
        return f"{filename_wo_ext_split}({year}){fk}{hdr}{file_ext}"

    log.warning(f"Failed to rename {filename_wo_ext}: No valid year found.")
    return filename_wo_ext + file_ext


def _get_year(target_string: str) -> str | None:
    """Extract the most recent 4-digit year from a string.

    Args:
        target_string: String to search for year

    Returns:
        str | None: Most recent valid year between year_min and year_max, or None if not found
    """
    year_min = CONFIG.year_min
    year_max = CONFIG.year_max
    try:
        matches = re.findall(r"[0-9]{4}", target_string)
    except FileNotFoundError:
        log.warning("NO YEAR MATCHES")
        return None

    filtered_matches = [m for m in matches if year_min <= int(m) <= year_max]

    if not filtered_matches:
        return None

    return filtered_matches[-1]


def _is_properly_formatted(file_name: str) -> bool:
    """Check if filename matches movie or TV show naming conventions and contains no illegal words.

    Args:
        file_name: Name of file to check

    Returns:
        bool: True if filename matches either movie or show pattern and contains no illegal words

    Examples of valid show names:
        - show_name_s01e01.mkv
        - multiple_word_show_name_s01e01.mkv
        - show_name_s01e01[4k_hdr].mkv

    Examples of valid movie names:
        - movie_name_(2023).mkv
        - multiple_word_movie_(2023).mkv

    Invalid examples:
        - pbs_show_name_s01e01.mkv (contains illegal word 'pbs')
        - bbc.show.name.s01e01.mkv (contains illegal word 'bbc')
        - show.name.s01e01.mkv (uses periods instead of underscores)
        - show_name_101.mkv (incorrect season/episode format)
    """
    file_lower = file_name.lower()
    if any(word.lower() in file_lower for word in CONFIG.name_cleanup_flags):
        return False

    show_pattern = re.compile(
        r"""^
        ([a-z0-9]+          # First word
        (?:_[a-z0-9]+)*)    # Additional words, each preceded by single underscore
        _                   # Single underscore before season/episode
        s\d{2,4}e\d{2}      # Season and starting episode
        (?:-e\d{2})?        # Optional ending episode (multi-episode support)
        (?:_\[[\w_]+\])?    # Optional quality flags with leading underscore
        \.[a-z0-9]+         # File extension
        $""",
        re.VERBOSE,
    )

    movie_pattern = re.compile(
        r"""^
        ([a-z0-9]+
        (?:_[a-z0-9]+)*)    # Additional words, each preceded by single underscore
        _\(\d{4}\)          # Year in parentheses with underscore before
        \.[a-z0-9]+         # File extension
        $""",
        re.VERBOSE,
    )

    return bool(movie_pattern.match(file_name) or show_pattern.match(file_name))


def _rename(file_obj: os.DirEntry | Path, debug: bool = False) -> None:
    """Rename a file using standardized naming conventions.

    Args:
        file_obj: File object to rename
        debug: If True, run in simulation mode without making actual changes

    Raises:
        OSError: If rename operation fails
    """
    new_name = ""
    flags = []
    file_obj_name = file_obj.name.lower()

    if _is_properly_formatted(file_obj.name):
        log.info(f"Skipping.....{file_obj.name} (already properly formatted)")
        return

    if "2160p" in file_obj_name:
        flags.append("4K")
    if any(hdr_tag in file_obj_name for hdr_tag in ["hdr", "hdr10", "hdr10plus"]):
        flags.append("hdr")
    flags_name = f"_[{'_'.join(flags)}]" if flags else ""

    file_path = Path(file_obj.path).parent
    filename_wo_ext, file_ext = os.path.splitext(file_obj_name)
    show_name, season_episode = parse_filename(filename_wo_ext)

    if show_name and season_episode:
        sanitized_show_name = _sanitize_show_name(
            show_name,
        )
        sanitized_season_episode = _sanitize_season_episode(season_episode)
        new_name = _format_tv_show_name(
            sanitized_show_name, sanitized_season_episode, flags_name, file_ext
        )
    else:
        new_name = _format_movie_name(filename_wo_ext, file_ext)

    new_name_path = file_path / new_name
    if not new_name_path.exists():
        if not debug:
            log.info(f"Renaming.....{file_obj.name} -> {new_name}")
            os.rename(file_obj.path, new_name_path)
        else:
            log.info(f"[Debug] Renaming.....{file_obj.name} -> {new_name}")


def _sanitize_show_name(show_name: str) -> str:
    """Clean up show name by removing unwanted words and special characters.

    Args:
        show_name: Original show name

    Returns:
        str: Sanitized show name in lowercase with single underscores only
    """
    log.debug(f"\tshow_name: {show_name}")
    sanitized_filename = show_name
    name_cleanup_flags = CONFIG.name_cleanup_flags
    # First remove unwanted words
    for word in name_cleanup_flags:
        sanitized_filename = sanitized_filename.replace(word, "")

    log.debug(f"\tsanitized_filename: {sanitized_filename}")

    # Initial cleanup
    sanitized_filename = sanitized_filename.lstrip().lstrip(".").rstrip(".")

    # Initial character replacements
    sanitized_filename = (
        sanitized_filename.replace(" ", "_")
        .replace(".", "_")
        .replace("'", "")
        .replace(",", "")
        .replace("!", "")
        .replace("?", "")
        .replace("-", "_")
        .replace("_-_", "_")
    )

    # Keep cleaning up until no more changes are made
    prev_name = ""
    while prev_name != sanitized_filename:
        prev_name = sanitized_filename
        # Remove consecutive underscores
        sanitized_filename = sanitized_filename.replace("__", "_")
        # Remove any trailing/leading underscores
        sanitized_filename = sanitized_filename.strip("_")

    return sanitized_filename.lower()


def _sanitize_season_episode(season_episode: str) -> str:
    """Clean up season and episode identifier.

    Args:
        season_episode: Original season/episode string (e.g. 'S01E01', 's.01.e.01')

    Returns:
        str: Clean season/episode string (e.g. 's01e01')
    """
    return season_episode.lower().replace(".", "").replace(" ", "").replace("_", "")


def _should_delete(file_name: str) -> bool:
    """Check if file matches exactly any filename in the deletion list.

    Args:
        file_name: Name of file to check

    Returns:
        bool: True if file matches any name or extension in deletable_extensions
    """
    _, ext = os.path.splitext(file_name)
    return file_name in CONFIG.deletable_extensions or ext in CONFIG.deletable_extensions
