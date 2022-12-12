
#!/usr/bin/env python3
#
# args.py
#
# Copyright James Berkheimer. 2022
#
# --------------------------------------------------------------------------------
# imports
# --------------------------------------------------------------------------------
import argparse
from pathlib import Path
import modules.utils as utils

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------
CONFIG = utils.get_config()
CURDIR = Path(CONFIG['paths']['TRANSMISSION'])

# Establish args PARSER
PARSER = argparse.ArgumentPARSER(prog="filetools", 
                                    description="Let's parse some files",
                                    allow_abbrev=False)

# --------------------------------------------------------------------------------
# Construct Args
# --------------------------------------------------------------------------------
PARSER.add_argument(
    "Path",
    metavar='path',
    type=str,
    nargs='?',
    default=CURDIR,
    help='path to directory to be worked on'
)

PARSER.add_argument(
    "-e",
    "--extract_files",
    dest='cmd',
    const='extract_files',
    action='append_const',
    help="Extract specified video files from subdirectories in the current directory")

PARSER.add_argument(
    "-r",
    "--raname_files",
    dest='cmd',
    const='rename_files',
    action='append_const',
    help="Rename files to standardized formats")

PARSER.add_argument(
    "-atd",
    "--add_to_dir",
    dest='cmd',
    const='add_to_dir',
    action='append_const',
    help="Moves renamed movie files into a directory of the same name")

PARSER.add_argument(
    "-ded",
    "--delete_empty_dirs",        
    dest='cmd',
    const='delete_empty_dirs',
    action='append_const',
    help="Deletes all subdirectories that don't hold a specified video file")

PARSER.add_argument(
    "-mf",
    "--move-files",        
    dest='cmd',
    const='move_files',
    action='append_const',
    help="Moves renamed files to the filesystem")

# --------------------------------------------------------------------------------
# Parse Args
# --------------------------------------------------------------------------------
parsed_args = PARSER.parse_args()