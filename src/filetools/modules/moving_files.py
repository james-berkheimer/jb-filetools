#!/usr/local/bin/python3
#
# moving_files.py
#

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------

import os, shutil, traceback


# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------
video_file_extensions = [".mkv", ".mp4", ".avi"]
file_extentions_to_clean = [".mkv", ".mp4", ".part", ".avi"]

# --------------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------------

def add_to_dir(curdir:str):
    files = []
    tmpdir = __make_temp_dir(os.path.join(curdir, "_tmp"))
    for entry in os.scandir(curdir):
        if entry.is_dir():
            continue
        else:
            files.append(entry.name) 
            
    for f in files:
        if any(x in f for x in video_file_extensions):
            newDir = f[:-11]
            newpath = curdir + newDir
            src = dst = os.path.join(curdir, f) 
            dst = os.path.join(newpath, f)
            print("Moving: %s to %s" % (src, dst))      
            toTmp = os.path.join(tmpdir, newDir)
            print("Moving: %s to %s" % (newpath, toTmp))
            try:
                os.mkdir(newpath)
                shutil.move(src, dst)
                shutil.move(newpath, toTmp, copy_function = shutil.copytree)
            except:
                print(traceback.format_exc())

        print("\n")

def clean_empty_dirs(curdir):
    dirsToDelete = []
    for d in __parse_dirs(curdir):
        delete = True
        print("Directory:",d)
        for f in __parse_files(d):
            print("  ",f)
            if any(x in f for x in file_extentions_to_clean):
                if "sample-" in f:
                    print("   Found file but it's a sample....deleting:", f)
                    delete = True
                    break
                print("   Found file....", f)
                delete = False
                pass
        if delete:
            dirsToDelete.append(os.path.join(curdir, d))
        print("\n")

    # Prompt user.  Initiate delete if yes
    print("Empty directories:")
    for d in dirsToDelete:    
        print("",d)
    print("\n")

    userInput = input("Delete directories? y/n?\n")
    if userInput == "y":
        for d in dirsToDelete:
            print("Deleting directory.....", d)
            try:
                shutil.rmtree(d)
            except OSError as e:
                print("Error: %s : %s" % (d, e.strerror))

def extract_files(curdir:str):
    for d in __parse_dirs(curdir):
        num_files = 0
        to_extract = []
        still_downloading = False
        for f in __parse_files(d):
            if '.part' in f:
                print("Found .part file....passing")
                still_downloading = True
                break
            else:
                if any(x in f for x in video_file_extensions):
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



# --------------------------------------------------------------------------------
# Private API
# --------------------------------------------------------------------------------

def __make_temp_dir(tmpdir):
    if os.path.exists(tmpdir):
        pass
    else:
        os.mkdir(tmpdir)
    return(tmpdir)

def __parse_dirs(curdir):
    print(f"Parsing directory: {curdir}")
    dirs = []
    for (dirpath, dirnames, filenames) in os.walk(curdir):
        dirs.extend(dirnames)
    return dirs

def __parse_files(dir):
    print(f"Parsing directory: {dir}")
    files = []
    for (dirpath, dirnames, filenames) in os.walk(dir):
        files.extend(filenames)
    return files
        