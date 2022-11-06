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
        still_downloading = False
        for f in filenames:
            if '.part' in f:
                print("Found .part file....passing")
                still_downloading = True
                break
            else:
                if '.mkv' in f or '.mp4' in f or '.avi' in f:
                    num_files+=1
                    print(f"   {os.path.join(curdir, d, f)}")
                    to_extract.append(f)
                else:
                    pass
        print(f"numfiles: {num_files}")
        if num_files > 1 or still_downloading == True:
            print("   This is either a series or still downloading")
        else:
            print("...Extracting files")
            for i in to_extract:
                shutil.move(os.path.join(curdir, d, i), os.path.join(curdir, i))
                    

def extract_files(curdir:str):
    for d in parse_dirs(curdir):
        num_files = 0
        to_extract = []
        still_downloading = False
        for f in parse_files(d):
            if '.part' in f:
                print("Found .part file....passing")
                still_downloading = True
                break
            else:
                if '.mkv' in f or '.mp4' in f or '.avi' in f:
                    num_files+=1
                    print(f"   {os.path.join(curdir, d, f)}")
                    to_extract.append(f)
                else:
                    pass
        print(f"numfiles: {num_files}")                
        if num_files > 1 or still_downloading == True:
            print("   This is either a series or still downloading")
        else:
            print("...Extracting files")
            for i in to_extract:
                shutil.move(os.path.join(curdir, d, i), os.path.join(curdir, i))


def find_series_dir(dir):
    pass

def parse_dirs(curdir):
    print(f"Parsing directory: {curdir}")
    dirs = []
    for (dirpath, dirnames, filenames) in os.walk(curdir):
        dirs.extend(dirnames)
    return dirs

def parse_files(dir):
    print(f"Parsing directory: {dir}")
    files = []
    for (dirpath, dirnames, filenames) in os.walk(dir):
        files.extend(filenames)
    return files
        