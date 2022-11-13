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
file_excludes = [".part"]

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

def extract_files(root_dir:str):
    for d in __dir_scan(root_dir):
        print(f"Directory: {d.name}")
        for f in __dir_scan(d.path, True):        
            if any(x in f.name for x in file_excludes):
                pass
            elif any(x in f.name for x in video_file_extensions):
                print(f"   Extracting....{f.path} to {os.path.join(root_dir, f.name)}")
                shutil.move(f.path, os.path.join(root_dir, f.name))



# --------------------------------------------------------------------------------
# Private API
# --------------------------------------------------------------------------------

def __dir_scan(scan_path:str, getfiles=False):
    scan_obj = os.scandir(scan_path)
    scan_output = []
    for root_scan_entry in scan_obj:
        if getfiles == False:
            if root_scan_entry.is_dir():
                scan_output.append(root_scan_entry)
        else:
            if root_scan_entry.is_file():
                scan_output.append(root_scan_entry)
    scan_obj.close()
    return scan_output

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
        