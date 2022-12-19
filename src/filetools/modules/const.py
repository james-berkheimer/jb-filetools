#!/usr/bin/env python
#
# modules/const.py
#
# This file will store globally used variables that don't change.
#

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------
from pathlib import Path
import configparser

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent
CURRENT_WORKING_DIR = Path.cwd()

try:
    config_file = PROJECT_ROOT.joinpath("config.ini")
    __config = configparser.ConfigParser()
    __config.read(config_file)
except:
    print("No congif.ini found, let's make one...") 

FILES_TO_DELETE = [".DS_Store","RARBG.txt",".srt",".nfo",".sfv","humbs.db",".txt"]
VIDEO_FILE_EXTENSIONS = [".mkv",".mp4",".mpeg",".mpg",".mov",".avi"]
FILE_EXCLUDES = [".part"]

#Paths
FILE_ROOT = Path(__config['paths']['file_root'])
TELEVISION_PATH = Path(__config['paths']['television'])
DOCUMENTARIES_PATH = Path(__config['paths']['documentaries'])
MOVIES_PATH = Path(__config['paths']['movies'])
