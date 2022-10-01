import os, shutil

curdir = os.getcwd()
file_extensions = [".mkv", ".mp4", ".avi"]
files = []
for entry in os.scandir(curdir):
    if entry.is_dir():
        continue
    else:
        files.append(entry.name)
        

# print("......",curdir)
for f in files:
    if [ele for ele in file_extensions if(ele in f)]:
        newpath = curdir + f[:-11]
        print(newpath)
        # src = curdir + '\\' + f
        src = dst = os.path.join(curdir, f) 
        # dst = newpath + '\\' + f        
        dst = os.path.join(newpath, f)
        print("Moving: %s to %s" % (src, dst))
        os.mkdir(newpath)
        shutil.move(curdir + '\\' + f, newpath + '\\' + f)

    print("\n")
