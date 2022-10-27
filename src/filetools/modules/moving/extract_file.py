#!/usr/bin/env python

import os, shutil

curdir = os.getcwd()
dirs = []
for (dirpath, dirnames, filenames) in os.walk(curdir):
    dirs.extend(dirnames)
    break

for d in dirs:
    print(d)
    for (dirpath, dirnames, filenames) in os.walk(d):
        for f in filenames:
            if '.part' in f:
                print("This torrent is still downloading....passing")
                pass
            else:
                if '.mkv' in f:
                    print(os.path.join(curdir, d, f))
                    shutil.move(os.path.join(curdir, d, f), os.path.join(curdir, f))
                if '.mp4' in f:
                    print(os.path.join(curdir, d, f))
                    shutil.move(os.path.join(curdir, d, f), os.path.join(curdir, f))
                if '.avi' in f:
                    print(os.path.join(curdir, d, f))
                    shutil.move(os.path.join(curdir, d, f), os.path.join(curdir, f))
        break

def extract_file(curdir):
    dirs = []
    for (dirpath, dirnames, filenames) in os.walk(curdir):
        dirs.extend(dirnames)
        break
    for d in dirs:
        for (dirpath, dirnames, filenames) in os.walk(d):
            for f in filenames:
                if '.part' in f:
                    print("This torrent is still downloading....passing")
                    pass
                else:
                    if '.mkv' in f:
                        print(os.path.join(curdir, d, f))
                        shutil.move(os.path.join(curdir, d, f), os.path.join(curdir, f))
                    if '.mp4' in f:
                        print(os.path.join(curdir, d, f))
                        shutil.move(os.path.join(curdir, d, f), os.path.join(curdir, f))
                    if '.avi' in f:
                        print(os.path.join(curdir, d, f))
                        shutil.move(os.path.join(curdir, d, f), os.path.join(curdir, f))
            break
