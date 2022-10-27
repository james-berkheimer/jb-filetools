import ffmpeg
import os
import subprocess

curdir = os.getcwd()
# curdir = "D:\Downloads\TV\Sonic Youth"

dirs = []
for (dirpath, dirnames, filenames) in os.walk(curdir):
    dirs.extend(dirnames)
    break

for d in dirs:
    print(os.path.join(curdir, d))
    for (dirpath, dirnames, filenames) in os.walk(os.path.join(curdir, d)):
        print("Dirpath: %s" % (dirpath))
        for file in filenames:
            if '.m4a' in file:
                name, ext = os.path.splitext(file)
                input = os.path.join(dirpath, file)
                output = os.path.join(dirpath, name + '.mp3')
                print("Converting %s to %s" % (input, output))
                subprocess.call([
                    'ffmpeg', '-i', input, '-acodec', 'libmp3lame', '-aq', '2',
                    output
                ])
