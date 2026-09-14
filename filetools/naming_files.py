import logging
import os
import re
import traceback
from pathlib import Path

from filetools import CONFIG
from filetools.utils import dir_scan, parse_filename

log = logging.getLogger("filetools")

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------

# Release tags that mark a file as 4K or HDR. Matched as whole tokens, so "HDRip"
# (a rip source, not HDR) and titles that merely contain these letters don't count.
UHD_TAGS = {"2160p", "4k", "uhd"}
HDR_TAGS = {"hdr", "hdr10", "hdr10+", "hdr10plus", "dv", "dovi"}

# Torrent-site prefixes such as "www.Example.org - " or "[ www.Example.org ] ".
_SITE_PREFIX = re.compile(r"^\s*\[?\s*www\.[^\s\]]+\s*\]?\s*-?\s*", re.I)

_NAME_WORD = r"(?:[a-z0-9]+|\(\d{4}\))"
_SHOW_PATTERN = re.compile(
    rf"""^
    {_NAME_WORD}(?:_{_NAME_WORD})*  # Words separated by single underscores; "(2022)" allowed
    _                               # Single underscore before season/episode
    s\d{{2,4}}e\d{{2,3}}            # Season and starting episode
    (?:-e\d{{2,3}})?                # Optional ending episode (multi-episode support)
    (?:_\[[a-z0-9_]+\])?            # Optional quality flags with leading underscore
    \.[a-z0-9]+                     # File extension
    $""",
    re.VERBOSE,
)
_MOVIE_PATTERN = re.compile(
    r"""^
    [a-z0-9]+(?:-[a-z0-9]+)*        # First word; hyphens allowed ("spider-man")
    (?:_[a-z0-9]+(?:-[a-z0-9]+)*)*  # Additional words, each preceded by single underscore
    _\(\d{4}\)                      # Year in parentheses with underscore before
    (?:-4K)?(?:-hdr)?               # Optional quality flags
    \.[a-z0-9]+                     # File extension
    $""",
    re.VERBOSE,
)

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
        if _should_delete(file_obj.name):
            if debug:
                log.info(f"[Debug] Deleting.....{file_obj.name}")
            else:
                log.info(f"Deleting.....{file_obj.name}")
                os.remove(file_obj.path)
            continue

        file_ext = os.path.splitext(file_obj.name)[1].lower()
        if file_ext in CONFIG.valid_extensions and file_ext not in CONFIG.excluded_extensions:
            try:
                _rename(file_obj, debug)
            except Exception as e:
                log.error(f"Failed to rename {file_obj.name}: {e}\n{traceback.format_exc()}")


# --------------------------------------------------------------------------------
# Private Functions
# --------------------------------------------------------------------------------


def _detect_flags(name: str) -> tuple[bool, bool]:
    """Detect 4K and HDR release tags in a filename.

    Returns:
        tuple[bool, bool]: (is_4k, is_hdr)
    """
    tokens = set(re.split(r"[^a-z0-9+]+", name.lower()))
    return bool(tokens & UHD_TAGS), bool(tokens & HDR_TAGS)


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
        str: Formatted filename in the pattern: movie_name_(year)-4K-hdr.ext
    """
    is_4k, is_hdr = _detect_flags(filename_wo_ext)
    fk = "-4K" if is_4k else ""
    hdr = "-hdr" if is_hdr else ""

    if "." in filename_wo_ext:
        filename_wo_ext = "_".join(filename_wo_ext.split(".")).lower()
    filename_wo_ext = filename_wo_ext.replace(" (", "_").replace(" ", "_").replace("'", "").lower()
    year = _get_year(filename_wo_ext)
    if year:
        # Everything before the year is the title. Drop any "(" or separators left
        # over from an existing "(year)" so re-running never produces "((year)".
        title = filename_wo_ext[: filename_wo_ext.rfind(year)]
        title = re.sub(r"_+", "_", title.replace("_-_", "_")).rstrip("_-.([ ")
        return f"{title}_({year}){fk}{hdr}{file_ext}" if title else f"({year}){fk}{hdr}{file_ext}"

    log.warning(f"Failed to rename {filename_wo_ext}: No valid year found.")
    return filename_wo_ext + file_ext


def _get_year(target_string: str) -> str | None:
    """Extract the most recent 4-digit year from a string.

    Args:
        target_string: String to search for year

    Returns:
        str | None: Most recent valid year between year_min and year_max, or None if not found
    """
    matches = re.findall(r"[0-9]{4}", target_string)
    filtered_matches = [m for m in matches if CONFIG.year_min <= int(m) <= CONFIG.year_max]
    return filtered_matches[-1] if filtered_matches else None


def _has_cleanup_flag(name: str) -> bool:
    """True if the name contains a broadcaster tag (e.g. 'bbc') as a whole word."""
    return any(_cleanup_flag_pattern(flag).search(name) for flag in CONFIG.name_cleanup_flags)


def _cleanup_flag_pattern(flag: str) -> re.Pattern:
    """Match a cleanup flag only as a whole word, so 'itv' doesn't match 'hitvideo'."""
    return re.compile(rf"(?<![a-z0-9]){re.escape(flag.lower())}(?![a-z0-9])", re.I)


def _is_properly_formatted(file_name: str) -> bool:
    """Check if filename matches movie or TV show naming conventions and contains no illegal words.

    Args:
        file_name: Name of file to check

    Returns:
        bool: True if filename matches either movie or show pattern and contains no illegal words

    Examples of valid show names:
        - show_name_s01e01.mkv
        - multiple_word_show_name_s01e01.mkv
        - show_name_s01e01_[4k_hdr].mkv
        - show_name_s00e201.mkv
        - 1923_(2022)_s01e01.mkv

    Examples of valid movie names:
        - movie_name_(2023).mkv
        - spider-man_(2002)-4K-hdr.mkv

    Invalid examples:
        - pbs_show_name_s01e01.mkv (contains illegal word 'pbs')
        - bbc.show.name.s01e01.mkv (contains illegal word 'bbc')
        - show.name.s01e01.mkv (uses periods instead of underscores)
        - show_name_101.mkv (incorrect season/episode format)
    """
    if _has_cleanup_flag(file_name):
        return False
    return bool(_MOVIE_PATTERN.match(file_name) or _SHOW_PATTERN.match(file_name))


def _rename(file_obj: os.DirEntry | Path, debug: bool = False) -> None:
    """Rename a file using standardized naming conventions.

    Args:
        file_obj: File object to rename
        debug: If True, run in simulation mode without making actual changes

    Raises:
        OSError: If rename operation fails
    """
    if _is_properly_formatted(file_obj.name):
        log.info(f"Skipping.....{file_obj.name} (already properly formatted)")
        return

    new_name = _target_name(file_obj.name)
    if new_name == file_obj.name:
        return

    new_name_path = Path(file_obj.path).parent / new_name
    if new_name_path.exists():
        log.warning(f"Not renaming {file_obj.name}: {new_name} already exists")
        return

    if debug:
        log.info(f"[Debug] Renaming.....{file_obj.name} -> {new_name}")
    else:
        log.info(f"Renaming.....{file_obj.name} -> {new_name}")
        os.rename(file_obj.path, new_name_path)


def _sanitize_show_name(show_name: str) -> str:
    """Clean up show name by removing unwanted words and special characters.

    Args:
        show_name: Original show name

    Returns:
        str: Sanitized show name in lowercase with single underscores only
    """
    log.debug(f"\tshow_name: {show_name}")
    sanitized_filename = show_name
    # First remove broadcaster tags, as whole words only
    for word in CONFIG.name_cleanup_flags:
        sanitized_filename = _cleanup_flag_pattern(word).sub("", sanitized_filename)

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


def _target_name(file_name: str) -> str:
    """Compute the standardized name for a file (without touching the filesystem).

    Args:
        file_name: Current file name, including extension

    Returns:
        str: The standardized file name
    """
    filename_wo_ext, file_ext = os.path.splitext(file_name.lower())
    filename_wo_ext = _SITE_PREFIX.sub("", filename_wo_ext)
    show_name, season_episode = parse_filename(filename_wo_ext)

    if show_name and season_episode:
        is_4k, is_hdr = _detect_flags(filename_wo_ext)
        flags = [flag for flag, present in (("4K", is_4k), ("hdr", is_hdr)) if present]
        flags_name = f"_[{'_'.join(flags)}]" if flags else ""
        return _format_tv_show_name(
            _sanitize_show_name(show_name),
            _sanitize_season_episode(season_episode),
            flags_name,
            file_ext,
        )

    return _format_movie_name(filename_wo_ext, file_ext)
