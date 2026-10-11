"""Original byte-identical direct Inbox PBg source asset, no guessed sprite state."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main

from original_pbg_back3_source import (
    OriginalPBgBack3SourceError,
    PBG_EAMAIL_BACK3_SOURCE_PATH,
    PBG_EAMAIL_BACK3_NATIVE_ATLAS,
    PBG_EAMAIL_BACK3_NATIVE_CROP,
    verified_original_pbg_back3_bytes,
)


class OriginalPBgBack3SourceTests(TestCase):
    def test_imported_original_button_four_frames_and_exact_bytes(self):
        root = Path(__file__).resolve().parents[1] / "original_assets/source"
        raw = verified_original_pbg_back3_bytes(root)
        self.assertEqual(len(raw), 5932)
        self.assertEqual(PBG_EAMAIL_BACK3_NATIVE_ATLAS, (40, 380))
        self.assertEqual(PBG_EAMAIL_BACK3_NATIVE_CROP, (40, 95))
        self.assertEqual(
            PBG_EAMAIL_BACK3_NATIVE_ATLAS[1] //
            PBG_EAMAIL_BACK3_NATIVE_CROP[1], 4,
        )

    def test_missing_and_corrupt_files_fail_without_substitute(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaises(OriginalPBgBack3SourceError):
                verified_original_pbg_back3_bytes(root)
            target = root / PBG_EAMAIL_BACK3_SOURCE_PATH
            target.parent.mkdir(parents=True)
            target.write_bytes(b"not original source")
            with self.assertRaisesRegex(OriginalPBgBack3SourceError, "differ"):
                verified_original_pbg_back3_bytes(root)


if __name__ == "__main__":
    main()
