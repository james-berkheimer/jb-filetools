import re

txt = "American.Masters.S34E108.Laura.Ingalls.Wilder.Prairie.to.Page.1080p.WEBRip.x264-BAE.mkv"
txt2 = "BBC.RICL.2020.Planet.Earth.A.Users.Guide.1of3.Engine.Earth.1080p.HDTV.x265.AAC.MVGroup.org.mkv"
txt3 = "Hell.The.History.of.Norwegian.Black.Metal.1of4.720p.x264.AAC.MVGroup.Forum.mkv"
txt4 = "Besieged.Fortresses.Series.1.Part.3.The.Daunting.Fortress.of.Richard.the.Lionheart.1080p.HDTV.x264.AAC.MVGroup.org.mp4"


def getSeasonEpisode(filename):
    match_season = re.search(
        r'''(?ix)                 # Ignore case (i), and use verbose regex (x)
        (?:                       # non-grouping pattern
          s|season|^           # e or x or episode or start of a line
          )                       # end non-grouping pattern 
        \s*                       # 0-or-more whitespaces
        (\d{3})                   # exactly 2 digits
        ''', filename)

    match_episode = re.search(
        r'''(?ix)                 # Ignore case (i), and use verbose regex (x)
        (?:                       # non-grouping pattern
          e|x|episode|^           # e or x or episode or start of a line
          )                       # end non-grouping pattern 
        \s*                       # 0-or-more whitespaces
        (\d{3})                   # exactly 2 digits
        ''', filename)
    if match_season and match_episode:
        return match_season.group(0) + match_episode.group(0)


def getSeries(filename):
    match_of = re.search(r'''(?ix)(\d+)of(\d+)''', filename)
    if match_of:
        return match_of.group(0)


# season_episode = getSeasonEpisode(txt)
# details = txt.split(season_episode)
# episode_name = details[0].replace(".", " ")
# file_extension = details[1].split(".")[-1]
# filename = episode_name + "- " + season_episode + "." + file_extension
# print(filename)

print(getSeries(txt3))