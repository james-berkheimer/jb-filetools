
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
TRANSMISSION = Path(CONFIG['paths']['TRANSMISSION'])

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
    if parsed_args.cmd:
        for action in parsed_args.cmd:
            print(f"{action} in {parsed_args.Path}")        


if __name__ == '__main__':
    return_code = main()
    sys.exit(return_code)

