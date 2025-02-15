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

from . import naming_files, utils
from .constants import CURRENT_WORKING_DIR
from .logging import setup_logger
from .moving_files import clean_empty_dirs, extract_from_src, move_to_libraries


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
@click.option("-fn", "--fix-names", is_flag=True, help="Fix file names to match them to the show maps")
@click.option("-v", "--verbose", count=True, help="Increase verbosity level (use -v, -vv, or -vvv)")
def cli(path, extract_files, rename_files, move_files, delete_empty_dirs, fix_names, verbose):
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

    logger = setup_logger(name="filetools", level=log_level)
    logger.info("Python version: %s", sys.version)

    # make/Update show_map
    utils.make_shows_map()

    work_dir = Path(path) if path else CURRENT_WORKING_DIR
    logger.info("Path to work on: %s", work_dir)

    if extract_files:
        logger.info("----------- extract_files -----------")
        extract_from_src(work_dir)
        logger.info("\n")

    if rename_files:
        logger.info("----------- rename_files -----------")
        naming_files.rename_files(work_dir)
        logger.info("\n")

    if move_files:
        logger.info("----------- move_to_libraries -----------")
        move_to_libraries(work_dir)
        logger.info("\n")

    if delete_empty_dirs:
        logger.info("----------- delete_empty_dirs -----------")
        clean_empty_dirs(work_dir)
        logger.info("\n")

    if fix_names:
        logger.info("----------- fix_names -----------")
        naming_files.fix_names(work_dir)
        logger.info("\n")


def main():
    cli()


if __name__ == "__main__":
    main()
