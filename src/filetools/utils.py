#!/usr/bin/env python
#
# modules/utils.py
#
# This file will store globally used functions used in this project
#

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------
import configparser
import os
import re

import const as const
import questions as questions

# import tvdb_v4_official
# from thefuzz import fuzz
# from thefuzz import process

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------
# try:
#     TVDB = tvdb_v4_official.TVDB("21f6c950-88b4-4491-bdb6-4f93f3c2d414", pin="1X0KXTWN")
# except:
#     print("!! UNABLE TO CONNECT TO TVDB !!")
# --------------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------------
def dir_scan(scan_path:str, getfiles=False):
    scan_obj = os.scandir(scan_path)
    scan_obj_sorted = sorted(scan_obj, key=lambda e: e.name)
    scan_output = []
    for root_scan_entry in scan_obj_sorted:
        if not getfiles:
            if root_scan_entry.is_dir():
                scan_output.append(root_scan_entry)
        else:
            if root_scan_entry.is_file():
                scan_output.append(root_scan_entry)
    scan_obj.close()
    return scan_output

def get_season_episode(filename):
    alt_naming = False
    # Search for episodes with season/episode names of #of#
    alt_season_match = match_for_altseason(filename)
    if alt_season_match:
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
    except FileNotFoundError:
        print("No show_map.ini found, let's make one...")
        make_shows_map([const.TELEVISION_PATH, const.DOCUMENTARIES_PATH])
    import configparser
    config = configparser.ConfigParser()
    config.read(show_map)
    return config

def get_year(target_string):
    try:
        matches = re.findall(r"[0-9]{4}", target_string)
    except FileNotFoundError:
        print("NO YEAR MATCHES")
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
    config_file.optionxform = str
    config_file.add_section('paths')
    paths = ["file_root","television", "documentaries", "movies", "exit"]
    while len(paths) > 0:
        print("Select path to add: ")
        choice = questions.ask_multichoice(paths)
        if choice == "exit":
            #SAVE CONFIG FILE
            with open(const.PROJECT_ROOT.joinpath("config.ini"),"w") as file_object:
                config_file.write(file_object)
            print("Config file 'config.ini' created")
            exit()
        else:
            path = questions.ask_text_input(f"Enter {choice} path:")
            config_file['paths'][choice] = path
            print(f"Adding to config.ini: [paths]:{choice} = {path}")
            paths.remove(choice)

def match_for_tv(filename):
    return re.search(r".?((s\d{2}|s\d{4})(?:.?)e\d{2}).?", filename, re.I)

def match_for_altseason(filename):
    return re.search(r'''(?ix)\s*(\d{1,2})(?:of|^)\s*(\d{1,2})''', filename)

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

def unique(lst):
    from collections import Counter
    return (list(Counter(lst).keys()))


# --------------------------------------------------------------------------------
# Private Methods
# --------------------------------------------------------------------------------
def __dict_merge(dict1, dict2):
    res = dict1 | dict2
    return res

def __get_episode_data(season):
    if season is not None:
        season_dict = {}
        for episode in season["episodes"]:
            episode_name = episode['name']
            episode_season = f"{episode['seasonNumber']:02}"
            episode_number = f"{episode['number']:02}"
            season_episode = f"s{episode_season}e{episode_number}"
            season_dict[episode_name] = season_episode
        return(season_dict)

# def __get_series_data(series_id):
#     series = TVDB.get_series_extended(series_id)
#     series_data = {}
#     for season in sorted(series["seasons"], key=lambda x: (x["type"]["name"], x["number"])):
#         if season["type"]["name"] == "Aired Order":
#             season = TVDB.get_season_extended(season["id"])
#             season_data = __get_episode_data(season)
#             series_data = __dict_merge(series_data, season_data)
#     return series_data