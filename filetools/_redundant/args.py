
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

from .. import constants

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Construct Args
# --------------------------------------------------------------------------------
# Establish args PARSER
PARSER = argparse.ArgumentParser(prog="filetools",
                                    description="Let's parse some files",
                                    allow_abbrev=False)
PARSER.add_argument(
    "root",
    metavar='root',
    type=str,
    nargs='?',
    default=constants.FILE_ROOT,
    help='path to directory to be worked on'
)

PARSER.add_argument(
    "-e",
    "--extract-files",
    dest='extractfiles',
    const='extract_files',
    action='append_const',
    help="Extract specified video files from subdirectories in the current directory")

PARSER.add_argument(
    "-rn",
    "--rename-files",
    dest='renamefiles',
    const='rename_files',
    action='append_const',
    help="Rename files to standardized formats")

PARSER.add_argument(
    "-m",
    "--move-files",
    dest='movefiles',
    const='move_files',
    action='append_const',
    help="Moves renamed files to the filesystem")

PARSER.add_argument(
    "-ded",
    "--delete-empty-dirs",
    dest='deleteemptydirs',
    const='delete_empty_dirs',
    action='append_const',
    help="Deletes all subdirectories that don't hold a specified video file")

PARSER.add_argument(
    "-mc",
    "--make-config",
    dest='makeconfig',
    action='store_true',
    help="Prints out the config.ini")

PARSER.add_argument(
    "-fn",
    "--fix-names",
    dest='fixnames',
    const='fix_names',
    action='append_const',
    help="Fix file names to match them to the show maps")



# --------------------------------------------------------------------------------
# Parse Args
# --------------------------------------------------------------------------------
parsed_args = PARSER.parse_args()