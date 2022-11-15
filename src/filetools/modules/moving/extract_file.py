#!/usr/bin/env python

import os, shutil

root_dir = os.getcwd()
video_file_extensions = [".mkv", ".mp4", ".avi"]
file_excludes = [".part"]

def dir_scan(scan_path:str, getfiles=False):
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

for d in dir_scan(root_dir):
    print(f"Directory: {d.name}")
    if d.name == "_testing":
        pass
    for f in dir_scan(d.path, True):        
        if any(x in f.name for x in file_excludes):
            pass
        elif any(x in f.name for x in video_file_extensions):
            print(f"   Extracting....{f.path} to {os.path.join(root_dir, f.name)}")
            shutil.move(f.path, os.path.join(root_dir, f.name))

