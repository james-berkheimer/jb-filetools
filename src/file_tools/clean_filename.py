from distutils.command.clean import clean
import os, shutil, traceback, pathlib
import re

def getYear(target_string):
    matches = re.findall(r"[0-9]{4}", target_string)
    filteredMatches = []
    for m in matches:
        if int(m) in range(1900,2030):
            filteredMatches.append(m)
    return(filteredMatches[-1])  
    

curdir = os.getcwd()
for f in os.listdir(curdir):
    if '.DS_Store' in f:
        pass
    if os.path.isdir(f):
        print("This is a directory....passing\n")
        pass
    else:
        print("Let's rename.....", f)
        file_extension = pathlib.Path(f).suffix
        print("   ", file_extension)
        woExt = f.split(file_extension)[0]
        print("   ", woExt)
        cleanName = " ".join(woExt.split('.')).title()
        print("   ", cleanName)
        year = getYear(cleanName)
        print("   ", year)
        newName = cleanName.split(year)[0] + "(" + year + ")" + file_extension
        print("   ", newName)
        try:
            os.rename(os.path.join(curdir, f), os.path.join(curdir, newName))
        except:
            print(traceback.format_exc())
        print("\n")


