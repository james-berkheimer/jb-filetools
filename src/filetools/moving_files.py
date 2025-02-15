#!/usr/local/bin/python3
#
# moving_files.py
#

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------

import os
import shutil
import traceback
from pathlib import Path

from .constants import (
    DO_NOT_DELETE,
    FILE_EXCLUDES,
    FILE_IGNORES,
    FILES_TO_DELETE,
    LIBRARIES,
    MOVIE_LIBRARIES,
    PROJECT_ROOT,
    SHOW_LIBRARIES,
    VIDEO_FILE_EXTENSIONS,
)
from .logging import setup_logger
from .questions import ask_bool, ask_multichoice, ask_text_input
from .utils import (
    dir_scan,
    get_season_episode,
    get_show_map,
    make_shows_map,
    match_for_tv,
    unique,
)

log = setup_logger(__name__)

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Public Functions
# --------------------------------------------------------------------------------


def clean_empty_dirs(root_dir: Path):
    """
    Recursively finds and deletes empty directories within the specified root directory.

    Args:
        root_dir (Path): The root directory to search for empty directories.

    Logs:
        - Lists all empty directories found.
        - Asks the user for confirmation before deleting directories.
        - Logs each directory deletion attempt and any errors encountered.

    Raises:
        OSError: If an error occurs while attempting to delete a directory.
    """
    dirs_to_delete = get_empty_dirs(root_dir)

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


def extract_from_src(root_dir: Path):
    """
    Extracts files from the source directory to their new locations.

    This function retrieves a list of files to be moved from the source directory
    specified by `root_dir` and moves each file to its new location. It logs the
    progress of the extraction process, including any errors encountered during
    the file moves.

    Args:
        root_dir (Path): The root directory containing the files to be extracted.

    Raises:
        Exception: If an error occurs while moving a file, it is logged but not re-raised.
    """
    files_to_extract = get_files_to_extract(root_dir)

    log.info("----------- Starting file extraction process -----------")
    for old_path, new_path in files_to_extract.items():
        try:
            log.info(f"Extracting {old_path} to {new_path}")
            shutil.move(old_path, new_path)
        except Exception as e:
            log.error(f"Failed to move {old_path} to {new_path}: {e}")

    log.info("File extraction process completed")


def move_to_libraries(root_dir: Path):
    movies, shows = _sort_media(dir_scan(root_dir, True))
    move_movie_files(movies, root_dir)
    move_show_files(shows, root_dir)


# --------------------------------------------------------------------------------
# Private Functions
# --------------------------------------------------------------------------------
def get_empty_dirs(root_dir: Path):
    """
    Identify empty directories within a given root directory.

    This function scans the specified root directory and identifies directories
    that can be considered empty based on the absence of certain file types.
    A directory is considered empty if it does not contain any files with
    extensions listed in DO_NOT_DELETE or any video files that are not samples
    or trailers.

    Args:
        root_dir (Path): The root directory to scan for empty directories.

    Returns:
        list: A list of Path objects representing directories that can be deleted.
    """
    dirs_to_delete = []
    for dir_obj in dir_scan(root_dir):
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
            dirs_to_delete.append(root_dir.joinpath(dir_obj.name))
    return dirs_to_delete


def get_files_to_extract(root_dir: Path):
    """
    Scans the given root directory and identifies files to be extracted.

    This function recursively scans the root directory and its subdirectories,
    identifying files that are ready to be extracted. It skips directories
    that should not be processed and handles files that are still downloading.

    Args:
        root_dir (Path): The root directory to scan for files to extract.

    Returns:
        dict: A dictionary where the keys are the original file paths and the
              values are the new paths for the files to be extracted.

    Raises:
        Exception: If an error occurs during the directory scanning or file processing.
    """
    files_to_extract = {}

    try:
        for dir_obj in dir_scan(root_dir):
            if _should_skip_directory(dir_obj):
                continue

            tmpdict = {}
            still_downloading = False

            for file_obj in dir_scan(dir_obj.path, True):
                new_path, downloading = _process_file(file_obj, root_dir)
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


def move_movie_files(movies: list, root_dir: Path):
    """
    Moves movie files from the root directory to the appropriate movie library.

    Args:
        movies (list): List of movie filenames to be moved.
        root_dir (Path): The root directory where the movie files are currently located.

    The function determines the target path for each movie based on the MOVIE_LIBRARIES
    dictionary. If there are multiple libraries, the user is prompted to choose one.
    It then creates the necessary directories and moves the movie files to the target path.
    If a movie file already exists at the target location, it logs that the movie is already
    in the server.
    """
    for movie in movies:
        libraries = list(MOVIE_LIBRARIES.keys())
        if len(libraries) > 1:
            choice = ask_multichoice(libraries)
            target_path = MOVIE_LIBRARIES[choice]
        else:
            target_path = MOVIE_LIBRARIES[libraries[0]]

        filename_wo_ext, _ = os.path.splitext(movie)
        filename_wo_ext = filename_wo_ext.replace("-4k-hdr", "")
        new_movie_path = target_path.joinpath(filename_wo_ext)
        src = root_dir.joinpath(movie)
        dst = new_movie_path.joinpath(movie)

        try:
            new_movie_path.mkdir(parents=True, exist_ok=True)
            if not dst.is_file():
                log.info(f"Moving: {src} to {dst}")
                shutil.move(src, dst)
            else:
                log.info(f"Movie already in server: {movie}")
        except Exception as e:
            log.error(f"Failed to move {src} to {dst}: {e}")


def move_show_files(shows: list, root_dir: Path):
    move_dict = {}
    make_dirs = []
    skip = []
    for show in shows:
        season_episode = get_season_episode(show)
        show_name = show.split(season_episode[0])[0].rstrip("_")
        season = _split_season_episode(season_episode)[0].replace("s", "season_")
        if season == "season_00":
            season = "specials"
        src = root_dir.joinpath(show)
        try:
            # first match.  Check if show is in show_map
            show_map = get_show_map()
            matched_path = Path(show_map["Shows"][show_name])
            season_path = matched_path.joinpath(season)
            # Second match.  Check if season exists
            if season_path.exists() is False:
                make_dirs.append(season_path)
            move_dict[src] = season_path.joinpath(show)
        except KeyError:
            # If show is not in show_map, we will make a new show directory
            if show_name not in skip:
                print(f"{show_name} does not exist")
                if ask_bool(f"Do you want to add {show_name}?"):
                    if ask_multichoice(["Television", "Documentary"]) == "Television":
                        show_type_path = TELEVISION_PATH
                    else:
                        show_type_path = DOCUMENTARIES_PATH
                    show_network = ask_text_input("Please enter the network the show is on")
                    new_show_path = show_type_path.joinpath(show_network, show_name, season)
                    # Making a new show directory.  This is for when we have multiple episodes
                    # for a new show to add.  This will prevent having to ask this question
                    # for each episode.
                    os.makedirs(new_show_path)
                    # create new show_map to include newly created show
                    make_shows_map()
                    move_dict[src] = new_show_path.joinpath(show)
                else:
                    skip.append(show_name)
    if make_dirs:
        # Make dirs that don't exist
        make_dirs = unique(make_dirs)
        print("Directories to make:")
        for mdir in make_dirs:
            print(f"   {mdir}")
        if ask_bool("Do you want to make directories?"):
            for mdir in make_dirs:
                print(f"Making....{mdir}")
                os.makedirs(mdir)
    print("\n")
    if move_dict:
        # Let's move these files
        for _, dest in move_dict.items():
            print(dest)
        if ask_bool("Do you want to move files?"):
            for src, dest in move_dict.items():
                if os.path.isfile(dest):
                    print(f"file exists....{dest}")
                    pass
                else:
                    print(f"moving....{dest}")
                    shutil.move(src, dest)


def _process_file(file_obj, root_dir):
    _, file_ext = os.path.splitext(file_obj.name)
    if file_ext in DO_NOT_DELETE:
        return None, True
    if any(x in file_ext for x in VIDEO_FILE_EXTENSIONS):
        if file_obj.name.lower() in FILE_IGNORES:
            return None, False
        return root_dir.joinpath(file_obj.name), False
    return None, False


def _sort_media(files_obj):
    movies = []
    shows = []
    for file_obj in files_obj:
        if any(x in file_obj.name for x in FILES_TO_DELETE):
            print(f"deleting: {file_obj.name}")
            os.remove(file_obj.path)
        elif any(x in file_obj.name for x in FILE_EXCLUDES):
            pass
        else:
            match = match_for_tv(file_obj.name)
            if match:
                shows.append(file_obj.name)
            else:
                movies.append(file_obj.name)
    return movies, shows


def _split_season_episode(season_episode):
    split = season_episode[0].split("e")
    season = split[0]
    episode = f"e{split[1]}"
    return season, episode


def _should_skip_directory(dir_obj):
    return dir_obj.name == "_in-progress"
