#!/usr/local/bin/python3
#
# moving_files.py
#

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------

import os, traceback, re
import modules.utils as utils
import modules.const as const


# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------------

def rename_files(target_dir):
    print("\n")
    for file_obj in utils.dir_scan(target_dir, True):
        print(f"Let's work on: {file_obj.name}")
        if any(x in file_obj.name for x in const.files_to_delete):
            print(f"   Cleanup, deleting: {file_obj.name}")
            os.remove(file_obj.path)
        file_ext = os.path.splitext(file_obj.name)[1]
        if any(x in file_ext for x in const.video_file_extensions):
            if os.path.isdir(file_obj.path):
                print("  This is a directory....passing")
                pass
            else:
                print("  Valid file, let's rename it")
                try:
                    __rename(file_obj)
                except:
                    print(traceback.format_exc())
        else:
            print(f"  This is not valid for renaming")
        print("\n")

# --------------------------------------------------------------------------------
# Private API
# --------------------------------------------------------------------------------

def __fix_season_episode(season_episode):
    print(f"      Let's make a proper season_episode: {season_episode}")
    sortmatch = season_episode.lower().split("of")
    season = f"s{int(sortmatch[0]):02}"
    episode = f"e{int(sortmatch[1]):02}"
    if season and episode:
        return f'{season}{episode}'

def __getSeasonEpisode(filename):
    print("      Let's extract the season and episode numbers")
    alt_naming = False
    # Search for episodes with season/episode names of #of#
    alt_season_match = re.search(r'''(?ix)\s*(\d{1,2})(?:of|^)\s*(\d{2})''', filename)
    if alt_season_match:
        print(f"Found alt season naming in {filename}")
        alt_naming = True
        return alt_season_match.group(0), alt_naming
    # Search for traditional S##E## naming
    else:
        match = re.search(r".?((s\d{2}|s\d{4})e\d{2}).?", filename, re.I)
        if match:
            parseMatch = match.group(1).lower().split('e')
            match_season = parseMatch[0]
            match_episode = f"e{parseMatch[1]}"
            return f"{match_season}{match_episode}", alt_naming
        else:
            return None, alt_naming

def __getYear(target_string):
    print("      Let's extract the year of the movie")
    try:
        matches = re.findall(r"[0-9]{4}", target_string)
    except:
        print(f"NO YEAR MATCHES")
        return False        
    filteredMatches = []
    for m in matches:
        if int(m) in range(1900,2030):
            filteredMatches.append(m)
    return(filteredMatches[-1])  

def __rename(file_obj):
    new_name:str()
    fk, hdr = "", ""
    file_path = os.path.split(file_obj.path)[0]
    filename_woExt, file_ext = os.path.splitext(file_obj.name)
    season_episode, alt_naming = __getSeasonEpisode(file_obj.name)
    if season_episode:
        print(f"    TV file found")
        fsplit = file_obj.name.lower().split(season_episode)
        if alt_naming:
            season_episode = __fix_season_episode(season_episode)        
        if "2160p" in fsplit[1]:
            print("      4K file found")
            fk = "-4K"
        if "hdr" in fsplit[1]:
            print("      HDR file found")
            hdr = "-hdr"
        fsplit0 = fsplit[0].split('.')
        print(f"fsplit0: {fsplit0}")
        if 'bbc' in fsplit0:
            print("      BBC file found")
            fsplit0.remove('bbc')
        episode_name = "_".join(fsplit0).rstrip()
        new_name = f"{episode_name}{season_episode}{fk}{hdr}{file_ext}"
        print(f"      new_name: {new_name}")
        print(f"      RENAMING: {file_obj.path}, {os.path.join(file_path, new_name.lower())}")
        os.rename(file_obj.path, os.path.join(file_path, new_name.lower()))
    else:
        print(f"    Movie file found")
        filename_woExt_split = filename_woExt.split('.')
        clean_name = "_".join(filename_woExt_split).lower()
        if "2160p" in clean_name:
            print("      4K file found")
            fk = "-4K"
        if "hdr" in clean_name or "hdr10plus" in clean_name:
            print("      HDR file found")
            hdr = "-hdr"
        year = __getYear(clean_name)
        new_name = f"{clean_name.split(year)[0].rstrip()}({year}){fk}{hdr}{file_ext}".lower()
        print(f"      new_name: {new_name}")
        print(f"      RENAMING: {file_obj.path}, {os.path.join(file_path, new_name)}")
        os.rename(file_obj.path, os.path.join(file_path, new_name))