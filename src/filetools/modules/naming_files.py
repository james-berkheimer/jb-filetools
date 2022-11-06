#!/usr/local/bin/python3
#
# moving_files.py
#

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------

from genericpath import isdir
import os, shutil, traceback, re, pathlib

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------
files_to_delete = ['.DS_Store', 'RARBG.txt']


# --------------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------------

def rename_episodes(curdir):
    for f in os.listdir(curdir):
        if any(x in f for x in files_to_delete):
            print(f"Deleting: {os.path.join(curdir, f)}")
            os.remove(os.path.join(curdir, f)) 
        elif '.part' in f:
            print("This torrent is still downloading.....passing.")
            pass
        else:
            if os.path.isdir(f):
                print("This is a directory....passing")
                pass
            else:
                fk, hdr = "", ""
                if "2160p" in f.split('.'):
                    fk = "-4K"
                if "HDR" in f.split('.'):
                    hdr = "-HDR"
                try:
                    season_episode = __getSeasonEpisode(f)
                    print("Season_Episode: " + str(season_episode))
                    details = f.split(season_episode)
                    print(details)
                    episode_name = details[0].replace(".", " ")
                    file_extension = details[1].split(".")[-1]
                    new_name = f"{episode_name} - {season_episode.upper()}{fk}{hdr}.{file_extension}"
                    print(new_name)
                    os.rename(os.path.join(curdir, f), os.path.join(curdir, new_name))
                except:
                    # print(traceback.format_exc())
                    print("Not an episodic file....passing")


def rename_movies(curdir):
    for f in os.listdir(curdir):
        if '.DS_Store' in f:
            pass
        if os.path.isdir(f):
            print("This is a directory....passing\n")
            pass
        else:
            print("Let's rename.....", f)
            file_extension = pathlib.Path(f).suffix
            print("   ", file_extension)
            woExt = f.split(file_extension)[0]
            print("   ", woExt)
            cleanName = " ".join(woExt.split('.')).title()
            print("   ", cleanName)
            year = __getYear(cleanName)
            print("   ", year)
            newName = cleanName.split(year)[0] + "(" + year + ")" + file_extension
            print("   ", newName)
            try:
                os.rename(os.path.join(curdir, f), os.path.join(curdir, newName))
            except:
                print(traceback.format_exc())
            print("\n")


# --------------------------------------------------------------------------------
# Private API
# --------------------------------------------------------------------------------

def __getSeasonEpisode(filename):
    match_season = re.search(
        r'''(?ix)                 # Ignore case (i), and use verbose regex (x)
        (?:                       # non-grouping pattern
          s|season|^           # e or x or episode or start of a line
          )                       # end non-grouping pattern 
        \s*                       # 0-or-more whitespaces
        (\d{2})                   # exactly 2 digits
        ''', filename)

    match_episode = re.search(
        r'''(?ix)                 # Ignore case (i), and use verbose regex (x)
        (?:                       # non-grouping pattern
          e|x|episode|^           # e or x or episode or start of a line
          )                       # end non-grouping pattern 
        \s*                       # 0-or-more whitespaces
        (\d{2})                   # exactly 2 digits
        ''', filename)
    if match_season and match_episode:
        return match_season.group(0) + match_episode.group(0)


def __getYear(target_string):
    matches = re.findall(r"[0-9]{4}", target_string)
    filteredMatches = []
    for m in matches:
        if int(m) in range(1900,2030):
            filteredMatches.append(m)
    return(filteredMatches[-1])  
