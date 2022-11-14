from genericpath import isdir
import os, shutil, traceback, re

files_to_delete = ['.DS_Store', 'RARBG.txt']
video_file_extensions = [".mkv", ".mp4", ".avi"]

def getSeasonEpisode(filename):
    alt_naming = False
    # Search for episodes with season/episode names of #of#
    initial_match = re.search(r'''(?ix)\s*(\d{1})(?:of|^)\s*(\d{2})''', filename)
    if initial_match:
        print(f"Found alt season naming in {filename}")
        alt_naming = True
        return initial_match.group(0), alt_naming
    # Search for traditional S##E## naming
    else:
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
            return f"{match_season.group(0)}{match_episode.group(0)}", alt_naming

def fix_season_episode(match):
    print("In fix_season_episode")
    sortmatch = match.lower().split("of")
    season = f'S{int(sortmatch[0]):02}'
    episode = f'E{int(sortmatch[1]):02}'
    if season and episode:
        return f'{season}{episode}'

def __rename(match, fsplit):
    print(f"Season_Episode: {str(match)}")
    print(fsplit)    
    fk, hdr = "", ""
    if "2160p" in fsplit:
        fk = "-4K"
    if "HDR" in fsplit:
        hdr = "-HDR"
    fsplit0 = fsplit[0].split('.')
    fsplit1 = fsplit[1].split('.')
    print(f"-----{fsplit0}------")
    if 'BBC' in fsplit0:
        fsplit0.remove('BBC')
    episode_name = " ".join(fsplit0).rstrip()
    file_extension = fsplit1[-1]
    return f"{episode_name} - {match.upper()}{fk}{hdr}.{file_extension}"
    


curdir = os.getcwd()
for f in os.listdir(curdir):
    try:              
        if f in files_to_delete:
            print("Deleting: %s" % (os.path.join(curdir, f)))
            os.remove(os.path.join(curdir, f))
        if os.path.splitext(f)[1] in video_file_extensions:
            if os.path.isdir(f):
                print("This is a directory....passing")
                pass
            else:
                season_episode, alt_naming = getSeasonEpisode(f)
                print(season_episode)
                fsplit = f.split(season_episode)
                if alt_naming:
                    new_name = __rename(fix_season_episode(season_episode), fsplit)
                else:                    
                    new_name = __rename(season_episode, fsplit)
                os.rename(os.path.join(curdir, f), os.path.join(curdir, new_name))
        else:
            print(f"{f}.....is not valid for renaming")
    except Exception as e:
        print(str(e))
        pass


