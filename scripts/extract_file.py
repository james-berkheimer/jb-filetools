import os, shutil

# ffmpeg -i Alice.Doesnt.Live.Here.Anymore.1974.1080p.WEBRip.x265-RARBG.mp4 -map_metadata -1 -c:v copy -c:a copy test.mp4

curdir = os.getcwd()

dirs = []
for (dirpath, dirnames, filenames) in os.walk(curdir):
    dirs.extend(dirnames)
    break

for d in dirs:
    print(d)
    for (dirpath, dirnames, filenames) in os.walk(d):
        for f in filenames:
            if '.part' in f:
                print("This torrent is still downloading....passing")
                pass
            else:
                if '.mkv' in f:
                    print(os.path.join(curdir, d, f))
                    shutil.move(os.path.join(curdir, d, f), os.path.join(curdir, f))
                if '.mp4' in f:
                    print(os.path.join(curdir, d, f))
                    shutil.move(os.path.join(curdir, d, f), os.path.join(curdir, f))
                if '.avi' in f:
                    print(os.path.join(curdir, d, f))
                    shutil.move(os.path.join(curdir, d, f), os.path.join(curdir, f))
        break
