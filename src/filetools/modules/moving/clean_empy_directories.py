import os, shutil

# Establish globals
curdir = os.getcwd()
root_scan_obj = os.scandir(curdir)
exclude_extensions = [".mkv", ".mp4", ".part", ".avi"]

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
            if [ele for ele in exclude_extensions if(ele in f)]:
                if "sample-" in f:
                    print("   Found file but it's a sample....deleting:", f)
                    delete = True
                    break
                print("   Found file....", f)
                delete = False
                pass
    if delete:
        dirsToDelete.append(os.path.join(curdir, d))
    print("\n")

# for entry1 in root_scan_obj:
#     if entry1.is_dir(): 
#         dir_scan_obj = os.scandir(entry1.path)
#         print(f"Directory: {entry1.name}")
#         for entry2 in dir_scan_obj:
#             delete = True            
#             if entry2.is_file():
#                 elif any(x in entry2.name for x in video_file_extensions):
    
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

