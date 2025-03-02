#!/usr/bin/env python3
#
# filetools
#
# Copyright James Berkheimer. 2022
#

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------
import logging
import sys
from pathlib import Path

import click

from . import naming_files
from .logger import setup_logger
from .moving_files import clean_empty_dirs, extract_from_src, move_movie_files, move_show_files
from .utils import dir_scan, make_shows_map, sort_media


# --------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------
@click.command()
@click.argument("path", required=False, type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option(
    "-e",
    "--extract-files",
    is_flag=True,
    help="Extract specified video files from subdirectories in the current directory",
)
@click.option("-rn", "--rename-files", is_flag=True, help="Rename files to standardized formats")
@click.option("-m", "--move-files", is_flag=True, help="Moves renamed files to the filesystem")
@click.option(
    "-ded",
    "--delete-empty-dirs",
    is_flag=True,
    help="Deletes all subdirectories that don't hold a specified video file",
)
@click.option(
    "-d", "--debug", is_flag=True, help="Run in debug mode: Log actions without renaming or moving files"
)
@click.option("-v", "--verbose", count=True, help="Increase verbosity level (use -v, -vv, or -vvv)")
def cli(path, extract_files, rename_files, move_files, delete_empty_dirs, debug, verbose):
    """CLI function
    This is a starting point of the application execution.
    """
    # Set the logging level based on the verbosity
    if verbose == 1:
        log_level = logging.DEBUG
    elif verbose >= 2:
        log_level = logging.NOTSET
    else:
        log_level = logging.INFO

    log = setup_logger(name="filetools", level=log_level)
    log.debug("Python version: %s", sys.version)

    # make/Update show_map
    make_shows_map()

    work_dir = Path(path) if path else Path.cwd()
    log.info("Path to work on: %s", work_dir)

    if extract_files:
        log.info("")
        log.info("---------------------------------- Extract Files -----------------------------------")
        log.info("")
        extract_from_src(work_dir, debug)
        log.info("\n")

    if rename_files:
        log.info("")
        log.info("----------------------------------- Rename Files ------------------------------------")
        log.info("")
        naming_files.rename_files(work_dir, debug)
        log.info("\n")

    if move_files:
        log.info("")
        log.info("------------------------------ Move Files To Libraries ------------------------------")
        log.info("")
        movies, shows = sort_media(dir_scan(work_dir, True))
        move_movie_files(movies, work_dir, debug)
        move_show_files(shows, work_dir, debug)
        log.info("\n")

    if delete_empty_dirs:
        log.info("")
        log.info("--------------------------------- Delete Empty Dirs ---------------------------------")
        log.info("")
        clean_empty_dirs(work_dir, debug)
        log.info("\n")


def main():
    cli()
