
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
CURDIR = Path(CONFIG['paths']['FILE_ROOT'])

# Establish args PARSER
PARSER = argparse.ArgumentParser(prog="filetools", 
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
    dest='cmd1',
    const='extract_files',
    action='append_const',
    help="Extract specified video files from subdirectories in the current directory")

PARSER.add_argument(
    "-r",
    "--rename_files",
    dest='cmd2',
    const='rename_files',
    action='append_const',
    help="Rename files to standardized formats")

PARSER.add_argument(
    "-m",
    "--move-files",        
    dest='cmd3',
    const='move_files',
    action='append_const',
    help="Moves renamed files to the filesystem")

PARSER.add_argument(
    "-ded",
    "--delete_empty_dirs",        
    dest='cmd4',
    const='delete_empty_dirs',
    action='append_const',
    help="Deletes all subdirectories that don't hold a specified video file")


# --------------------------------------------------------------------------------
# Parse Args
# --------------------------------------------------------------------------------
parsed_args = PARSER.parse_args()