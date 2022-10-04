import re

txt = "American.Masters.S34E08.Laura.Ingalls.Wilder.Prairie.to.Page.1080p.WEBRip.x264-BAE.mkv"
txt2 = "BBC.RICL.2020.Planet.Earth.A.Users.Guide.1of3.Engine.Earth.1080p.HDTV.x265.AAC.MVGroup.org.mkv"
txt3 = "Hell.The.History.of.Norwegian.Black.Metal.1of4.720p.x264.AAC.MVGroup.Forum.mkv"


def getSeasonEpisode(filename):
    match = re.search(r'''(?ix)(?:s|season|^)\s*(\d{2})''', filename)

    if match:
        return match.group(0)