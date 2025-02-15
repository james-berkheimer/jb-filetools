#!/usr/local/bin/python3
#
# naming_files.py
#

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------
import os
import traceback

from . import constants, utils

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------------


def rename_files(target_dir):
    for file_obj in utils.dir_scan(target_dir, True):
        if any(x in file_obj.name for x in constants.FILES_TO_DELETE):
            print(f"Deleting.....{file_obj.name}")
            os.remove(file_obj.path)
        file_ext = os.path.splitext(file_obj.name)[1]
        if any(x in file_ext for x in constants.VIDEO_FILE_EXTENSIONS):
            if any(x in file_ext for x in constants.FILE_EXCLUDES):
                pass
            else:
                try:
                    __rename(file_obj)
                except Exception:
                    print(f"\nFailed on...{file_obj.name}")
                    print(traceback.format_exc())


# --------------------------------------------------------------------------------
# Private API
# --------------------------------------------------------------------------------
def __fix_season_episode(season_episode):
    sortmatch = season_episode.lower().split("of")
    # season = f"s{int(sortmatch[0]):02}"
    season = "s01"
    episode = f"e{int(sortmatch[0]):02}"
    if season and episode:
        return f"{season}{episode}"


def __rename(file_obj):
    new_name = ""
    fk, hdr, flags_name = "", "", ""
    flags = []

    file_obj_name = file_obj.name.lower()
    if "2160p" in file_obj_name:
        flags.append("4K")

    if "hdr" in file_obj_name or "hdr10" in file_obj_name or "hdr10plus" in file_obj_name:
        flags.append("hdr")
    if flags:
        flags_name = f"_[{'_'.join(flags)}]"

    file_path = os.path.split(file_obj.path)[0]
    filename_woExt, file_ext = os.path.splitext(file_obj_name)
    season_episode, alt_naming = utils.get_season_episode(file_obj_name)
    if season_episode:
        raw_episode_name = file_obj_name.split(season_episode)[0]
        if alt_naming:
            season_episode = __fix_season_episode(season_episode)
        if "bbc" in raw_episode_name:
            raw_episode_name = raw_episode_name.replace("bbc", "").lstrip()
            if raw_episode_name[0] == ".":
                raw_episode_name = raw_episode_name[1:]
        episode_name = (
            raw_episode_name.replace(" ", "_")
            .replace(".", "_")
            .replace("'", "")
            .replace("!", "")
            .replace("_-_", "_")
            .rstrip()
        )
        new_name = f"{episode_name}{season_episode}{flags_name}{file_ext}"
        new_name_path = os.path.join(file_path, new_name.lower())
        if not os.path.exists(new_name_path):
            print(f"Renaming.....{file_obj.path} -> {new_name_path}")
            os.rename(file_obj.path, new_name_path)
    else:
        if "2160p" in filename_woExt:
            fk = "-4K"
        if "hdr" in filename_woExt or "hdr10plus" in filename_woExt:
            hdr = "-hdr"
        if "." in filename_woExt:
            filename_woExt = "_".join(filename_woExt.split(".")).lower()
        filename_woExt = filename_woExt.replace(" (", "_").replace(" ", "_").lower()
        year = utils.get_year(filename_woExt)
        filename_woExt_split = filename_woExt.split(year)
        new_name = f"{filename_woExt_split[0]}({year}){fk}{hdr}{file_ext}"
        new_name_path = os.path.join(file_path, new_name)
        if not os.path.exists(new_name_path):
            print(f"Renaming.....{file_obj.path} -> {new_name_path}")
            os.rename(file_obj.path, new_name_path)
