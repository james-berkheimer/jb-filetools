#
# show_matching.py
#
# Match a show name parsed from a filename against the shows already in the library.
#

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------
import difflib
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------
_YEAR_SUFFIX = re.compile(r"_(\d{4})$")
_FUZZY_CUTOFF = 0.8
_FUZZY_LIMIT = 3

# --------------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------------


@dataclass(frozen=True)
class ShowMatch:
    """Result of matching a show name against the library.

    Attributes:
        path: The show folder when the match is unambiguous, otherwise None
        candidates: Possible show folders to offer the user when there is no clear match
    """

    path: Path | None = None
    candidates: list[Path] = field(default_factory=list)


class ShowCatalog:
    """Index of library show folders that tolerates naming differences.

    Matching tries, in order:
        1. The same name once punctuation is ignored ("beavis_and_butt_head" finds
           "beavis_and_butt-head", "1923_2022" finds "1923_(2022)")
        2. The same name ignoring a trailing year, when that is unambiguous
           ("ludwig_2024" finds "ludwig", "the_paper" finds "the_paper_2025")
        3. Close spellings, returned only as candidates for the user to confirm
    """

    def __init__(self: "ShowCatalog", shows: Mapping[str, str | Path]) -> None:
        self._by_name: dict[str, Path] = {}
        self._by_base: dict[str, list[str]] = {}
        for name, path in shows.items():
            self.add(name, path)

    def add(self: "ShowCatalog", name: str, path: str | Path) -> None:
        """Add a show folder to the catalog."""
        key = normalize_show_name(name)
        if key in self._by_name:
            return
        self._by_name[key] = Path(path)
        self._by_base.setdefault(_split_year(key)[0], []).append(key)

    def match(self: "ShowCatalog", show_name: str) -> ShowMatch:
        """Find the library folder for a show name parsed from a filename."""
        key = normalize_show_name(show_name)
        if key in self._by_name:
            return ShowMatch(path=self._by_name[key])

        base, year = _split_year(key)
        same_base = self._by_base.get(base, [])
        if len(same_base) == 1 and _years_compatible(year, _split_year(same_base[0])[1]):
            return ShowMatch(path=self._by_name[same_base[0]])
        if same_base:
            return ShowMatch(candidates=[self._by_name[k] for k in sorted(same_base)])

        close = difflib.get_close_matches(base, self._by_base, n=_FUZZY_LIMIT, cutoff=_FUZZY_CUTOFF)
        return ShowMatch(candidates=[self._by_name[k] for b in close for k in sorted(self._by_base[b])])


def normalize_show_name(name: str) -> str:
    """Lowercase a show name and collapse all punctuation and spacing to single underscores."""
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


# --------------------------------------------------------------------------------
# Private Functions
# --------------------------------------------------------------------------------


def _split_year(key: str) -> tuple[str, str | None]:
    """Split a normalized name into (base, year), e.g. "ludwig_2024" -> ("ludwig", "2024")."""
    match = _YEAR_SUFFIX.search(key)
    if match and match.start() > 0:
        return key[: match.start()], match.group(1)
    return key, None


def _years_compatible(wanted: str | None, existing: str | None) -> bool:
    """Two names can refer to the same show unless both carry a year and the years differ."""
    return wanted is None or existing is None or wanted == existing
