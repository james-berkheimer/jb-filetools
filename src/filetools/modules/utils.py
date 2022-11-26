#!/usr/bin/env python
#
# modules/utils.py
#
# This file will store globally used functions used in this project
#
import os

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