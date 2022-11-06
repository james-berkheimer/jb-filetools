
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
import os, sys, pathlib
import modules.const as const
import modules.moving_files as moving_files
import modules.naming_files as naming_files
import modules._testing.test as test

# --------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------
def main():
    ''' Main function
    This is a starting point of the application execution.
    '''
    print("I am Main()")
    curdir = os.getcwd()

    parser = argparse.ArgumentParser(prog="filetools", description="Let's parse some files")
    # subparser = parser.add_subparsers(dest='command')

    parser.add_argument(
        "-e",
        "--extractfiles",
        nargs='?',
        const=curdir,
        help="Extract specified video files from subdirectories in the current directory")

    parser.add_argument(
        "-re",
        "--rename-episodes",
        type=str,
        nargs='?',
        const=curdir,
        help="Rename eposidic video files")

    parser.add_argument(
        "-rm",
        "--rename-movies",
        type=str,
        nargs='?',
        const=curdir,
        help="Rename movie video files")

    parser.add_argument(
        "-atd",
        "--add-to-dir",
        type=str,
        nargs='?',
        const=curdir,
        help="Moves renamed movie files into a directory of the same name")

    parser.add_argument(
        "-ded",
        "--delete-empty-dirs",
        type=str,
        nargs='?',
        const=curdir,
        help="Deletes all subdirectories that don't hold a specified video file")

    args = parser.parse_args()

    for arg in vars(args):
        print(arg, getattr(args, arg))
       

    # Let's enact the tools

    if "extractfiles" in args:
        if os.path.isdir(args.extractfiles):
            # test.hello1(args.extractfiles)
            moving_files.extract_files(args.extractfile)
        else:
            print(f"{args.extractfiles} is not a valid directory path")

    if "rename_episodes" in args:
        if os.path.isdir(args.extractfiles):
            # test.hello2(args.extractfiles)
            naming_files.rename_episodes(args.rename_episodes)
        else:
            print(f"{args.extractfiles} is not a valid directory path")

    if "rename_movies" in args:
        if os.path.isdir(args.extractfiles):
            # test.hello2(args.extractfiles)
            naming_files.rename_movies(args.rename_movies)
        else:
            print(f"{args.extractfiles} is not a valid directory path")
   
    return const.EXIT_OK

# def checkpath(path):
#     pass

if __name__ == '__main__':
    return_code = main()
    sys.exit(return_code)

