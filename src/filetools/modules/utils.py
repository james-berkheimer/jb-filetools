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
    print(f"Let's make a proper season_episode: {season_episode}")
    sortmatch = season_episode.lower().split("of")
    season = f"s{int(sortmatch[0]):02}"
    episode = f"e{int(sortmatch[1]):02}"
    if season and episode:
        return f'{season}{episode}'

def get_config():
    config_file = get_project_root().joinpath("config.ini")
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def get_project_root() -> Path:
    return Path(__file__).parent.parent

def get_season_episode(filename):
    print("Let's extract the season and episode numbers")
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

def match_for_tv(filename):    
    return re.search(r".?((s\d{2}|s\d{4})e\d{2}).?", filename, re.I)

def match_for_altseason(filename):
    return re.search(r'''(?ix)\s*(\d{1,2})(?:of|^)\s*(\d{2})''', filename)

def make_shows_map():
    config = configparser.ConfigParser()
    dirs_to_scan = []
    shows_dict = {}
    for dir_to_scan in dirs_to_scan:
        print(dir_to_scan)
        for network_obj in dir_scan(dir_to_scan):
            for show_obj in dir_scan(network_obj):
                if show_obj != "empty":
                    print(f"{show_obj.name} : {show_obj.path}")
                    shows_dict[show_obj.name] = show_obj.path

    config['Shows'] = shows_dict
    shows_map_path = get_project_root().joinpath("shows_map.ini")
    with open(shows_map_path, 'w') as configfile:
        config.write(configfile)

def read_shows_map():
    shows_dict = {}
    config = configparser.ConfigParser()
    config.read('shows_map.ini')
    for key in config['Shows']:
        print(config['Shows'][key])
        shows_dict[key] = config['Shows'][key]
    return shows_dict

def split_season_episode(season_episode):
    split = (season_episode[0].split('e'))
    season = split[0]
    episode = f"e{split[1]}"
    return season, episode