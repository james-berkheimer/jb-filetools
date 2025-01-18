
#!/usr/bin/env python3
#
# filetools
#
# Copyright James Berkheimer. 2022
#

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------
import sys
from pathlib import Path

import args as args
import moving_files as moving_files
import naming_files as naming_files
import utils as utils


# --------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------
def main():
    ''' Main function
    This is a starting point of the application execution.
    '''
    print("Python version")
    print (sys.version)
    # make/Update show_map
    utils.make_shows_map()

    # Get tool arguments
    parsed_args = args.parsed_args
    root_dir = Path(parsed_args.root)
    print(f"Path to work on: {root_dir}")
    if parsed_args.extractfiles:
        for action in parsed_args.extractfiles:
            print(f"----------- {action} -----------")
            moving_files.extract_files(root_dir)
            print("\n")

    if parsed_args.renamefiles:
        for action in parsed_args.renamefiles:
            print(f"----------- {action} -----------")
            naming_files.rename_files(root_dir)
            print("\n")

    if parsed_args.movefiles:
        for action in parsed_args.movefiles:
            print(f"----------- {action} -----------")
            moving_files.move_files(root_dir)
            print("\n")

    if parsed_args.deleteemptydirs:
        for action in parsed_args.deleteemptydirs:
            print(f"----------- {action} -----------")
            moving_files.clean_empty_dirs(root_dir)
            print("\n")

    if parsed_args.fixnames:
        for action in parsed_args.fixnames:
            print(f"----------- {action} -----------")
            naming_files.fix_names(root_dir)
            print("\n")

    if parsed_args.makeconfig:
        print("calling make config")
        utils.make_config()
# Main
if __name__ == '__main__':
    return_code = main()
    sys.exit(return_code)

