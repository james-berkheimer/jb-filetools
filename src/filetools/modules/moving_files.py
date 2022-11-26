#!/usr/local/bin/python3
#
# moving_files.py
#

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------

import os, shutil, traceback
import modules.const as const
import modules.utils as utils


# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------------

def add_to_dir(target_dir:str):
    files = []
    tmpdir = __make_temp_dir(os.path.join(target_dir, "_tmp"))
    for entry in os.scandir(target_dir):
        if entry.is_dir():
            continue
        else:
            files.append(entry.name) 
            
    for f in files:
        if any(x in f for x in const.video_file_extensions):
            newDir = f[:-11]
            newpath = target_dir + newDir
            src = dst = os.path.join(target_dir, f) 
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

def clean_empty_dirs(target_dir:str):
    dirs_to_delete = []
    # for d in __parse_dirs(target_dir):
    for dir_obj in utils.dir_scan(target_dir):
        delete = True
        print("Directory:",dir_obj.name)
        # for f in __parse_files(d):
        for file_obj in utils.dir_scan(dir_obj.path):
            print("  ",file_obj.name)
            if any(x in file_obj.name for x in const.video_file_extensions):
                if "sample-" in file_obj.name:
                    print("   Found file but it's a sample....deleting:", file_obj.name)
                    delete = True
                    break
                print("   Found file....", file_obj.name)
                delete = False
                pass
        if delete:
            dirs_to_delete.append(os.path.join(target_dir, dir_obj.name))
        print("\n")

    # Prompt user.  Initiate delete if yes
    print("Empty directories:")
    for dir_to_delete in dirs_to_delete:    
        print(f"   {dir_to_delete}")
    print("\n")
    user_input = input("Delete directories? y/n?\n")
    if user_input == "y":
        for d in dirs_to_delete:
            print("Deleting directory.....", d)
            try:
                shutil.rmtree(d)
            except OSError as e:
                print("Error: %s : %s" % (d, e.strerror))

def extract_files(target_dir:str):
    for dir_obj in utils.dir_scan(target_dir):
        print(f"Directory: {dir_obj.name}")
        for file_obj in utils.dir_scan(dir_obj.path, True):        
            if any(x in file_obj.name for x in const.file_excludes):
                pass
            elif any(x in file_obj.name for x in const.video_file_extensions):
                new_name = os.path.join(target_dir, file_obj.name)
                print(f"   Extracting....{file_obj.path} to {new_name}")
                shutil.move(file_obj.path, new_name)

# --------------------------------------------------------------------------------
# Private API
# --------------------------------------------------------------------------------

def __make_temp_dir(tmpdir):
    if os.path.exists(tmpdir):
        pass
    else:
        os.mkdir(tmpdir)
    return(tmpdir)