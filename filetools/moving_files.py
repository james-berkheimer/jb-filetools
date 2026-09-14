#!/usr/local/bin/python3
#
# moving_files.py
#

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------
import errno
import logging
import os
import re
import shutil
import time
from os import DirEntry
from pathlib import Path

from filetools import CONFIG
from filetools.questions import ask_bool, ask_multichoice, ask_text_input
from filetools.show_matching import ShowCatalog, normalize_show_name
from filetools.utils import dir_scan, get_show_map, parse_filename, should_exclude

log = logging.getLogger("filetools")

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------
IN_PROGRESS_DIR = "_in-progress"
SPECIALS_DIR = "specials"
_SEASON_DIR = re.compile(r"season[\s_]*(\d+)", re.I)

# --------------------------------------------------------------------------------
# Public Functions
# --------------------------------------------------------------------------------


def clean_empty_dirs(working_directory: Path, debug: bool = False) -> None:
    """Delete empty directories within the specified root directory.

    Args:
        working_directory: The root directory to search for empty directories
        debug: If True, run in simulation mode without making actual changes
    """
    dirs_to_delete = _get_empty_dirs(working_directory)

    if not dirs_to_delete:
        log.info("No directories to delete")
        return

    log.info("Empty directories found:")
    for dir_to_delete in dirs_to_delete:
        log.info(f"{dir_to_delete}")

    if not ask_bool("Delete directories?"):
        return

    for d in dirs_to_delete:
        if debug:
            log.info(f"[Debug] Deleting directory: {d}")
            continue
        try:
            log.info(f"Deleting directory: {d}")
            shutil.rmtree(d)
        except OSError as e:
            log.error(f"Error deleting {d}: {e.strerror}")


def delete_malware(working_directory: Path, debug: bool = False) -> list[Path]:
    """Delete executables and fake archives disguised as downloads, at any depth.

    Indexers regularly serve fake episodes whose payload is "Show.S01E01.mkv.exe" or a
    ".zipx" archive. These are never media, so they are removed without asking every
    time filetools runs. Transmission's in-progress folder is left alone.

    Args:
        working_directory: The download directory to sweep
        debug: If True, only report what would be deleted

    Returns:
        list[Path]: The files deleted (or, in debug mode, that would be deleted)
    """
    working_directory = Path(working_directory)
    malware = [
        path
        for path in _walk_files(working_directory)
        if path.relative_to(working_directory).parts[0] != IN_PROGRESS_DIR and _is_malware(path)
    ]
    if not malware:
        log.debug("No malware found")
        return []

    log.warning(f"Found {len(malware)} malware file(s) disguised as downloads:")
    for path in malware:
        if debug:
            log.info(f"[Debug] Would delete malware: {path}")
            continue
        try:
            path.unlink()
            log.warning(f"Deleted malware: {path}")
        except OSError as e:
            log.error(f"Failed to delete malware {path}: {e}")
    return malware


def extract_from_src(working_directory: Path, debug: bool = False) -> None:
    """Move finished videos out of downloaded folders, at any depth, into the working directory.

    Args:
        working_directory: The root directory containing files to extract
        debug: If True, run in simulation mode without making actual changes
    """
    working_directory = Path(working_directory)
    if not working_directory.is_dir():
        log.error(f"Invalid working directory: {working_directory}")
        return

    files_to_extract = _get_files_to_extract(working_directory)
    if not files_to_extract:
        log.info("No files found to extract")
        return

    for src, dest in files_to_extract.items():
        if debug:
            log.info(f"[Debug] Would extract: {src} -> {dest}")
            continue
        if dest.exists():
            log.warning(f"Not extracting {src}: {dest} already exists")
            continue
        try:
            log.info(f"Extracting: {src} -> {dest}")
            _move_file(src, dest)
        except OSError as e:
            log.error(f"Failed to extract {src} to {dest}: {e}")

    log.info("File extraction process completed")


def move_movie_files(movies: list[Path], working_directory: Path, debug: bool = False) -> None:
    """Move movie files to their respective destination directories.

    Args:
        movies: List of movie file paths to be moved
        working_directory: Directory where movie files are currently located
        debug: If True, run in simulation mode without making actual changes

    Raises:
        NotADirectoryError: If the working directory does not exist
    """
    working_directory = Path(working_directory)
    if not working_directory.is_dir():
        raise NotADirectoryError(f"Working directory does not exist: {working_directory}")

    files_to_move = {}
    for movie in movies:
        src = working_directory / Path(movie).name
        if not src.exists():
            log.error(f"Source file not found: {src}")
            continue

        dest = _build_movie_destination(Path(movie))
        if dest:
            files_to_move[src] = dest

    if not files_to_move:
        log.info("No movies to move")
        return

    _perform_moves(files_to_move, "movies", debug)


def move_show_files(shows: list[Path], working_directory: Path, debug: bool = False) -> None:
    """Move show files into their show and season folders in the library.

    Each show is resolved once per run, so the user is asked at most one question
    per show rather than one per episode.

    Args:
        shows: Show file paths to be moved
        working_directory: The directory where the show files are currently located
        debug: If True, run in simulation mode without making actual changes
    """
    if not shows:
        return

    catalog = ShowCatalog(get_show_map()["Shows"])
    show_dirs: dict[str, Path | None] = {}
    files_to_move = {}

    for show in shows:
        log.info(f"Processing show: {show}")
        show_name, season_episode = parse_filename(show.name)
        if not show_name or not season_episode:
            log.warning(f"Could not parse show name and season/episode from {show.name}")
            continue

        key = normalize_show_name(show_name)
        if key not in show_dirs:
            show_dirs[key] = _resolve_show_dir(show_name, catalog)
        show_dir = show_dirs[key]
        if show_dir is None:
            log.info(f"Skipping {show.name} (no library folder chosen for {show_name})")
            continue

        season_number = int(re.match(r"s(\d+)", season_episode).group(1))
        dest = show_dir / _season_dir_name(show_dir, season_number) / show.name
        log.debug(f"destination: {dest}")
        files_to_move[working_directory / show.name] = dest

    _perform_moves(files_to_move, "shows", debug)


# --------------------------------------------------------------------------------
# Private Functions
# --------------------------------------------------------------------------------


def _build_movie_destination(movie_path: Path) -> Path | None:
    """Builds the destination path for a movie file within a selected movie library.

    Args:
        movie_path: Path of the movie file.

    Returns:
        Path | None: The destination path for the movie file within the selected library,
                     or None if no valid library is selected or found.
    """
    log.debug(f"Processing movie: {movie_path}")
    library_path = _choose_library(CONFIG.movies, "Select a movie library:")
    cleaned_filename = movie_path.stem.replace("-4K", "").replace("-hdr", "")
    log.debug(f"Using library: {library_path}")
    if not library_path:
        log.warning("No valid movie library selected or found.")
        return None

    destination = library_path / cleaned_filename / movie_path.name
    log.debug(f"Destination: {destination}")
    return destination


def _choose_library(library_dict: dict[str, str], prompt: str) -> Path | None:
    """Selects a library from a dictionary of library names and their corresponding paths.

    Args:
        library_dict (dict[str, str]): A dictionary where keys are library names and values are their paths.
        prompt (str): A prompt message to display when asking the user to choose a library.

    Returns:
        Path | None: The path of the selected library as a Path object, or None if the dictionary is empty.
    """
    if not library_dict:
        return None

    library_names = list(library_dict.keys())
    if len(library_names) > 1:
        choice = ask_multichoice(library_names, prompt)
        return Path(library_dict[choice])
    return Path(library_dict[library_names[0]])


def _get_empty_dirs(working_directory: Path) -> list[Path]:
    """Identify downloaded folders that no longer hold anything worth keeping.

    A folder is kept if anything beneath it, at any depth, is still downloading or is
    a video that isn't a sample or trailer. Season packs ("Show/Season 01/...") are
    therefore kept until their episodes have been extracted.

    Args:
        working_directory (Path): The root directory to scan for empty directories.

    Returns:
        list: A list of Path objects representing directories that can be deleted.
    """
    dirs_to_delete = []
    for dir_obj in dir_scan(working_directory):
        if _should_skip_directory(dir_obj):
            continue
        dir_path = Path(dir_obj.path)
        if not any(
            _is_downloading(f) or _is_extractable(f.relative_to(dir_path)) for f in _walk_files(dir_path)
        ):
            dirs_to_delete.append(dir_path)
    return dirs_to_delete


def _get_files_to_extract(working_directory: Path) -> dict[Path, Path]:
    """Find finished videos inside downloaded folders, at any depth.

    A folder is skipped entirely while anything in it is still downloading. Videos
    are flattened into the working directory; if two would end up with the same
    name, the second is left in place with a warning rather than overwriting.

    Args:
        working_directory (Path): The root directory to scan for files to extract.

    Returns:
        dict: Original file paths mapped to their new paths in the working directory.
    """
    files_to_extract: dict[Path, Path] = {}
    claimed: set[Path] = set()

    for dir_obj in dir_scan(working_directory):
        if _should_skip_directory(dir_obj):
            continue

        dir_path = Path(dir_obj.path)
        files = _walk_files(dir_path)
        if any(_is_downloading(f) for f in files):
            log.debug(f"Skipping {dir_obj.name}: still downloading")
            continue

        for file_path in files:
            if not _is_extractable(file_path.relative_to(dir_path)):
                log.debug(f"\tNot extracting: {file_path}")
                continue
            dest = working_directory / file_path.name
            if dest in claimed or dest.exists():
                log.warning(
                    f"Not extracting {file_path}: {dest.name} already exists in {working_directory}"
                )
                continue
            log.debug(f"\tAdding file to extraction list: {file_path} -> {dest}")
            files_to_extract[file_path] = dest
            claimed.add(dest)

    return files_to_extract


def _is_downloading(file_path: Path) -> bool:
    """True for partial downloads, e.g. "episode.mkv.part" (but not "The.Party.1968.mkv")."""
    name = file_path.name.lower()
    return any(name.endswith(indicator) for indicator in CONFIG.downloading_indicators)


def _is_extractable(relative_path: Path) -> bool:
    """True for a finished video that isn't a sample, trailer or preview.

    Args:
        relative_path: Path of the file relative to its download folder, so that
            "Sample/show.mkv" is recognised as a sample by its folder name.
    """
    if relative_path.suffix.lower() not in CONFIG.valid_extensions:
        return False
    if should_exclude(relative_path.name, CONFIG.excluded_extensions):
        return False
    parts = [part.lower() for part in relative_path.parts]
    return not any(keyword in part for part in parts for keyword in CONFIG.ignore_keywords)


def _is_malware(file_path: Path) -> bool:
    """True for executables and fake archives, e.g. "Show.S01E01.1080p.mkv.exe"."""
    return file_path.name.lower().endswith(tuple(CONFIG.malware_extensions))


def _library_label(show_dir: Path) -> str:
    """Short, unambiguous label for a show folder, e.g. "television/bbc/ludwig"."""
    return "/".join(show_dir.parts[-3:])


def _move_file(src: Path, dest: Path) -> float:
    """Move a file, copying it when source and destination are on different filesystems.

    The source is only removed once the copy is known to be complete.

    Args:
        src: Source file path
        dest: Destination file path

    Returns:
        float: Time taken to perform the move in seconds

    Raises:
        OSError: If the move fails
    """
    start = time.perf_counter()

    try:
        os.rename(src, dest)
        log.debug(f"Moved {src} -> {dest} using os.rename")
        return time.perf_counter() - start
    except OSError as e:
        if e.errno != errno.EXDEV:
            raise

    # copyfile() uses sendfile() on Linux and loops until the whole file is copied.
    shutil.copyfile(src, dest)
    if os.path.getsize(dest) != os.path.getsize(src):
        os.unlink(dest)
        raise OSError(f"Incomplete copy of {src} to {dest}")
    os.unlink(src)
    log.debug(f"Moved {src} -> {dest} using shutil.copyfile() + unlink()")
    return time.perf_counter() - start


def _perform_moves(files_to_move: dict[Path, Path], media_type: str, debug: bool = False) -> None:
    """Move files from source to destination paths.

    Args:
        files_to_move: Dictionary mapping source paths to destination paths
        media_type: Type of media being moved (e.g., "movies", "shows")
        debug: If True, run in simulation mode without making actual changes
    """
    if not files_to_move:
        return

    log.info(f"\nThe following {media_type} will be moved:")
    for dest in files_to_move.values():
        log.info(f"{dest}")

    if not ask_bool(f"Do you want to move these {media_type}?"):
        return

    for src, dest in files_to_move.items():
        if dest.exists():
            log.info(f"File already exists: {dest}, skipping...")
            continue
        if debug:
            log.info(f"[Debug] Moving: {src} -> {dest}")
            continue
        try:
            log.debug(f"Creating directory: {dest.parent}")
            dest.parent.mkdir(parents=True, exist_ok=True)
            log.info(f"Moving: {src} -> {dest}")
            elapsed = _move_file(src, dest)
            log.info(f"Moved in {elapsed:.3f} seconds")
        except OSError as e:
            log.error(f"Failed to move {src} to {dest}: {e}")


def _prompt_for_new_show(show_name: str) -> Path | None:
    """Ask which library and network a new show belongs to.

    Nothing is created here; the folder is made when the first episode is moved,
    so declining the final move leaves no empty folders behind.

    Returns:
        Path | None: The new show folder, or None if no show library is configured.
    """
    library_path = _choose_library(CONFIG.shows, f"Which library does '{show_name}' belong in?")
    if not library_path:
        log.error("No show libraries are configured.")
        return None

    while True:
        network = ask_text_input("Please enter the network the show is on (e.g., 'HBO', 'BBC')")
        if not network:
            log.warning("A network is required.")
            continue
        if (library_path / network).is_dir() or ask_bool(
            f"'{network}' is a new network folder in {library_path}. Create it?"
        ):
            break

    new_show_dir = library_path / network / show_name
    log.info(f"New show folder: {new_show_dir}")
    return new_show_dir


def _resolve_show_dir(show_name: str, catalog: ShowCatalog) -> Path | None:
    """Find or choose the library folder for a show, asking the user when unsure.

    Returns:
        Path | None: The show folder, or None if the user chose to skip the show.
    """
    match = catalog.match(show_name)
    if match.path:
        if normalize_show_name(match.path.name) != normalize_show_name(show_name):
            log.info(f"Matched '{show_name}' to existing show {_library_label(match.path)}")
        return match.path

    log.warning(f"Show '{show_name}' is not in the library.")
    if match.candidates:
        add_option, skip_option = f"Add '{show_name}' as a new show", "Skip"
        existing = {_library_label(path): path for path in match.candidates}
        choice = ask_multichoice([*existing, add_option, skip_option], f"Where should '{show_name}' go?")
        if choice in existing:
            return existing[choice]
        if choice == skip_option:
            return None
    elif not ask_bool(f"Do you want to add '{show_name}'?"):
        return None

    new_show_dir = _prompt_for_new_show(show_name)
    if new_show_dir:
        catalog.add(new_show_dir.name, new_show_dir)
    return new_show_dir


def _season_dir_name(show_dir: Path, season_number: int) -> str:
    """Name of the season folder to use, reusing an existing folder if there is one.

    The library contains "season_01", "season 01" and "season_1" styles; reusing
    whichever already exists keeps a season's episodes together.
    """
    canonical = SPECIALS_DIR if season_number == 0 else f"season_{season_number:02}"
    if not show_dir.is_dir() or (show_dir / canonical).is_dir():
        return canonical

    for entry in dir_scan(show_dir):
        if season_number == 0 and entry.name.lower() == SPECIALS_DIR:
            return entry.name
        match = _SEASON_DIR.fullmatch(entry.name)
        if match and int(match.group(1)) == season_number:
            return entry.name
    return canonical


def _should_skip_directory(dir_obj: DirEntry) -> bool:
    """Determines whether a directory should be skipped based on its name.

    Args:
        dir_obj (DirEntry): A DirEntry object representing a directory to check.

    Returns:
        bool: True if the directory is Transmission's in-progress folder; False otherwise.
    """
    return dir_obj.name == IN_PROGRESS_DIR


def _walk_files(directory: Path) -> list[Path]:
    """Every file beneath a directory, at any depth, in a stable order."""
    files = []
    for root, dirs, names in os.walk(directory):
        dirs.sort()
        files.extend(Path(root, name) for name in sorted(names))
    return files
