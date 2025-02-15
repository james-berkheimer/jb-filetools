from .constants import MOVIE_LIBRARIES, SHOW_LIBRARIES


def test1():
    print(f"SHOW_LIBRARIES: {SHOW_LIBRARIES}")
    print(f"Show Paths: {list(SHOW_LIBRARIES.values())}")
    libraries = list(MOVIE_LIBRARIES.keys())
    if len(libraries) > 1:
        for library in libraries:
            print(library, MOVIE_LIBRARIES[library])
    else:
        print(libraries[0], MOVIE_LIBRARIES[libraries[0]])
