from distutils.command.clean import clean
import os, shutil, traceback, pathlib
import re

def getYear(target_string):
    pattern = re.compile(r"(\d{4})")
    for match in pattern.finditer(target_string):
        if int(match.group(1)) in range(1950,2030):
            return (match.group(1))
    

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


