"""Guard exactly the previously verified original first-screen extraction plan."""
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest

from gate13_first_screen_selection import (
    CANONICAL_ARCHIVE_SHA256,
    FIRST_SCREEN_ORIGINALS,
    ExpectedSource,
    FirstScreenSelectionError,
    assert_canonical_selection_file,
    read_selection_paths,
    source_selection_file,
    verify_first_screen_selection,
)
from original_button_frames import (
    PSTARTMENU_BUTTON_ATLAS,
    TEAMSELECT_BUTTON_ATLAS,
)
from original_front_end_layout import (
    GLOBAL_BACKGROUND_PATH,
    PSTARTMENU_BACKGROUND_PATH,
    TEAMSELECT_BACKGROUND_PATH,
    TEAMSELECT_HIERARCHY_ANIM_PATH,
    TEAMSELECT_HIERARCHY_BARS_PATH,
)
from original_pstartmenu_resources import (
    GLOBAL_BACKGROUND_SHA256,
    MENU_BACKGROUND_SHA256,
    ZURICH_FONT20_SHA256,
    ENGLISH_STR_SHA256,
    ENGLISH_IDX_SHA256,
)
from original_teamselect_resources import TEAMSELECT_BACKGROUND_SHA256


def synthetic():
    items = (
        ("Art/a.444", b"original art", "iso9660-extracted"),
        ("English.str", b"original language", "disc-image-extracted"),
    )
    assets = tuple(ExpectedSource(name, sha256(data).hexdigest())
                   for name, data, _ in items)
    directory = tempfile.TemporaryDirectory()
    root = Path(directory.name)
    records = []
    for name, data, source in items:
        dest = root / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        records.append({
            "path": name, "sha256": sha256(data).hexdigest(),
            "size": len(data), "source_layer": source,
        })
    report = {
        "source_sha256": "a" * 64,
        "source_size": 123,
        "explicit_paths": [a.path for a in assets],
        "unresolved_explicit_paths": [],
        "only_explicit": True,
        "candidates": records,
    }
    return directory, root, assets, report


class ExactFirstScreenSelectionTests(unittest.TestCase):
    def test_exact_selection_is_only_the_ten_proven_source_paths(self):
        assert_canonical_selection_file(source_selection_file())
        planned = read_selection_paths(source_selection_file())
        self.assertEqual(planned, tuple(a.path for a in FIRST_SCREEN_ORIGINALS))
        self.assertEqual(len(planned), 10)
        self.assertEqual(
            len(set(p.casefold() for p in planned)), len(planned)
        )
        self.assertTrue(all(not p.lower().endswith(
            (".bin", ".iso", ".zip", ".exe", ".cue")
        ) for p in planned))
        self.assertEqual(
            CANONICAL_ARCHIVE_SHA256,
            "677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4",
        )
        known = {a.path: a.sha256 for a in FIRST_SCREEN_ORIGINALS}
        self.assertEqual(known[GLOBAL_BACKGROUND_PATH], GLOBAL_BACKGROUND_SHA256)
        self.assertEqual(known[PSTARTMENU_BACKGROUND_PATH], MENU_BACKGROUND_SHA256)
        self.assertEqual(
            known[TEAMSELECT_BACKGROUND_PATH], TEAMSELECT_BACKGROUND_SHA256
        )
        self.assertEqual(
            known[PSTARTMENU_BUTTON_ATLAS.source_path],
            PSTARTMENU_BUTTON_ATLAS.source_sha256,
        )
        self.assertEqual(
            known[TEAMSELECT_BUTTON_ATLAS.source_path],
            TEAMSELECT_BUTTON_ATLAS.source_sha256,
        )
        self.assertIn(TEAMSELECT_HIERARCHY_ANIM_PATH, known)
        self.assertIn(TEAMSELECT_HIERARCHY_BARS_PATH, known)
        self.assertEqual(
            known["Fonts/Zurich_BdXCn_BT_20pixel.fnt"], ZURICH_FONT20_SHA256
        )
        self.assertEqual(known["English.str"], ENGLISH_STR_SHA256)
        self.assertEqual(known["English.idx"], ENGLISH_IDX_SHA256)

    def test_matching_receipt_and_staged_original_bytes_pass(self):
        temporary, root, assets, report = synthetic()
        with temporary:
            self.assertEqual(
                verify_first_screen_selection(
                    report, root, expected_assets=assets,
                    expected_archive_sha="a" * 64, expected_archive_size=123,
                ),
                tuple(x.path for x in assets),
            )

    def test_mismatched_source_receipt_and_staged_bytes_fail_closed(self):
        temporary, root, assets, report = synthetic()
        options = {"expected_assets": assets,
                   "expected_archive_sha": "a" * 64,
                   "expected_archive_size": 123}
        with temporary:
            altered = dict(report, source_sha256="b" * 64)
            with self.assertRaisesRegex(FirstScreenSelectionError, "canonical"):
                verify_first_screen_selection(altered, root, **options)
            altered = dict(report, only_explicit=False)
            with self.assertRaisesRegex(FirstScreenSelectionError, "broad"):
                verify_first_screen_selection(altered, root, **options)
            altered = dict(report, explicit_paths=["Art/a.444"])
            with self.assertRaisesRegex(FirstScreenSelectionError, "Explicit"):
                verify_first_screen_selection(altered, root, **options)
            changed = [dict(x) for x in report["candidates"]]
            changed[0]["source_layer"] = "zip"
            with self.assertRaisesRegex(FirstScreenSelectionError, "original disc"):
                verify_first_screen_selection(
                    dict(report, candidates=changed), root, **options
                )
            (root / "Art/a.444").write_bytes(b"tampered original")
            with self.assertRaisesRegex(FirstScreenSelectionError, "Staged bytes"):
                verify_first_screen_selection(report, root, **options)

    def test_no_extra_or_duplicate_candidates_or_partially_missing_files(self):
        temporary, root, assets, report = synthetic()
        options = {"expected_assets": assets,
                   "expected_archive_sha": "a" * 64,
                   "expected_archive_size": 123}
        with temporary:
            extra = list(report["candidates"]) + [report["candidates"][0]]
            with self.assertRaisesRegex(FirstScreenSelectionError, "exactly"):
                verify_first_screen_selection(
                    dict(report, candidates=extra), root, **options
                )
            (root / "English.str").unlink()
            with self.assertRaisesRegex(FirstScreenSelectionError, "not staged"):
                verify_first_screen_selection(report, root, **options)


if __name__ == "__main__":
    unittest.main()
