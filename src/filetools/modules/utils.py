#!/usr/bin/env python
#
# modules/utils.py
#
# This file will store globally used functions used in this project
#

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------
import os
import re
from pathlib import Path
import configparser
import modules.const as const
import modules.questions as questions

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------------
def dir_scan(scan_path:str, getfiles=False):
    scan_obj = os.scandir(scan_path)
    scan_output = []
    for root_scan_entry in scan_obj:
        if getfiles == False:
            if root_scan_entry.is_dir():
                scan_output.append(root_scan_entry)
        else:
            if root_scan_entry.is_file():
                scan_output.append(root_scan_entry)
    scan_obj.close()
    return scan_output

def fix_season_episode(season_episode):
    print(f"Fixing season_episode to standard: {season_episode}")
    sortmatch = season_episode.lower().split("of")
    season = f"s{int(sortmatch[0]):02}"
    episode = f"e{int(sortmatch[1]):02}"
    if season and episode:
        return f'{season}{episode}'

def get_season_episode(filename):
    print("Extracting the season and episode numbers")
    alt_naming = False
    # Search for episodes with season/episode names of #of#
    alt_season_match = match_for_altseason(filename)
    if alt_season_match:
        print(f"Found alt season naming in {filename}")
        alt_naming = True
        return alt_season_match.group(0), alt_naming
    # Search for traditional S##E## naming
    else:
        match = match_for_tv(filename)
        if match:
            parseMatch = match.group(1).lower().split('e')
            match_season = parseMatch[0]
            match_episode = f"e{parseMatch[1]}"
            return f"{match_season}{match_episode}", alt_naming
        else:
            return None, alt_naming

def get_show_map():
    try:
        show_map = const.PROJECT_ROOT.joinpath("shows_map.ini")
    except:
        print("No show_map.ini found, let's make one...")
        make_shows_map([const.TELEVISION_PATH, const.DOCUMENTARIES_PATH])
        
    config = configparser.ConfigParser()
    config.read(show_map)
    return config

def get_year(target_string):
    print("Let's extract the year of the movie")
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

def make_config():
    '''TODO
    For eventual public release.  Make a function that 
    allows the user to generate a config. 
    '''
    config_file = configparser.ConfigParser()
    config_file.add_section('paths')
    paths = ["FILE_ROOT","TELEVISION", "DOCUMENTARIES", "MOVIES", "exit"]
    while len(paths) > 0:
        print("Select path to add: ")
        choice = questions.ask_multichoice(paths)
        if choice == "exit":
            #SAVE CONFIG FILE
            with open(const.PROJECT_ROOT.joinpath("config.ini"),"w") as file_object:
                config_file.write(file_object)
            print("Config file 'person.ini' created")
            exit()
        else:
            path = questions.ask_text_input(f"Enter {choice} path:")
            config_file['paths'][choice] = path
            print(f"Adding to config.ini: [paths]:{choice} = {path}")
            paths.remove(choice)


def match_for_tv(filename):    
    return re.search(r".?((s\d{2}|s\d{4})e\d{2}).?", filename, re.I)

def match_for_altseason(filename):
    return re.search(r'''(?ix)\s*(\d{1,2})(?:of|^)\s*(\d{2})''', filename)

def make_shows_map():
    config = configparser.ConfigParser()
    shows_dict = {}
    for dir_to_scan in [const.TELEVISION_PATH, const.DOCUMENTARIES_PATH]:
        for network_obj in dir_scan(dir_to_scan):
            for show_obj in dir_scan(network_obj):
                if show_obj != "empty":
                    shows_dict[show_obj.name] = show_obj.path
    config['Shows'] = shows_dict
    shows_map_path = const.PROJECT_ROOT.joinpath("shows_map.ini")
    with open(shows_map_path, 'w') as configfile:
        config.write(configfile)

def split_season_episode(season_episode):
    split = (season_episode[0].split('e'))
    season = split[0]
    episode = f"e{split[1]}"
    return season, episode