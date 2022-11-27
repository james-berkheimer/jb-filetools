
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
    print(f"Curdir: {curdir}")

    parser = argparse.ArgumentParser(prog="filetools", 
                                     description="Let's parse some files",
                                     allow_abbrev=False)
    # subparser = parser.add_subparsers(dest='command')

    parser.add_argument(
        "Path",
        metavar='path',
        type=str,
        nargs='?',
        default=curdir,
        help='path to directory to be worked on'
    )

    parser.add_argument(
        "-e",
        "--extractfiles",
        help="Extract specified video files from subdirectories in the current directory")

    parser.add_argument(
        "-r",
        "--rename",
        help="Rename files to standardized formats")

    parser.add_argument(
        "-atd",
        "--add-to-dir",
        help="Moves renamed movie files into a directory of the same name")

    parser.add_argument(
        "-ded",
        "--delete-empty-dirs",
        help="Deletes all subdirectories that don't hold a specified video file")

    args = parser.parse_args()

    for arg in vars(args):
        print(arg, getattr(args, arg))
    print("\n")

    # Let's enact the tools
    print(f"Path to work on: {args.Path}")

    # if "extractfiles" in args:
    #     print(f"Extracting files from: {args.extractfiles}")

    # if "rename" in args:
    #     print(f"Renaming files from: {args.extractfiles}")

        
    # if "rename" in args:
    #     if os.path.isdir(args.extractfiles):
    #         test.hello2(args.extractfiles)
    #         # naming_files.rename_files(args.rename)
    #     else:
    #         print(f"{args.rename} is not a valid directory path")
            
    return const.EXIT_OK

if __name__ == '__main__':
    return_code = main()
    sys.exit(return_code)

