if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        globals()[sys.argv[1]]()

import errno
import logging
import os
import re
import shutil
import time
from pathlib import Path
from typing import Optional

import pathspec

from filetools.logger import setup_logger
from filetools.questions import ask_bool
from filetools.utils import dir_scan, make_shows_map

import os
import shutil
import time
from pathlib import Path

log = setup_logger(name="filetools", level=logging.INFO)


def test1() -> None:
    filename = "test_move.mkv"
    src = Path("/mnt/media/transmission/_saved") / filename
    dest = Path("/mnt/media") / filename

    # Start timer
    start = time.perf_counter()

    try:
        os.rename(src, dest)
        method = "os.rename"
    except OSError as e:
        if e.errno != os.errno.EXDEV:
            raise
        try:
            with open(src, "rb") as fsrc, open(dest, "wb") as fdst:
                os.sendfile(fdst.fileno(), fsrc.fileno(), 0, os.stat(src).st_size)
            os.unlink(src)
            method = "os.sendfile"
        except Exception:
            shutil.copyfile(src, dest)
            os.unlink(src)
            method = "shutil.copyfile + unlink"

    elapsed = time.perf_counter() - start
    print(f"{method} completed in {elapsed:.3f} seconds")
