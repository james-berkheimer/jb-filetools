import logging
import os
import re
import traceback
from pathlib import Path
from typing import Union

from . import CONFIG
from .utils import dir_scan, parse_filename

log = logging.getLogger("filetools")

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------
FILES_TO_DELETE = CONFIG.files_to_delete
FILE_EXCLUDES = CONFIG.file_excludes
VIDEO_FILE_EXTENSIONS = CONFIG.video_file_extensions
NAME_CLEANUP_FLAGS = CONFIG.name_cleanup_flags  # New setting for words to remove from filenames

# --------------------------------------------------------------------------------
# Public Functions
# --------------------------------------------------------------------------------


def rename_files(target_dir: Path, debug: bool = False):
    """
    Scans and renames files in the target directory based on predefined naming conventions.

    Args:
        target_dir (Path): The directory containing files to be renamed.
    """
    for file_obj in dir_scan(target_dir, get_files=True):
        if _should_delete(file_obj.name):
            log.info(f"Deleting.....{file_obj.name}")
            os.remove(file_obj.path)
            continue

        file_ext = os.path.splitext(file_obj.name)[1]
        if file_ext in VIDEO_FILE_EXTENSIONS and file_ext not in FILE_EXCLUDES:
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
    """Formats a TV show filename with season and episode information."""
    log.debug(f"\tsanitized_episode_name: {sanitized_episode_name}")
    log.debug(f"\tseason_episode: {season_episode}")
    log.debug(f"\tflags_name: {flags_name}")
    log.debug(f"\tfile_ext: {file_ext}")
    return f"{sanitized_episode_name}_{season_episode}{flags_name}{file_ext}".lower()


def _format_movie_name(filename_wo_ext: str, file_ext: str) -> str:
    """Formats a movie filename, extracting year and applying proper conventions."""
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
        new_name = f"{filename_wo_ext_split}({year}){fk}{hdr}{file_ext}"
        return new_name

    log.warning(f"Failed to rename {filename_wo_ext}: No valid year found.")
    return filename_wo_ext + file_ext


def _get_year(target_string: str) -> str | None:
    """
    Extracts the most recent 4-digit year from a given string.

    Args:
        target_string (str): The string to search.

    Returns:
        str | None: The most recent valid year (within settings range) or None if no match is found.
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
    """
    Checks if a file name is properly formatted as either a movie or a TV show.

    Args:
        file_name (str): The name of the file to check.

    Returns:
        bool: True if the file name is properly formatted, False otherwise.
    """
    movie_pattern = re.compile(r"^[a-z0-9_]+_\(\d{4}\)\.[a-z0-9]+$")
    show_pattern = re.compile(r"^[a-z0-9_]+_s\d{2,4}e\d{2,3}\.[a-z0-9]+$")

    return bool(movie_pattern.match(file_name) or show_pattern.match(file_name))


def _rename(file_obj: Union[os.DirEntry, Path], debug: bool = False):
    """Renames a file based on predefined naming conventions."""
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
    """
    Cleans up filename by removing unwanted words and characters based on user-defined settings.
    """
    sanitized_filename = show_name
    for word in NAME_CLEANUP_FLAGS:
        sanitized_filename = sanitized_filename.replace(word, "")
    sanitized_filename = sanitized_filename.lstrip().lstrip(".").rstrip(".")
    sanatized_filename = (
        sanitized_filename.replace(" ", "_")
        .replace(".", "_")
        .replace("'", "")
        .replace(",", "")
        .replace("!", "")
        .replace("?", "")
        .replace("_-_", "_")
        .rstrip()
    )
    return sanatized_filename.lower()


def _sanitize_season_episode(season_episode: str) -> str:
    """Sanitizes a season and episode string by removing unwanted characters."""
    sanitized = season_episode.replace(".", "").replace(" ", "").replace("_", "")
    return sanitized


def _should_delete(file_name: str) -> bool:
    """Checks if a file should be deleted based on predefined rules."""
    return any(flag in file_name for flag in FILES_TO_DELETE)
