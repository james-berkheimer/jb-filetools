import os, shutil, traceback, pathlib
import re


curdir = os.getcwd()
for f in os.listdir(curdir):
    if '.DS_Store' in f:
        pass
    if os.path.isdir(f):
        print("This is a directory....passing")
        pass
    else:
        print("Let's rename")
        file_extension = pathlib.Path(f).suffix
        try:
            woExt = f.split(file_extension)[0]
            new_name = (" ".join(woExt.split('.')).title()) + "." + file_extension
            print(new_name)
            os.rename(os.path.join(curdir, f), os.path.join(curdir, new_name))
        except:
            print(traceback.format_exc())
