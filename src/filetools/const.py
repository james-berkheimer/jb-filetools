#!/usr/bin/env python
#
# modules/const.py
#
# This file will store globally used variables that don't change.
#

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------
import configparser
from pathlib import Path

import utils as utils

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent
CURRENT_WORKING_DIR = Path.cwd()
FILES_TO_DELETE = [".DS_Store","RARBG.txt",".srt",".nfo",".sfv","Thumbs.db",
                   ".txt","Sample.mkv", "Trailer.mkv",".jpg", ".vtx"]
VIDEO_FILE_EXTENSIONS = [".mkv",".mp4",".mpeg",".mpg",".mov",".avi"]
FILE_EXCLUDES = [".part", "Sample.mkv", "sample.mkv", "Trailer.mkv", ".DS_Store"]
DOC_SHOWS = ["Horizon", "Frontline", "American Experience", "NOVA"]

try:
    config_file = PROJECT_ROOT.joinpath("config.ini")
    __config = configparser.ConfigParser()
    __config.read(config_file)
    #Paths
    FILE_ROOT = Path(__config['paths']['file_root'])
    TELEVISION_PATH = Path(__config['paths']['television'])
    DOCUMENTARIES_PATH = Path(__config['paths']['documentaries'])
    MOVIES_PATH = Path(__config['paths']['movies'])
except configparser.Error:
    print("No congif.ini found, let's make one...")
    utils.make_config()




