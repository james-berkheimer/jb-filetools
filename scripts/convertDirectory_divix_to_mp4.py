import ffmpeg
import os
import subprocess

curdir = os.getcwd()
# curdir = "T:\The New Yankee Workshop\Season 01"

dirs = []
for (dirpath, dirnames, filenames) in os.walk(curdir):
    dirs.extend(dirnames)
    break

for d in dirs:
    print(os.path.join(curdir, d))
    for (dirpath, dirnames, filenames) in os.walk(os.path.join(curdir, d)):
        print("Dirpath: %s" % (dirpath))
        for file in filenames:
            if '.divx' or '.avi' in file:
                name, ext = os.path.splitext(file)
                input = os.path.join(dirpath, file)
                output = os.path.join(dirpath, name + '.mp4')
                print("Converting %s to %s" % (input, output))
                subprocess.call(['ffmpeg', '-i', input, '-acodec', 'aac', 'vcodec', 'libx264', output])
