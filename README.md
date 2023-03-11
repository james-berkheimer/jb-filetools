
jb-filetools
===========

A collection of tools built on Python 3.10 used to help manage downloaded files and direct them to a local file server.

Options
=========

* **clean_empty_directories** - Delete directories that are empty of media or .part files
* **extract_file** - Extracts all media files from all directories in the current directory.
* **rename_files** - Renames all files.  Conforms to standards i.e. (show_s01e01.mkv, movie_(2022).mkv)
* **move_files** - Moves the files from their download location to their proper locations on the media server.


  -h, --help            show this help message and exit
  -e, --extract-files   Extract specified video files from subdirectories in the current directory
  -rn, --rename-files   Rename files to standardized formats
  -m, --move-files      Moves renamed files to the filesystem
  -ded, --delete-empty-dirs
                        Deletes all subdirectories that don't hold a specified video file
  -mc, --make-config    Prints out the config.ini
  -fn, --fix-names      Fix file names to match them to the show maps


