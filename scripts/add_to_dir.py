import os, shutil

curdir = os.getcwd()
mypath = 'T:\\'
files = []
for (dirpath, dirnames, filenames) in os.walk(curdir):
    files.extend(filenames)

for f in files:
    print(f)
    if (f == ".DS_Store") or (f == "._.DS_Store"):
        print("pass")
    else:
        newpath = curdir + f[:-11]
        print(newpath)
        os.mkdir(newpath)
        src = curdir + '\\' + f
        dst = newpath + '\\' + f
        shutil.move(curdir + '\\' + f, newpath + '\\' + f)
        print("Moving: %s to %s" % (src, dst))
