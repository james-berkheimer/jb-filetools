
jb-filetools
===========

A collection of tools built on Python 3.10 used to help manage downloaded files and direct them to a local file server.

# INSTALLATION
    Simple install in any convinent.  Run with a Python call i.e. python jb-filetools/src/filetools/main.py
    
    Future versions will use a distribution format and be callable on it's own.

# Options
    {EMPTY}                     Running the command without any flags will print out the current working directory.
    {PATH}                      Adding a file path after the command and before the flags will set the directory path to be worked on.
    -h, --help                  show this help message and exit.
    -e, --extract-files         Extract specified video files from subdirectories in the current directory.
    -rn, --rename-files         Rename files to standardized formats i.e. (show_s01e01.mkv, movie_(2022).mkv).
    -m, --move-files            Moves renamed files to the filesystem.
    -ded, --delete-empty-dirs   Deletes all subdirectories that don't hold a specified video file.
    -mc, --make-config          Prints out the config.ini.
    -fn, --fix-names            Fix file names to match them to the show maps.
    




