#!/usr/local/bin/python3
#
# moving_files.py
#

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------

import os, shutil, traceback
from pathlib import Path
import modules.utils as utils
import modules.const as const
import modules.questions as questions


# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------------

def add_to_dir(root_dir:Path):
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
                shutil.move(newpath, toTmp, copy_function = shutil.copytree)
            except:
                print(traceback.format_exc())
        print("\n")

def clean_empty_dirs(root_dir:Path):
    dirs_to_delete = []
    for dir_obj in utils.dir_scan(root_dir):
        delete = True
        print("Directory:",dir_obj.name)
        for file_obj in utils.dir_scan(dir_obj.path):
            print("  ",file_obj.name)
            if any(x in file_obj.name for x in const.VIDEO_FILE_EXTENSIONS):
                if "sample-" in file_obj.name:
                    print("Found file but it's a sample....deleting:", file_obj.name)
                    delete = True
                    break
                print("   Found file....", file_obj.name)
                delete = False
                pass
        if delete:
            dirs_to_delete.append(root_dir.joinpath(dir_obj.name))
        print("\n")

    # Prompt user.  Initiate delete if yes
    print("Empty directories:")
    for dir_to_delete in dirs_to_delete:    
        print(f"   {dir_to_delete}")
    print("\n")
    user_input = input("Delete directories? y/n?\n")
    if user_input == "y":
        for d in dirs_to_delete:
            print("Deleting directory.....", d)
            try:
                shutil.rmtree(d)
            except OSError as e:
                print("Error: %s : %s" % (d, e.strerror))

def extract_files(root_dir:Path):
    print(type(root_dir))
    for dir_obj in utils.dir_scan(root_dir):
        print(f"DIRECTORY: {dir_obj.name}")
        for file_obj in utils.dir_scan(dir_obj.path, True):
            print(f"FILE: {file_obj.name}")        
            if any(x in file_obj.name for x in const.FILE_EXCLUDES):
                print(f"Exclude: {file_obj.name}")
                pass
            elif any(x in file_obj.name for x in const.VIDEO_FILE_EXTENSIONS):
                new_name = root_dir.joinpath(file_obj.name)
                print(f"Extracting....{file_obj.path} to {new_name}")
                shutil.move(file_obj.path, new_name)

def move_files(root_dir:Path):
    print("------------ Move Files ------------")
    movies, shows = __sort_media(utils.dir_scan(root_dir, True))
    print(shows)
    print(movies)
    __move_movies(movies, root_dir)
    __move_shows(shows, root_dir)


# --------------------------------------------------------------------------------
# Private API
# --------------------------------------------------------------------------------

def __make_temp_dir(tmpdir:Path):
    if tmpdir.exists():
        pass
    else:
        os.mkdir(tmpdir)
    return(tmpdir)

def __move_movies(movies: list, root_dir:Path):
    print("------------ Move Movies ------------")
    print(movies)
    for movie in movies:
        print(movie)
        movie_year = utils.get_year(movie)
        movie_name = movie.split(f"({movie_year})")[0].rstrip('_')
        new_movie_path = const.MOVIES_PATH.joinpath(movie_name)
        if not new_movie_path.is_dir():
            print(f"Making: {new_movie_path}")            
            os.mkdir(new_movie_path)
            src = root_dir.joinpath(movie)
            dst = new_movie_path.joinpath(movie)
            print(f"Movie: {src} to {dst}")
            shutil.move(src, dst)
        else:
            print(f"Movie already in server: {movie}")

def __move_shows(shows: list, root_dir:Path):
    '''TODO
    You need to make a list of all the moves to run 
    after you prepared the directory structure for all files
    '''
    print("------------ Move Shows ------------")
    show_map = utils.get_show_map()
    for show in shows:
        print(show)
        season_episode = utils.get_season_episode(show)
        show_name = show.split(season_episode[0])[0].rstrip('_')
        season = utils.split_season_episode(season_episode)[0].replace("s", "season_")
        src = root_dir.joinpath(show)
        try:
            matched_path = Path(show_map['Shows'][show_name])
            season_path = matched_path.joinpath(season)
            dest = season_path.joinpath(show)            
            if season_path.exists() is False:
                print(f"Season {season} does not exist")
                if questions.ask_bool("Do you want to add a new season and move file to it?"):
                    print(f"Making season directory: {season_path}")
                    os.makedir(season_path)   
                    print(f"Moving: {src} -> {dest}")
                    shutil.move(src, dest)
                else:
                    print("Passing")
            elif dest.exists():
                print(f"File exists: {dest}")
                print("Passing")
            else:
                print(f"Moving: {src} -> {dest}")
                shutil.move(src, dest)
                print("\n")
        except:
            print(f"{show_name} does not exist")
            if questions.ask_bool(f"Do you want to create {show_name} directory?"):
                if questions.ask_multichoice(["Television", "Documentary"]) == "Television":
                    show_type_path = const.TELEVISION_PATH
                    show_network = questions.ask_text_input("Please enter the network the show is on")
                    new_show_path = show_type_path.joinpath(show_network, show_name, season)
                    print(f"Making {new_show_path}")
                    os.makedirs(new_show_path)
                    print(f"Moving {src} to {new_show_path.joinpath(show)}")                    
                    shutil.move(src, new_show_path.joinpath(show))                  
                else:
                    show_type_path = const.DOCUMENTARIES_PATH
                    show_network = questions.ask_text_input("Please enter the network the show is on")
                    new_show_path = show_type_path.joinpath(show_network, show_name, season)
                    print(f"Making {new_show_path}")
                    os.makedirs(new_show_path)
                    print(f"Moving {src} to {new_show_path.joinpath(show)}")
                    shutil.move(src, new_show_path.joinpath(show))
                    
def __sort_media(files_obj):
    print("------------ Sort Media ------------")
    movies = []
    shows = []
    for file_obj in files_obj:
        print(f"Matching: {file_obj.name}")
        match = utils.match_for_tv(file_obj.name)
        print(match)
        if match:
            print(f"Appending {file_obj.name} to shows")
            shows.append(file_obj.name)
        else:
            print(f"Appending {file_obj.name} to movies")
            movies.append(file_obj.name)
    return movies, shows
    
