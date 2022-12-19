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
        print(f"Let's work on: {file_obj.name}")
        if any(x in file_obj.name for x in const.FILES_TO_DELETE):
            print(f"deleting: {file_obj.name}")
            os.remove(file_obj.path)
        file_ext = os.path.splitext(file_obj.name)[1]
        if any(x in file_ext for x in const.VIDEO_FILE_EXTENSIONS):
            if os.path.isdir(file_obj.path):
                print("This is a directory....passing")
                pass
            else:
                print("Valid file, let's rename it")
                try:
                    __rename(file_obj)
                except:
                    print(traceback.format_exc())
        else:
            print(f"This is not valid for renaming")
        print("\n")

# --------------------------------------------------------------------------------
# Private API
# --------------------------------------------------------------------------------
def __rename(file_obj):
    new_name:str()
    fk, hdr = "", ""
    file_path = os.path.split(file_obj.path)[0]
    filename_woExt, file_ext = os.path.splitext(file_obj.name)
    season_episode, alt_naming = utils.get_season_episode(file_obj.name)
    if season_episode:
        print(f"TV file found")
        fsplit = file_obj.name.lower().split(season_episode)
        if alt_naming:
            season_episode = utils.fix_season_episode(season_episode)        
        if "2160p" in fsplit[1]:
            print("4K file found")
            fk = "-4K"
        if "hdr" in fsplit[1]:
            print("HDR file found")
            hdr = "-hdr"
        fsplit0 = fsplit[0].split('.')
        print(f"fsplit0: {fsplit0}")
        if 'bbc' in fsplit0:
            print("BBC file found")
            fsplit0.remove('bbc')
        episode_name = "_".join(fsplit0).rstrip().replace("!", "")
        new_name = f"{episode_name}{season_episode}{fk}{hdr}{file_ext}"
        print(f"new_name: {new_name}")
        print(f"RENAMING: {file_obj.path}, {os.path.join(file_path, new_name.lower())}")
        os.rename(file_obj.path, os.path.join(file_path, new_name.lower()))
    else:
        print(f"Movie file found")
        filename_woExt_split = filename_woExt.split('.')
        clean_name = "_".join(filename_woExt_split).lower()
        if "2160p" in clean_name:
            print("4K file found")
            fk = "-4K"
        if "hdr" in clean_name or "hdr10plus" in clean_name:
            print("HDR file found")
            hdr = "-hdr"
        year = utils.get_year(clean_name)
        new_name = f"{clean_name.split(year)[0].rstrip()}({year}){fk}{hdr}{file_ext}".lower()
        print(f"new_name: {new_name}")
        print(f"RENAMING: {file_obj.path}, {os.path.join(file_path, new_name)}")
        os.rename(file_obj.path, os.path.join(file_path, new_name))
