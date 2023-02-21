#!/usr/local/bin/python3
#
# moving_files.py
#

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------
import os, traceback
import modules.utils as utils
import modules.const as const

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------------

def rename_files(target_dir):
    for file_obj in utils.dir_scan(target_dir, True):
        # print(f"Let's work on: {file_obj.name}")
        if any(x in file_obj.name for x in const.FILES_TO_DELETE):
            print(f"Deleting.....{file_obj.name}")
            os.remove(file_obj.path)
        file_ext = os.path.splitext(file_obj.name)[1]
        if any(x in file_ext for x in const.FILE_EXCLUDES):
            # print(f"{file_obj.name} is still downloading")
            pass
        elif any(x in file_ext for x in const.VIDEO_FILE_EXTENSIONS):
            if os.path.isdir(file_obj.path):
                # print("This is a directory....passing")
                pass
            else:
                # print("Valid file, let's rename it")
                try:
                    __rename(file_obj)
                except:
                    print(traceback.format_exc())
        else:
            pass
            # print(f"This is not valid for renaming")
        # print("\n")

# --------------------------------------------------------------------------------
# Private API
# --------------------------------------------------------------------------------
def __fix_season_episode(season_episode):
    sortmatch = season_episode.lower().split("of")
    season = f"s{int(sortmatch[0]):02}"
    episode = f"e{int(sortmatch[1]):02}"
    if season and episode:
        return f'{season}{episode}'

def __rename(file_obj):
    new_name:str()
    fk, hdr = "", ""
    file_obj_name = file_obj.name.lower()
    if "2160p" in file_obj_name:
            fk = "-4K"
    if "hdr" in file_obj_name or "hdr10" in file_obj_name or "hdr10plus" in file_obj_name:
        hdr = "-hdr"
    file_path = os.path.split(file_obj.path)[0]
    filename_woExt, file_ext = os.path.splitext(file_obj_name)
    season_episode, alt_naming = utils.get_season_episode(file_obj_name)
    if season_episode:
        # print(f"TV file found")
        raw_episode_name = file_obj_name.split(season_episode)[0]
        if alt_naming:
            season_episode = __fix_season_episode(season_episode)
        if 'bbc' in raw_episode_name:
            raw_episode_name = raw_episode_name.replace("bbc", "").lstrip()
        episode_name = raw_episode_name.replace(" ", "_").replace(".", "_").replace("'", "").replace("!", "").rstrip()
        new_name = f"{episode_name}{season_episode}{fk}{hdr}{file_ext}"
        print(f"Renaming.....{file_obj.path} -> {os.path.join(file_path, new_name.lower())}")
        os.rename(file_obj.path, os.path.join(file_path, new_name.lower()))
    else:
        # print(f"Movie file found")
        if "2160p" in filename_woExt:
            fk = "-4K"
        if "hdr" in filename_woExt or "hdr10plus" in filename_woExt:
            hdr = "-hdr"
        if "." in filename_woExt:
            filename_woExt = "_".join(filename_woExt.split('.')).lower()
        filename_woExt = filename_woExt.replace(" (", "_").replace(" ", "_").lower()
        year = utils.get_year(filename_woExt)
        filename_woExt_split = filename_woExt.split(year)
        new_name = f"{filename_woExt_split[0]}({year}){fk}{hdr}{file_ext}"
        print(f"Renaming.....{file_obj.path} -> {os.path.join(file_path, new_name)}")
        os.rename(file_obj.path, os.path.join(file_path, new_name))
