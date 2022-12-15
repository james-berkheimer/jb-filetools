
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
import modules.args as args
import modules.moving_files as moving_files
import modules.naming_files as naming_files
import modules.utils as utils

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------
utils.make_shows_map() #Make and/or update the shows_map.ini
CONFIG = utils.get_config()
FILE_ROOT = Path(CONFIG['paths']['FILE_ROOT'])

# --------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------
def main():
    ''' Main function
    This is a starting point of the application execution.
    '''
    
    # Get tool arguments
    parsed_args = args.parsed_args
    print(f"Path to work on: {parsed_args.Path}")
    if parsed_args.cmd1:
        for action in parsed_args.cmd1:
            print(f"{action}")      

    if parsed_args.cmd2:          
        for action in parsed_args.cmd2:
            print(f"{action}")   

    if parsed_args.cmd3:
        for action in parsed_args.cmd3:
            print(f"{action}")        

    if parsed_args.cmd4:
        for action in parsed_args.cmd4:
            print(f"{action}")        


if __name__ == '__main__':
    return_code = main()
    sys.exit(return_code)

