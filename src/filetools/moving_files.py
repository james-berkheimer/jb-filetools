#!/usr/local/bin/python3
#
# moving_files.py
#

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------

import os
import shutil
from pathlib import Path

from . import CONFIG
from .logging import setup_logger
from .questions import ask_bool, ask_multichoice, ask_text_input
from .utils import dir_scan, get_season_episode, get_show_map, make_shows_map

log = setup_logger(__name__)

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------
DO_NOT_DELETE = CONFIG.do_not_delete
FILE_EXCLUDES = CONFIG.file_excludes
FILE_IGNORES = CONFIG.file_ignores
FILES_TO_DELETE = CONFIG.files_to_delete
VIDEO_FILE_EXTENSIONS = CONFIG.video_file_extensions

MOVIE_LIBRARIES = CONFIG.movies
SHOW_LIBRARIES = CONFIG.shows
MUSIC_LIBRARIES = CONFIG.music

# --------------------------------------------------------------------------------
# Public Functions
# --------------------------------------------------------------------------------


def clean_empty_dirs(working_directory: Path):
    """
    Recursively finds and deletes empty directories within the specified root directory.

    Args:
        working_directory (Path): The root directory to search for empty directories.

    Logs:
        - Lists all empty directories found.
        - Asks the user for confirmation before deleting directories.
        - Logs each directory deletion attempt and any errors encountered.

    Raises:
        OSError: If an error occurs while attempting to delete a directory.
    """
    dirs_to_delete = _get_empty_dirs(working_directory)

    if dirs_to_delete:
        log.info("Empty directories found:")
        for dir_to_delete in dirs_to_delete:
            log.info(f"{dir_to_delete}")

        if ask_bool("Delete directories?"):
            for d in dirs_to_delete:
                log.info(f"Deleting directory: {d}")
                try:
                    shutil.rmtree(d)
                except OSError as e:
                    log.error(f"Error deleting {d}: {e.strerror}")
    else:
        log.info("No directories to delete")


def extract_from_src(working_directory: Path):
    """
    Extracts files from the source directory to their new locations.

    This function retrieves a list of files to be moved from the source directory
    specified by `working_directory` and moves each file to its new location. It logs the
    progress of the extraction process, including any errors encountered during
    the file moves.

    Args:
        working_directory (Path): The root directory containing the files to be extracted.

    Raises:
        Exception: If an error occurs while moving a file, it is logged but not re-raised.
    """
    files_to_extract = _get_files_to_extract(working_directory)

    log.info("----------- Starting file extraction process -----------")
    for old_path, new_path in files_to_extract.items():
        try:
            log.info(f"Ex_get_files_to_extracttracting {old_path} to {new_path}")
            shutil.move(old_path, new_path)
        except Exception as e:
            log.error(f"Failed to move {old_path} to {new_path}: {e}")

    log.info("File extraction process completed")


def move_movie_files(movies: list[str], working_directory: Path):
    """
    Moves movie files from the working directory to their respective destinations.

    This function takes a list of movie filenames and a working directory path,
    then moves each movie file to its designated destination. If the destination
    directory does not exist, it will be created.

    Args:
        movies (list[str]): A list of movie filenames to be moved.
        working_directory (Path): The path to the working directory where the
                                  movie files are currently located.

    Raises:
        FileNotFoundError: If any of the movie files do not exist in the working directory.
        OSError: If there is an error creating directories or moving files.
    """
    files_to_move = {}
    directories_to_create = []

    for movie in movies:
        src = working_directory.joinpath(movie)
        dest = _build_movie_destination(movie)
        if dest:
            if not dest.parent.exists():
                directories_to_create.append(dest.parent)
            files_to_move[src] = dest

    _create_missing_directories(directories_to_create)
    _perform_moves(files_to_move)


def move_show_files(shows: list[str], working_directory: Path):
    """
    Moves show files to their respective destination directories.

    Args:
        shows (list[str]): A list of show filenames to be moved.
        working_directory (Path): The directory where the show files are currently located.

    The function processes each show filename, determines its destination path,
    creates any necessary directories, and then moves the files to their new locations.
    """
    files_to_move = {}
    directories_to_create = []

    for show_filename in shows:
        src = working_directory.joinpath(show_filename)
        dest = _build_show_destination(show_filename)
        if dest:
            if not dest.parent.exists():
                directories_to_create.append(dest.parent)
            files_to_move[src] = dest

    _create_missing_directories(directories_to_create)
    _perform_moves(files_to_move)


# --------------------------------------------------------------------------------
# Private Functions
# --------------------------------------------------------------------------------


def _build_movie_destination(movie_name: str) -> Path | None:
    """
    Builds the destination path for a movie file within a selected movie library.

    Args:
        movie_name (str): The name of the movie file.

    Returns:
        Path | None: The destination path for the movie file within the selected library,
                     or None if no valid library is selected or found.
    """
    library_path = _choose_library(MOVIE_LIBRARIES, "Select a movie library:")
    if not library_path:
        log.warning("No valid movie library selected or found.")
        return None

    filename_wo_ext, _ = os.path.splitext(movie_name)
    filename_wo_ext = filename_wo_ext.replace("-4k-hdr", "")
    return Path(library_path).joinpath(filename_wo_ext, movie_name)


def _build_show_destination(show_name: str) -> Path | None:
    """
    Constructs the destination path for a given show name.

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
    season_episode, _ = get_season_episode(show_name)
    if not season_episode:
        log.warning(f"Could not parse season/episode from {show_name}")
        return None

    base_show_name = show_name.split(season_episode[0])[0].rstrip("_")
    season_name = _split_season_episode(season_episode)[0].replace("s", "season_")
    if season_name == "season_00":
        season_name = "specials"

    try:
        # 1. Check shows_map.ini
        show_map = get_show_map()
        matched_path = Path(show_map["Shows"][base_show_name])
        return matched_path.joinpath(season_name, show_name)

    except KeyError:
        # 2. If show not found, prompt user
        return _prompt_for_new_show(base_show_name, season_name, show_name)


def _choose_library(library_dict: dict[str, str], prompt: str) -> str | None:
    """
    Selects a library from a dictionary of library names and their corresponding paths.

    Args:
        library_dict (dict[str, str]): A dictionary where keys are library names and values are their paths.
        prompt (str): A prompt message to display when asking the user to choose a library.

    Returns:
        str | None: The path of the selected library, or None if the dictionary is empty.
    """
    if not library_dict:
        return None

    library_names = list(library_dict.keys())
    if len(library_names) > 1:
        choice = ask_multichoice(library_names, prompt)
        return library_dict[choice]
    else:
        return library_dict[library_names[0]]


def _create_missing_directories(dir_list: list[Path]):
    """
    Create missing directories from a list of directory paths.

    This function takes a list of directory paths, removes duplicates, and prompts the user
    to confirm if they want to create the missing directories. If the user confirms, it creates
    the directories that do not already exist.

    Args:
        dir_list (list[Path]): A list of directory paths to be created if missing.

    Returns:
        None
    """
    unique_dirs = list(set(dir_list))
    if not unique_dirs:
        return

    print("Directories to create:")
    for d in unique_dirs:
        print(f"   {d}")

    if ask_bool("Do you want to create these directories?"):
        for d in unique_dirs:
            if not d.exists():
                log.info(f"Creating directory: {d}")
                os.makedirs(d, exist_ok=True)


def _get_empty_dirs(working_directory: Path):
    """
    Identify empty directories within a given root directory.

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
            if file_ext in DO_NOT_DELETE:
                delete = False
                break
            if any(x in file_ext for x in VIDEO_FILE_EXTENSIONS):
                if "sample" in file_obj.name.lower() or "trailer" in file_obj.name.lower():
                    continue
                else:
                    delete = False
        if delete:
            dirs_to_delete.append(working_directory.joinpath(dir_obj.name))
    return dirs_to_delete


def _get_files_to_extract(working_directory: Path):
    """
    Scans the given root directory and identifies files to be extracted.

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
        for dir_obj in dir_scan(working_directory):
            if _should_skip_directory(dir_obj):
                continue

            tmpdict = {}
            still_downloading = False

            for file_obj in dir_scan(dir_obj.path, True):
                new_path, downloading = _process_file(file_obj, working_directory)
                if downloading:
                    still_downloading = True
                    break
                if new_path:
                    tmpdict[file_obj.path] = new_path

            if not still_downloading:
                files_to_extract.update(tmpdict)
    except Exception as e:
        log.error(f"An error occurred while getting files to extract: {e}")

    return files_to_extract


def _perform_moves(files_to_move: dict[Path, Path]):
    """
    Moves files from source to destination as specified in the files_to_move dictionary.

    Args:
        files_to_move (dict[Path, Path]): A dictionary where keys are source file paths and values are destination file paths.

    Returns:
        None

    The function first prints the list of files to be moved. It then prompts the user for confirmation to proceed with the move.
    If the user confirms, it creates the necessary directories at the destination if they do not exist, and moves the files.
    If a file already exists at the destination, it logs a message and skips moving that file. If an error occurs during the move,
    it logs an error message.
    """
    if not files_to_move:
        return

    print("\nThe following files will be moved:")
    for src, dest in files_to_move.items():
        print(f"{src} -> {dest}")

    if ask_bool("Do you want to move these files?"):
        for src, dest in files_to_move.items():
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists():
                log.info(f"File already exists: {dest}, skipping...")
            else:
                try:
                    log.info(f"Moving: {src} -> {dest}")
                    shutil.move(src, dest)
                except Exception as e:
                    log.error(f"Failed to move {src} to {dest}: {e}")


def _process_file(file_obj, working_directory):
    """
    Processes a file object to determine its new path based on its extension.

    Args:
        file_obj (File): The file object to be processed.
        working_directory (Path): The directory where the file should be moved if applicable.

    Returns:
        tuple: A tuple containing the new file path (or None if not moved) and a boolean indicating
               whether the file should not be deleted (True) or can be deleted (False).
    """
    _, file_ext = os.path.splitext(file_obj.name)
    if file_ext in DO_NOT_DELETE:
        return None, True
    if any(x in file_ext for x in VIDEO_FILE_EXTENSIONS):
        if file_obj.name.lower() in FILE_IGNORES:
            return None, False
        return working_directory.joinpath(file_obj.name), False
    return None, False


def _prompt_for_new_show(show_name: str, season_name: str, filename: str) -> Path | None:
    """
    If the show isn't in shows_map.ini, asks user whether to add it.
    Prompts for library type (Television/Documentaries), network, etc.
    Returns the newly created path or None if user declines.
    """
    print(f"Show '{show_name}' does not exist in the shows_map.ini.")
    if not ask_bool(f"Do you want to add '{show_name}'?"):
        return None

    # Prompt user for which library to use (this example is simplified)
    choice = ask_multichoice(["Television", "Documentaries"])
    if choice in SHOW_LIBRARIES:
        base_library_path = Path(SHOW_LIBRARIES[choice])
    else:
        # Fallback if not found in SHOW_LIBRARIES
        log.warning(f"{choice} not found in SHOW_LIBRARIES, defaulting to /media/Television.")
        base_library_path = Path("/media/Television")

    show_network = ask_text_input("Please enter the network the show is on (e.g., 'HBO', 'BBC'):")

    new_show_dir = base_library_path.joinpath(show_network, show_name, season_name)
    os.makedirs(new_show_dir, exist_ok=True)

    # Add to shows_map.ini
    make_shows_map()

    return new_show_dir.joinpath(filename)


def _split_season_episode(season_episode):
    """
    Splits a season and episode string into separate components.

    Args:
        season_episode (list): A list containing a single string in the format "SxxExx",
                               where "Sxx" represents the season and "Exx" represents the episode.

    Returns:
        tuple: A tuple containing the season as a string and the episode as a string.
    """
    split = season_episode[0].split("e")
    season = split[0]
    episode = f"e{split[1]}"
    return season, episode


def _should_skip_directory(dir_obj):
    """
    Determines whether a directory should be skipped based on its name.

    Args:
        dir_obj (object): An object representing a directory, which must have a 'name' attribute.

    Returns:
        bool: True if the directory's name is "_in-progress", indicating it should be skipped; False otherwise.
    """
    return dir_obj.name == "_in-progress"
