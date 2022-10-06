import os, shutil

# Establish globals
curdir = os.getcwd()
file_extensions = [".mkv", ".mp4", ".part", ".avi"]

# parse directories and identify those that are empty
dirs = []
dirsToDelete = []
for (dirpath, dirnames, filenames) in os.walk(curdir):
    dirs.extend(dirnames)
    break

for d in dirs:
    delete = True
    print("Directory:",d)
    for (dirpath, dirnames, filenames) in os.walk(d):
        for f in filenames:
            print("  ",f)
            if [ele for ele in file_extensions if(ele in f)]:
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

