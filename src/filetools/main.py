
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
import modules.moving_files as moving_files
import modules.naming_files as naming_files

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
        default=curdir,
        help="Extract specified video files from subdirectories in the current directory")

    parser.add_argument(
        "-r",
        "--rename",
        type=str,
        nargs='?',
        default=curdir,
        help="Rename files to standardized formats")

    parser.add_argument(
        "-atd",
        "--add-to-dir",
        type=str,
        nargs='?',
        default=curdir,
        help="Moves renamed movie files into a directory of the same name")

    parser.add_argument(
        "-ded",
        "--delete-empty-dirs",
        type=str,
        nargs='?',
        default=curdir,
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

    if "rename" in args:
        if os.path.isdir(args.extractfiles):
            # test.hello2(args.extractfiles)
            naming_files.rename_files(args.rename)
        else:
            print(f"{args.rename} is not a valid directory path")
            
    return const.EXIT_OK

# def checkpath(path):
#     pass

if __name__ == '__main__':
    return_code = main()
    sys.exit(return_code)

