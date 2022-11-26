#!/usr/bin/env python3
#
# modules/const.py
#
# This file will store constants used in this project
#

import os
from typing import Dict, List

# Script return codes
EXIT_OK: int = 0
EXIT_ERROR: int = 1

files_to_delete = ['.DS_Store', 'RARBG.txt', ".srt", ".nfo", ".sfv", "Thumbs.db", ".txt"]
video_file_extensions = [".mkv", ".mp4", ".mpeg", ".mpg", ".mov", ".avi"]
file_excludes = [".part"]
