
#!/usr/bin/env python3
#
# filetools
#
# Copyright James Berkheimer. 2022
#

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------
import argparse
import os, sys
import modules.const as const

# --------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------
def main():
    ''' Main function
    This is a starting point of the application execution.
    '''
    print("I am Main()")

    parser = argparse.ArgumentParser(prog="filetools", description="Let's parse some files")

    parser.add_argument(
        "-e",
        "--extractfiles",
        action='store',
        default=os.getcwd(),
        help="Extract specified video files from subdirectories in the current directory")

    parser.add_argument(
        "-re",
        "--rename-episodes",
        action='store',,
        help="Rename eposidic video files")

    parser.add_argument(
        "-rm",
        "--rename-movies",
        action='store',
        help="Rename movie video files")

    parser.add_argument(
        "-a2d",
        "--add-to-dir",
        action='store',
        help="Moves renamed movie files into a directory of the same name")

    parser.add_argument(
        "-ded",
        "--delete-empty-dirs",
        action='store',
        help="Deletes all subdirectories that don't hold a specified video file")


    args = parser.parse_args()

    return const.EXIT_OK

if __name__ == '__main__':
    return_code = main()
    sys.exit(return_code)