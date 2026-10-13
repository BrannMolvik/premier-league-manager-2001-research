"""Native EAMail filter caption source files: no invented radio art/UI."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from original_eamail_main_language import load_verified_original_main_eam_language
from original_eamail_filter_labels import (
    OriginalEAMailFilterLabelError,
    ORIGINAL_EAM_FILTER_FONT_PATH,
    ORIGINAL_EAM_FILTER_FONT_LENGTH,
    ORIGINAL_EAM_FILTER_FONT_SHA256,
    NATIVE_EAM_FILTER_FONT_OBJECT,
    NATIVE_EAM_FILTER_TEXT_WRAPPER,
    NATIVE_EAM_FILTER_TEXT_FLAGS,
    load_source_original_eam_filter_labels,
)

SOURCE = Path(__file__).resolve().parent.parent / "original_assets" / "source"


class OriginalEAMailFilterLabelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.language = load_verified_original_main_eam_language(SOURCE)

    def test_original_font_and_ten_english_idx_labels(self):
        import hashlib
        f = (SOURCE / ORIGINAL_EAM_FILTER_FONT_PATH).read_bytes()
        self.assertEqual(len(f), ORIGINAL_EAM_FILTER_FONT_LENGTH)
        self.assertEqual(hashlib.sha256(f).hexdigest(), ORIGINAL_EAM_FILTER_FONT_SHA256)
        result = load_source_original_eam_filter_labels(SOURCE, self.language)
        expected = ("New", "All", "Finance", "Building", "Events",
                    "Player/Team", "Transfer Market", "Youth Team",
                    "Contracts", "FA")
        self.assertEqual(len(result.entries), 10)
        self.assertEqual(tuple(x.text for x in result.entries), expected)
        self.assertTrue(result.native_font.native_line_height() > 0)
        for i, e in enumerate(result.entries):
            self.assertEqual(e.index, i)
            self.assertEqual(e.english_idx_ordinal, 177 + i)
            self.assertEqual(e.panel_local_text_origin, (52, 30 + 30 * i))
            self.assertEqual(e.native_font_va, NATIVE_EAM_FILTER_FONT_OBJECT)
            self.assertEqual(e.native_text_wrapper_va, NATIVE_EAM_FILTER_TEXT_WRAPPER)
            self.assertEqual(e.native_text_flags, NATIVE_EAM_FILTER_TEXT_FLAGS)

    def test_reject_source_font_missing_mutated_or_unverified_language(self):
        with self.assertRaises(OriginalEAMailFilterLabelError):
            load_source_original_eam_filter_labels(SOURCE, None)
        with TemporaryDirectory() as temp:
            folder = Path(temp) / "Fonts"
            folder.mkdir()
            p = Path(temp) / ORIGINAL_EAM_FILTER_FONT_PATH
            with self.assertRaisesRegex(OriginalEAMailFilterLabelError, "Missing"):
                load_source_original_eam_filter_labels(temp, self.language)
            real = (SOURCE / ORIGINAL_EAM_FILTER_FONT_PATH).read_bytes()
            p.write_bytes(real[:-1])
            with self.assertRaisesRegex(OriginalEAMailFilterLabelError, "digest"):
                load_source_original_eam_filter_labels(temp, self.language)
            p.write_bytes(real[:-1] + bytes((real[-1] ^ 0x01,)))
            with self.assertRaisesRegex(OriginalEAMailFilterLabelError, "digest"):
                load_source_original_eam_filter_labels(temp, self.language)
            p.write_bytes(real)
            self.assertEqual(len(
                load_source_original_eam_filter_labels(temp, self.language).entries
            ), 10)

    @unittest.skipUnless(__import__("os").environ.get("FM2001_ORIGINAL_EXE"),
                         "Canonical licensed private original executable unavailable")
    def test_authentic_original_exe_uses_exact_font_slot_and_child_setup(self):
        from gate13_button_source_trace import OriginalPE32
        import os
        import struct
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        self.assertEqual(pe.read(0x5D4FD1, 5), bytes.fromhex("68e0979100"))
        self.assertEqual(pe.read(0x5D4FD7, 5), bytes.fromhex("68b05b9400"))
        self.assertEqual(pe.read(0x5D4FCC, 5), bytes.fromhex("6801200000"))
        self.assertEqual(pe.read(0x5D4F50, 3), bytes.fromhex("83c51e"))
        self.assertEqual(pe.read(0x6042F0, 5), bytes.fromhex("b9e0979100"))
        self.assertEqual(struct.unpack("<I",pe.read(0x5D4F2E,4))[0],0x941430)


if __name__ == "__main__":
    unittest.main()
