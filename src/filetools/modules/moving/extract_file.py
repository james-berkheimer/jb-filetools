#!/usr/bin/env python

import os, shutil

curdir = os.getcwd()
dirs = []
for (dirpath, dirnames, filenames) in os.walk(curdir):
    dirs.extend(dirnames)
    break

for d in dirs:
    print(f"Directory: {d}")
    for (dirpath, dirnames, filenames) in os.walk(d):
        num_files = 0
        to_extract = []
        for f in filenames:
            if '.part' in f:
                print("This torrent is still downloading....passing")
                pass
            else:
                if '.mkv' in f or '.mp4' in f or '.avi' in f:
                    num_files+=1
                    print(f"   {os.path.join(curdir, d, f)}")
                    to_extract.append(f)
                else:
                    pass
        print(f"numfiles: {num_files}")
        if num_files < 2:
            print("...Extracting files")
            for i in to_extract:
                shutil.move(os.path.join(curdir, d, i), os.path.join(curdir, i))
        else:
            print("Multi-episode....passing")
                    

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
