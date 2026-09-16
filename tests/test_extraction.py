from pathlib import Path

from filetools.moving_files import _get_empty_dirs, _get_files_to_extract, extract_from_src


def make(root: Path, *relative_paths: str) -> None:
    for relative in relative_paths:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()


def test_season_pack_subdirectories_are_extracted(tmp_path):
    # Regression: files inside "Show/Season NN/" were never found.
    make(
        tmp_path,
        "Show A/Season 01/Show.A.S01E01.mkv",
        "Show A/Season 02/Show.A.S02E01.mkv",
        "Show A/Show.A.nfo",
    )

    assert _get_files_to_extract(tmp_path) == {
        tmp_path / "Show A/Season 01/Show.A.S01E01.mkv": tmp_path / "Show.A.S01E01.mkv",
        tmp_path / "Show A/Season 02/Show.A.S02E01.mkv": tmp_path / "Show.A.S02E01.mkv",
    }


def test_folder_still_downloading_anywhere_is_skipped(tmp_path):
    make(tmp_path, "Show A/Season 01/Show.A.S01E01.mkv", "Show A/Season 02/Show.A.S02E01.mkv.part")
    assert _get_files_to_extract(tmp_path) == {}


def test_names_containing_part_are_not_downloading(tmp_path):
    # Regression: ".part" was matched anywhere in the name, so "The.Party" never extracted.
    make(tmp_path, "the.party.1968.1080p/the.party.1968.1080p.mkv")
    assert list(_get_files_to_extract(tmp_path).values()) == [tmp_path / "the.party.1968.1080p.mkv"]


def test_samples_and_in_progress_are_not_extracted(tmp_path):
    make(
        tmp_path,
        "Movie.2024/Movie.2024.mkv",
        "Movie.2024/Sample/movie.2024.mkv",
        "Movie.2024/movie.2024.trailer.mkv",
        "_in-progress/Other.2024.mkv",
    )
    assert _get_files_to_extract(tmp_path) == {
        tmp_path / "Movie.2024/Movie.2024.mkv": tmp_path / "Movie.2024.mkv",
    }


def test_name_collisions_never_overwrite(tmp_path):
    make(
        tmp_path,
        "Pack/Season 01/Episode.mkv",
        "Pack/Season 02/Episode.mkv",
        "Other/Existing.mkv",
        "Existing.mkv",
    )
    assert _get_files_to_extract(tmp_path) == {
        tmp_path / "Pack/Season 01/Episode.mkv": tmp_path / "Episode.mkv",
    }


def test_extract_from_src_moves_files(tmp_path):
    make(tmp_path, "Show A/Season 01/Show.A.S01E01.mkv")
    extract_from_src(tmp_path)
    assert (tmp_path / "Show.A.S01E01.mkv").exists()
    assert not (tmp_path / "Show A/Season 01/Show.A.S01E01.mkv").exists()


def test_extract_from_src_debug_moves_nothing(tmp_path):
    make(tmp_path, "Show A/Season 01/Show.A.S01E01.mkv")
    extract_from_src(tmp_path, debug=True)
    assert (tmp_path / "Show A/Season 01/Show.A.S01E01.mkv").exists()
    assert not (tmp_path / "Show.A.S01E01.mkv").exists()


def test_unextracted_season_pack_is_not_empty(tmp_path):
    # Regression: a season pack looked empty because only the top level was checked.
    make(tmp_path, "Show A/Season 01/Show.A.S01E01.mkv", "Show A/Show.A.nfo")
    assert _get_empty_dirs(tmp_path) == []


def test_empty_dirs(tmp_path):
    make(
        tmp_path,
        "Extracted/Season 01/Show.A.nfo",
        "OnlySample/Sample/movie.sample.mkv",
        "_saved/DONOTDELETE.part",
        "_in-progress/whatever.nfo",
        "Downloading/Season 01/Show.S01E01.mkv.part",
    )
    assert _get_empty_dirs(tmp_path) == [tmp_path / "Extracted", tmp_path / "OnlySample"]


MKV_HEADER = b"\x1a\x45\xdf\xa3" + b"\x00" * 60


def test_extensionless_video_is_extracted(tmp_path):
    (tmp_path / "Pack").mkdir()
    (tmp_path / "Pack/Show S01E06 1080p WEB-DL x265 NTb").write_bytes(MKV_HEADER)

    assert list(_get_files_to_extract(tmp_path).values()) == [
        tmp_path / "Show S01E06 1080p WEB-DL x265 NTb"
    ]


def test_folder_holding_only_an_extensionless_video_is_not_empty(tmp_path):
    # Without content detection this folder looked empty and would have been deleted.
    (tmp_path / "Pack").mkdir()
    (tmp_path / "Pack/Show S01E06 1080p WEB-DL x265 NTb").write_bytes(MKV_HEADER)

    assert _get_empty_dirs(tmp_path) == []
