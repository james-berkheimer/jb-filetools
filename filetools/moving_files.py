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
import shutil
from os import DirEntry
from pathlib import Path

from filetools import CONFIG
from filetools.questions import ask_bool, ask_multichoice, ask_text_input
from filetools.utils import dir_scan, get_show_map, make_shows_map, parse_filename

log = logging.getLogger("filetools")

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Public Functions
# --------------------------------------------------------------------------------


def clean_empty_dirs(working_directory: Path, debug: bool = False) -> None:
    """Delete empty directories within the specified root directory.

    Args:
        working_directory: The root directory to search for empty directories
        debug: If True, run in simulation mode without making actual changes

    Raises:
        OSError: If deletion of a directory fails
    """
    dirs_to_delete = _get_empty_dirs(working_directory)

    if dirs_to_delete:
        log.info("Empty directories found:")
        for dir_to_delete in dirs_to_delete:
            log.info(f"{dir_to_delete}")

        if ask_bool("Delete directories?"):
            for d in dirs_to_delete:
                if not debug:
                    try:
                        log.info(f"Deleting directory: {d}")
                        shutil.rmtree(d)
                    except OSError as e:
                        log.error(f"Error deleting {d}: {e.strerror}")
                else:
                    log.info(f"[Debug] Deleting directory: {d}")
    else:
        log.info("No directories to delete")


def extract_from_src(working_directory: Path, debug: bool = False) -> None:
    """Extract files from source directory to their new locations.

    Args:
        working_directory: The root directory containing files to extract
        debug: If True, run in simulation mode without making actual changes
    """
    try:
        working_directory = Path(working_directory)
        if not working_directory.is_dir():
            log.error(f"Invalid working directory: {working_directory}")
            return

        files_to_extract = _get_files_to_extract(working_directory)
        if not files_to_extract:
            log.info("No files found to extract")
            return

        for src, dest in files_to_extract.items():
            try:
                if debug:
                    log.info(f"[Debug] Would extract: {src} -> {dest}")
                else:
                    log.info(f"Extracting: {src} -> {dest}")
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    _move_file(src, dest)
            except Exception as e:
                log.error(f"Failed to extract {src} to {dest}: {e}")
                continue

    except Exception as e:
        log.error(f"Extraction process failed: {e}")
        log.debug("Error details:", exc_info=True)

    log.info("File extraction process completed")


def move_movie_files(movies: list[Path], working_directory: Path, debug: bool = False) -> None:
    """Move movie files to their respective destination directories.

    Args:
        movies: List of movie file paths to be moved
        working_directory: Directory where movie files are currently located
        debug: If True, run in simulation mode without making actual changes

    Raises:
        FileNotFoundError: If any movie files don't exist in working directory
        OSError: If creating directories or moving files fails
    """
    try:
        working_directory = Path(working_directory)
        if not working_directory.is_dir():
            raise NotADirectoryError(f"Working directory does not exist: {working_directory}")

        files_to_move = {}
        for movie in movies:
            try:
                movie = Path(movie)
                src = working_directory / movie.name

                if not src.exists():
                    log.error(f"Source file not found: {src}")
                    continue

                dest = _build_movie_destination(movie)
                if dest:
                    files_to_move[src] = dest

            except Exception as e:
                log.error(f"Error processing movie {movie}: {e}")
                continue

        if not files_to_move:
            log.warning("No valid movies to move")
            return

        _perform_moves(files_to_move, "movies", debug)

    except Exception as e:
        log.error(f"Failed to move movie files: {e}")
        log.debug("Error details:", exc_info=True)
        raise


def move_show_files(shows: list[Path], working_directory: Path, debug: bool = False) -> None:
    """Moves show files to their respective destination directories.

    Args:
        shows (List[Path]): A list of show file paths to be moved.
        working_directory (Path): The directory where the show files are currently located.

    The function processes each show file path, determines its destination path,
    creates any necessary directories, and then moves the files to their new locations.
    """
    files_to_move = {}
    rejected_shows = set()

    for show in shows:
        src = working_directory.joinpath(show)
        show_name, _ = parse_filename(show.name)

        # Skip if user already declined to add this show
        if show_name in rejected_shows:
            log.info(f"Skipping {show.name} (previously rejected show: {show_name})")
            continue

        dest = _build_show_destination(show)

        if dest:
            files_to_move[src] = dest
        elif show_name:
            rejected_shows.add(show_name)

    _perform_moves(files_to_move, "shows", debug)


# --------------------------------------------------------------------------------
# Private Functions
# --------------------------------------------------------------------------------


def _build_movie_destination(movie_path: Path) -> Path | None:
    """Builds the destination path for a movie file within a selected movie library.

    Args:
        movie_name (str): The name of the movie file.

    Returns:
        Path | None: The destination path for the movie file within the selected library,
                     or None if no valid library is selected or found.
    """
    log.debug(f"Processing movie: {movie_path}")
    library_path = _choose_library(CONFIG.movies, "Select a movie library:")
    filename_without_extension = movie_path.stem
    cleaned_filename = filename_without_extension.replace("-4K", "").replace("-hdr", "")
    log.debug(f"Using library: {library_path}")
    if not library_path:
        log.warning("No valid movie library selected or found.")
        return None

    destination = library_path / cleaned_filename / movie_path.name
    log.debug(f"Destination: {destination}")
    return Path(destination)


def _build_show_destination(show_path: Path) -> Path | None:
    """Constructs the destination path for a given show name.

    This function attempts to parse the season and episode information from the
    provided show name. If successful, it constructs a destination path based on
    a predefined mapping of shows. If the show is not found in the mapping, it
    prompts the user to provide a new show path.

    Args:
        show_name (str): The name of the show, including season and episode information.

    Returns:
        Path | None: The constructed destination path for the show, or None if the
        season/episode information could not be parsed.
    """
    log.info(f"Processing show: {show_path}")
    show_name, season_episode = parse_filename(show_path.name)
    log.debug(f"Show name: {show_name} | Season/Episode: {season_episode}")
    if not season_episode:
        log.warning(f"Could not parse season/episode from {show_name}")
        return None

    base_show_name = show_name.split(season_episode)[0].rstrip("_").lstrip("_")
    season_name = _split_season_episode(season_episode)[0].replace("s", "season_")
    if season_name == "season_00":
        season_name = "specials"

    log.debug(f"Base show name: {base_show_name} | Season name: {season_name}")

    try:
        show_map = get_show_map()
        matched_path = Path(show_map["Shows"][base_show_name])
        destination = matched_path / season_name / show_path.name
        log.debug(f"destination: {destination}")
        return destination

    except KeyError:
        return _prompt_for_new_show(base_show_name, season_name, show_path.name)


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
    """Identify empty directories within a given root directory.

    This function scans the specified root directory and identifies directories
    that can be considered empty based on the absence of certain file types.
    A directory is considered empty if it does not contain any files with
    extensions listed in DO_NOT_DELETE or any video files that are not samples
    or trailers.

    Args:
        working_directory (Path): The root directory to scan for empty directories.

    Returns:
        list: A list of Path objects representing directories that can be deleted.
    """
    dirs_to_delete = []
    for dir_obj in dir_scan(working_directory):
        delete = True
        for file_obj in dir_scan(dir_obj.path, True):
            _, file_ext = os.path.splitext(file_obj.name)
            if file_ext in CONFIG.downloading_indicators:
                delete = False
                break
            if any(x in file_ext for x in CONFIG.valid_extensions):
                if "sample" in file_obj.name.lower() or "trailer" in file_obj.name.lower():
                    continue
                delete = False
        if delete:
            dirs_to_delete.append(working_directory.joinpath(dir_obj.name))
    return dirs_to_delete


def _get_files_to_extract(working_directory: Path) -> dict[Path, Path]:
    """Scans the given root directory and identifies files to be extracted.

    This function recursively scans the root directory and its subdirectories,
    identifying files that are ready to be extracted. It skips directories
    that should not be processed and handles files that are still downloading.

    Args:
        working_directory (Path): The root directory to scan for files to extract.

    Returns:
        dict: A dictionary where the keys are the original file paths and the
              values are the new paths for the files to be extracted.

    Raises:
        Exception: If an error occurs during the directory scanning or file processing.
    """
    files_to_extract = {}

    try:
        working_directory = Path(working_directory)
        for dir_obj in dir_scan(working_directory):
            if _should_skip_directory(dir_obj):
                continue

            tmpdict = {}
            still_downloading = False

            try:
                for file_obj in dir_scan(dir_obj.path, True):
                    try:
                        log.debug(f"Processing file: {file_obj.name}")
                        new_path, still_downloading = _process_file(file_obj, working_directory)
                        log.debug(f"File {file_obj.name} processed: Is downloading? {still_downloading}")
                        if still_downloading:
                            break
                        if new_path:
                            log.debug(f"\tAdding file to extraction list: {file_obj.path} -> {new_path}")
                            tmpdict[Path(file_obj.path)] = Path(new_path)
                    except Exception as e:
                        log.error(f"Error processing file {file_obj.name}: {e}")
                        continue

                if not still_downloading:
                    files_to_extract.update(tmpdict)
            except Exception as e:
                log.error(f"Error scanning directory {dir_obj.path}: {e}")
                continue

    except Exception as e:
        log.error(f"An error occurred while getting files to extract: {e}")
        log.debug("Error details:", exc_info=True)

    return files_to_extract


def _move_file(src: Path, dest: Path) -> float:
    """Move a file reliably across filesystems and return elapsed time in seconds.

    Attempts multiple methods in order of preference:
    1. os.rename() (fastest, same filesystem)
    2. sendfile() (zero-copy, Linux-only)
    3. shutil.copyfile() + unlink() (fallback)

    Args:
        src: Source file path
        dest: Destination file path

    Returns:
        float: Time taken to perform the move in seconds

    Raises:
        OSError: If all move attempts fail
    """
    import time

    start = time.perf_counter()

    try:
        os.rename(src, dest)
        log.debug(f"Moved {src} -> {dest} using os.rename")
        return time.perf_counter() - start
    except OSError as e:
        if e.errno != errno.EXDEV:
            log.error(f"Failed to move {src} -> {dest}: {e}")
            raise

    try:
        with open(src, "rb") as fsrc, open(dest, "wb") as fdst:
            os.sendfile(fdst.fileno(), fsrc.fileno(), 0, os.stat(src).st_size)
        os.unlink(src)
        log.debug(f"Moved {src} -> {dest} using sendfile()")
        return time.perf_counter() - start
    except OSError as e:
        log.error(f"Failed to move {src} -> {dest} using sendfile(): {e}")

    try:
        shutil.copyfile(src, dest)
        os.unlink(src)
        log.debug(f"Moved {src} -> {dest} using shutil.copyfile() + unlink()")
        return time.perf_counter() - start
    except OSError as e:
        log.error(f"Failed to move {src} -> {dest} using shutil.copyfile() + unlink(): {e}")
        raise


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
    for _, dest in files_to_move.items():
        log.info(f"{dest}")

    if ask_bool(f"Do you want to move these {media_type}?"):
        for src, dest in files_to_move.items():
            log.debug(f"Creating directory: {dest.parent}")
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists():
                log.info(f"File already exists: {dest}, skipping...")
            else:
                try:
                    if not debug:
                        log.info(f"Moving: {src} -> {dest}")
                        elapsed = _move_file(src, dest)
                        log.info(f"Moved in {elapsed:.3f} seconds")
                    else:
                        log.info(f"[Debug] Moving: {src} -> {dest}")
                except Exception as e:
                    log.error(f"Failed to move {src} to {dest}: {e}")


def _process_file(file_obj: DirEntry, working_directory: Path) -> tuple[Path | None, bool]:
    """Process a single file to determine if it should be extracted."""
    filename = file_obj.name

    try:
        if any(ind in filename for ind in CONFIG.downloading_indicators):
            log.debug(f"\tFile {filename} is still downloading.")
            return None, True

        _, ext = os.path.splitext(filename)

        if ext not in CONFIG.valid_extensions:
            log.debug(f"\tFile {filename} does not match valid extensions.")
            return None, False

        if ext in CONFIG.excluded_extensions:
            log.debug(f"\tFile {filename} is excluded from processing.")
            return None, False

        if any(keyword in filename.lower() for keyword in CONFIG.ignore_keywords):
            log.debug(f"\tFile {filename} matches ignore keywords.")
            return None, False

        log.debug(f"\tFile {filename} is valid for processing.")
        return working_directory / filename, False

    except AttributeError as e:
        log.error(f"Invalid file object for {filename}: {e}")
        return None, False
    except Exception as e:
        log.error(f"Error processing file {filename}: {e}")
        return None, False


def _prompt_for_new_show(show_name: str, season_name: str, filename: str) -> Path | None:
    """If the show isn't in shows_map.ini, asks user whether to add it.
    Prompts for library type (Television/Documentaries), network, etc.
    Returns the newly created path or None if user declines.
    """
    log.warning(f"Show '{show_name}' does not exist.")
    if not ask_bool(f"Do you want to add '{show_name}'?"):
        return None

    choice = ask_multichoice(["Television", "Documentaries"])
    show_libraries = CONFIG.shows
    if choice in show_libraries:
        base_library_path = Path(show_libraries[choice])
    else:
        log.warning(f"{choice} not found in SHOW_LIBRARIES, defaulting to /media/Television.")
        base_library_path = Path("/media/Television")

    show_network = ask_text_input("Please enter the network the show is on (e.g., 'HBO', 'BBC'):")

    new_show_dir = base_library_path.joinpath(show_network, show_name, season_name)
    log.info(f"Making new show directory: {new_show_dir}")
    os.makedirs(new_show_dir, exist_ok=True)

    make_shows_map()

    return new_show_dir.joinpath(filename)


def _split_season_episode(season_episode: str) -> tuple[str, str]:
    """Splits a season and episode string into separate components.

    Args:
        season_episode (list): A list containing a single string in the format "SxxExx",
                               where "Sxx" represents the season and "Exx" represents the episode.

    Returns:
        tuple: A tuple containing the season as a string and the episode as a string.
    """
    season_episode = season_episode.lstrip("_").rstrip("_")
    split = season_episode.split("e")
    season = split[0]
    episode = f"e{split[1]}"
    return season, episode


def _should_skip_directory(dir_obj: DirEntry) -> bool:
    """Determines whether a directory should be skipped based on its name.

    Args:
        dir_obj (DirEntry): A DirEntry object representing a directory to check.

    Returns:
        bool: True if the directory's name is "_in-progress", indicating it should be skipped; False otherwise.
    """
    return dir_obj.name == "_in-progress"
