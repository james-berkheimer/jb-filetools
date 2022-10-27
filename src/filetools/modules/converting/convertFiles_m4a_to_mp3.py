import ffmpeg
import os
import subprocess

# curdir = os.getcwd()
curdir = "C:/Users/James/Music/iTunes/iTunes Media/Music/Zero 7/Simple Science - EP"

filenames = []
for (dirpath, dirnames, filenames) in os.walk(curdir):
    for file in filenames:
        print(os.path.join(curdir, file))
        if '.m4a' in file:
            name, ext = os.path.splitext(file)
            input = os.path.join(dirpath, file)
            output = os.path.join(dirpath, name + '.mp3')
            print("Converting %s to %s" % (input, output))
            subprocess.call([
                'ffmpeg', '-i', input, '-acodec', 'libmp3lame', '-aq', '2',
                output
            ])
