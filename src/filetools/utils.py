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
from pathlib import Path
from typing import List, Union

from . import constants, questions
from .logging import setup_logger

logger = setup_logger(__name__)

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------------
def dir_scan(scan_path: Union[str, Path], get_files: bool = False) -> List[os.DirEntry]:
    """
    Scans a directory and returns a list of directory entries.

    Args:
        scan_path (Union[str, Path]): The path to the directory to scan.
        get_files (bool, optional): If True, return files; if False, return directories. Defaults to False.

    Returns:
        List[os.DirEntry]: A list of directory entries (files or directories) found in the specified path.
    """
    logger.debug(f"Scanning directory: {scan_path}, get_files: {get_files}")

    scan_path = Path(scan_path)
    scan_output = []

    with os.scandir(scan_path) as scan_obj:
        for entry in sorted(scan_obj, key=lambda e: e.name):
            if get_files and entry.is_file():
                scan_output.append(entry)
                logger.debug(f"File found: {entry.name}")
            elif not get_files and entry.is_dir():
                scan_output.append(entry)
                logger.debug(f"Directory found: {entry.name}")

    logger.debug(f"Scan complete. Total entries found: {len(scan_output)}")
    return scan_output


def get_library_names():
    return constants.LIBRARIES.keys()


def get_library_path(library_name):
    return constants.LIBRARIES.get(library_name)


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
            parse_match = match.group(1).lower().split("e")
            match_season = parse_match[0]
            match_episode = f"e{parse_match[1]}"
            return f"{match_season}{match_episode}", alt_naming
        else:
            return None, alt_naming


def get_show_map():
    try:
        show_map = constants.PROJECT_ROOT.joinpath("shows_map.ini")
    except FileNotFoundError:
        print("No show_map.ini found, let's make one...")
        make_shows_map([constants.TELEVISION_PATH, constants.DOCUMENTARIES_PATH])
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
    filtered_matches = []
    for m in matches:
        if int(m) in range(1900, 2030):
            filtered_matches.append(m)
    return filtered_matches[-1]


def match_for_tv(filename):
    return re.search(r".?((s\d{2}|s\d{4})(?:.?)e\d{2}).?", filename, re.I)


def match_for_altseason(filename):
    return re.search(r"""(?ix)\s*(\d{1,2})(?:of|^)\s*(\d{1,2})""", filename)


def make_shows_map():
    config = configparser.ConfigParser()
    shows_dict = {}
    for dir_to_scan in [constants.TELEVISION_PATH, constants.DOCUMENTARIES_PATH]:
        for network_obj in dir_scan(dir_to_scan):
            for show_obj in dir_scan(network_obj):
                if show_obj != "empty":
                    shows_dict[show_obj.name] = show_obj.path
    config["Shows"] = shows_dict
    shows_map_path = constants.PROJECT_ROOT.joinpath("shows_map.ini")
    with open(shows_map_path, "w") as configfile:
        config.write(configfile)


def unique(lst):
    from collections import Counter

    return list(Counter(lst).keys())


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
            episode_name = episode["name"]
            episode_season = f"{episode['seasonNumber']:02}"
            episode_number = f"{episode['number']:02}"
            season_episode = f"s{episode_season}e{episode_number}"
            season_dict[episode_name] = season_episode
        return season_dict
