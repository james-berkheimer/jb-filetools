from genericpath import isdir
import os, shutil, traceback, re


def getSeasonEpisode(filename):
    match_season = re.search(
        r'''(?ix)                 # Ignore case (i), and use verbose regex (x)
        (?:                       # non-grouping pattern
          s|season|^           # e or x or episode or start of a line
          )                       # end non-grouping pattern 
        \s*                       # 0-or-more whitespaces
        (\d{2})                   # exactly 2 digits
        ''', filename)

    match_episode = re.search(
        r'''(?ix)                 # Ignore case (i), and use verbose regex (x)
        (?:                       # non-grouping pattern
          e|x|episode|^           # e or x or episode or start of a line
          )                       # end non-grouping pattern 
        \s*                       # 0-or-more whitespaces
        (\d{2})                   # exactly 2 digits
        ''', filename)
    if match_season and match_episode:
        return match_season.group(0) + match_episode.group(0)


curdir = os.getcwd()
for f in os.listdir(curdir):
    if '.DS_Store' in f:
        print("Deleting: %s" % (os.path.join(curdir, f)))
        os.remove(os.path.join(curdir, f))        
    if 'RARBG.txt' in f:
        print("Deleting: %s" % (os.path.join(curdir, f)))
        os.remove(os.path.join(curdir, f))
    if '.part' in f:
        print("This torrent is still downloading.....passing.")
        pass
    else:
        if os.path.isdir(f):
            print("This is a directory....passing")
            pass
        else:
            fk, hdr = "", ""
            if "2160p" in f.split('.'):
                fk = "-4K"
            if "HDR" in f.split('.'):
                hdr = "-HDR"
            season_episode = getSeasonEpisode(f)
            try:
                season_episode = getSeasonEpisode(f)
                print("Season_Episode: " + str(season_episode))
                details = f.split(season_episode)
                print(details)
                episode_name = details[0].replace(".", " ")
                file_extension = details[1].split(".")[-1]
                new_name = f"{episode_name} - {season_episode.upper()}{fk}{hdr}.{file_extension}"
                print(new_name)
                os.rename(os.path.join(curdir, f), os.path.join(curdir, new_name))
            except:
                # print(traceback.format_exc())
                print("Not an episodic file....passing")

