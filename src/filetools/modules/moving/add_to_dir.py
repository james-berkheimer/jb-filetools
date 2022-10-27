import os, shutil, traceback

curdir = os.getcwd()
tmpDir = os.path.join(curdir, "_tmp")
if os.path.exists(tmpDir):
    pass
else:
    os.mkdir(tmpDir)
file_extensions = [".mkv", ".mp4", ".avi"]
files = []
for entry in os.scandir(curdir):
    if entry.is_dir():
        continue
    else:
        files.append(entry.name)        

for f in files:
    if [ele for ele in file_extensions if(ele in f)]:
        newDir = f[:-11]
        newpath = curdir + newDir
        src = dst = os.path.join(curdir, f) 
        dst = os.path.join(newpath, f)
        print("Moving: %s to %s" % (src, dst))      
        toTmp = os.path.join(tmpDir, newDir)
        print("Moving: %s to %s" % (newpath, toTmp))
        try:
            os.mkdir(newpath)
            shutil.move(src, dst)
            shutil.move(newpath, toTmp, copy_function = shutil.copytree)
        except:
            print(traceback.format_exc())

    print("\n")
