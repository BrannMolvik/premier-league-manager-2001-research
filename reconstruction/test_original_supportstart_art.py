"""Exact original SupportStart file integrity, not live GUI acceptance."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main

from original_supportstart_art import (
    ORIGINAL_SUPPORTSTART_ART_SPECS,
    ORIGINAL_SUPPORTSTART_BUTTON_FIRST_FRAME_SOURCE,
    ORIGINAL_SUPPORTSTART_IMAGE_SIZE,
    ORIGINAL_SUPPORTSTART_ROW_BAR_FRAME_SOURCE,
    OriginalSupportStartArtError,
    verified_original_supportstart_art,
)


class OriginalSupportStartArtTests(TestCase):
    def test_source_complete_original_six_art_headers_and_sha_checks(self):
        root = Path(__file__).resolve().parents[1]
        art = verified_original_supportstart_art(root)
        self.assertEqual(len(art), 6)
        self.assertEqual(set(art), {s.relative_source for s in ORIGINAL_SUPPORTSTART_ART_SPECS})
        self.assertEqual(sum(map(len, art.values())), 216020)
        self.assertEqual(ORIGINAL_SUPPORTSTART_IMAGE_SIZE, (760, 500))
        self.assertEqual(ORIGINAL_SUPPORTSTART_ROW_BAR_FRAME_SOURCE, (0,0,306,17))
        self.assertEqual(ORIGINAL_SUPPORTSTART_BUTTON_FIRST_FRAME_SOURCE, (0,0,30,30))

    def test_missing_original_files_never_fall_back_to_fake_art(self):
        with TemporaryDirectory() as d:
            with self.assertRaisesRegex(OriginalSupportStartArtError, "unavailable"):
                verified_original_supportstart_art(Path(d))

    def test_tampered_original_source_fails_checksum_before_decode(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            first = ORIGINAL_SUPPORTSTART_ART_SPECS[0]
            original = (Path(__file__).resolve().parents[1]
                        / "original_assets" / "source" / first.relative_source)
            target = root / "original_assets" / "source" / first.relative_source
            target.parent.mkdir(parents=True)
            b = bytearray(original.read_bytes())
            b[8] ^= 0x40
            target.write_bytes(b)
            with self.assertRaisesRegex(OriginalSupportStartArtError, "mismatch"):
                verified_original_supportstart_art(root)


if __name__ == "__main__":
    main()
