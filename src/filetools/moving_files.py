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

import const as const
import questions as questions
import utils as utils

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------------


def add_to_dir(root_dir: Path):
    files = []
    tmpdir = __make_temp_dir(root_dir.joinpath("_tmp"))
    for entry in os.scandir(root_dir):
        if entry.is_dir():
            continue
        else:
            files.append(entry.name)

    for f in files:
        if any(x in f for x in const.VIDEO_FILE_EXTENSIONS):
            newDir = f[:-11]
            newpath = Path(root_dir + newDir)
            src = dst = root_dir.joinpath(f)
            dst = newpath.joinpath(f)
            print("Moving: %s to %s" % (src, dst))
            toTmp = os.path.join(tmpdir, newDir)
            print("Moving: %s to %s" % (newpath, toTmp))
            try:
                os.mkdir(newpath)
                shutil.move(src, dst)
                shutil.move(newpath, toTmp, copy_function=shutil.copytree)
            except Exception:
                print(traceback.format_exc())
        print("\n")


def clean_empty_dirs(root_dir: Path):
    dirs_to_delete = []
    for dir_obj in utils.dir_scan(root_dir):
        delete = True
        for file_obj in utils.dir_scan(dir_obj.path, True):
            filename_woExt, file_ext = os.path.splitext(file_obj.name)
            if ".part" == file_ext:
                delete = False
                break
            if any(x in file_ext for x in const.VIDEO_FILE_EXTENSIONS):
                if "sample" in file_obj.name.lower():
                    pass
                elif "trailer" in file_obj.name.lower():
                    pass
                else:
                    delete = False
        if delete:
            dirs_to_delete.append(root_dir.joinpath(dir_obj.name))
    # Prompt user.  Initiate delete if yes
    if dirs_to_delete:
        print("Empty directories:")
        for dir_to_delete in dirs_to_delete:
            print(f"{dir_to_delete}")
        print("\n")
        if questions.ask_bool("Delete directories?"):
            for d in dirs_to_delete:
                print("Deleting directory.....", d)
                try:
                    shutil.rmtree(d)
                except OSError as e:
                    print("Error: %s : %s" % (d, e.strerror))
    else:
        print("No directories to delete")


def extract_files(root_dir: Path):
    files_to_extract = {}

    for dir_obj in utils.dir_scan(root_dir):
        if dir_obj.name == "_in-progress":
            continue

        tmpdict = {}
        still_downloading = False

        for file_obj in utils.dir_scan(dir_obj.path, True):
            filename_woExt, file_ext = os.path.splitext(file_obj.name)

            if file_ext == ".part":
                still_downloading = True
                break

            if any(x in file_ext for x in const.VIDEO_FILE_EXTENSIONS):
                if "sample" in file_obj.name.lower() or "trailer" in file_obj.name.lower():
                    continue
                tmpdict[file_obj.path] = root_dir.joinpath(file_obj.name)

        if not still_downloading:
            files_to_extract.update(tmpdict)

    print("------------------------------------------------------------------------------------------")
    for old_path, new_path in files_to_extract.items():
        print(f"Extracting......{old_path}")
        shutil.move(old_path, new_path)


def move_files(root_dir: Path):
    movies, shows = __sort_media(utils.dir_scan(root_dir, True))
    __move_movies(movies, root_dir)
    __move_shows(shows, root_dir)


# --------------------------------------------------------------------------------
# Private API
# --------------------------------------------------------------------------------
def __get_show_map():
    try:
        show_map = const.PROJECT_ROOT.joinpath("shows_map.ini")
    except KeyError:
        print("No show_map.ini found, let's make one...")
        utils.make_shows_map([const.TELEVISION_PATH, const.DOCUMENTARIES_PATH])
    import configparser

    config = configparser.ConfigParser()
    config.read(show_map)
    return config


def __make_temp_dir(tmpdir: Path):
    if tmpdir.exists():
        pass
    else:
        os.mkdir(tmpdir)
    return tmpdir


def __move_movies(movies: list, root_dir: Path):
    for movie in movies:
        # print(movie)
        # movie_year = utils.get_year(movie)
        # movie_name = movie.split(f"({movie_year})")[0].rstrip('_')
        filename_woExt, file_ext = os.path.splitext(movie)
        filename_woExt = filename_woExt.replace("-4k-hdr", "")
        new_movie_path = const.MOVIES_PATH.joinpath(filename_woExt)
        src = root_dir.joinpath(movie)
        dst = new_movie_path.joinpath(movie)
        if new_movie_path.exists() is False:
            print(f"Making: {new_movie_path}")
            os.mkdir(new_movie_path)
        if dst.is_file() is False:
            print(f"Moving: {src} to {dst}")
            shutil.move(src, dst)
        else:
            print(f"Movie already in server: {movie}")


def __move_shows(shows: list, root_dir: Path):
    move_dict = {}
    make_dirs = []
    skip = []
    for show in shows:
        season_episode = utils.get_season_episode(show)
        show_name = show.split(season_episode[0])[0].rstrip("_")
        season = __split_season_episode(season_episode)[0].replace("s", "season_")
        if season == "season_00":
            season = "specials"
        src = root_dir.joinpath(show)
        try:
            # first match.  Check if show is in show_map
            show_map = __get_show_map()
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
                if questions.ask_bool(f"Do you want to add {show_name}?"):
                    if questions.ask_multichoice(["Television", "Documentary"]) == "Television":
                        show_type_path = const.TELEVISION_PATH
                    else:
                        show_type_path = const.DOCUMENTARIES_PATH
                    show_network = questions.ask_text_input("Please enter the network the show is on")
                    new_show_path = show_type_path.joinpath(show_network, show_name, season)
                    # Making a new show directory.  This is for when we have multiple episodes
                    # for a new show to add.  This will prevent having to ask this question
                    # for each episode.
                    os.makedirs(new_show_path)
                    # create new show_map to include newly created show
                    utils.make_shows_map()
                    move_dict[src] = new_show_path.joinpath(show)
                else:
                    skip.append(show_name)
    if make_dirs:
        # Make dirs that don't exist
        make_dirs = utils.unique(make_dirs)
        print("Directories to make:")
        for mdir in make_dirs:
            print(f"   {mdir}")
        if questions.ask_bool("Do you want to make directories?"):
            for mdir in make_dirs:
                print(f"Making....{mdir}")
                os.makedirs(mdir)
    print("\n")
    if move_dict:
        # Let's move these files
        for src, dest in move_dict.items():
            print(dest)
        if questions.ask_bool("Do you want to move files?"):
            for src, dest in move_dict.items():
                if os.path.isfile(dest):
                    print(f"file exists....{dest}")
                    pass
                else:
                    print(f"moving....{dest}")
                    shutil.move(src, dest)


def __sort_media(files_obj):
    movies = []
    shows = []
    for file_obj in files_obj:
        if any(x in file_obj.name for x in const.FILES_TO_DELETE):
            print(f"deleting: {file_obj.name}")
            os.remove(file_obj.path)
        elif any(x in file_obj.name for x in const.FILE_EXCLUDES):
            pass
        else:
            match = utils.match_for_tv(file_obj.name)
            if match:
                shows.append(file_obj.name)
            else:
                movies.append(file_obj.name)
    return movies, shows


def __split_season_episode(season_episode):
    split = season_episode[0].split("e")
    season = split[0]
    episode = f"e{split[1]}"
    return season, episode
