"""Recovered original PStartMenu event/label/glyph integration tests.

The ordinary CI path uses synthetic format fixtures. Optional tests compare
real original licensed Zurich font and English STR/IDX bytes by exact hashes.
"""
import hashlib
import os
from pathlib import Path
import struct
import unittest

from ea_font import EAFont
from ea_language_strings import parse_language_pair
from original_front_end_layout import PSTARTMENU_ACTIONS
from original_pstartmenu_labels import prepare_original_pstartmenu_captions
from test_ea_font import build_fixture
from test_ea_language_strings import make_str


class OriginalPStartMenuCaptionTests(unittest.TestCase):
    def test_labels_come_from_idx_mapping_not_string_table_order(self):
        font = EAFont.from_bytes(build_fixture())
        strings, index = parse_language_pair(
            make_str(("B", "AB", "A", "BA")),
            struct.pack("<7H", 1, 3, 2, 0, 0, 2, 0),
        )
        captions = prepare_original_pstartmenu_captions(font, strings, index)
        self.assertEqual(
            tuple((label.event, label.source_idx_position, label.original_text)
                  for label in captions),
            ((1, 0, "AB"), (2, 1, "BA"), (3, 2, "A"), (4, 6, "B")),
        )
        self.assertEqual(
            tuple(label.control_rect for label in captions),
            tuple(action.rect for action in PSTARTMENU_ACTIONS),
        )
        self.assertEqual(
            tuple((label.glyph_mask.width, label.glyph_mask.height)
                  for label in captions),
            ((3, 2), (4, 2), (2, 2), (2, 2)),
        )
        self.assertEqual(
            captions[0].glyph_mask.alpha,
            bytes((255, 0, 0, 0, 255, 64)),
        )
        self.assertEqual(
            tuple((item.native_style, item.normal_color_16,
                   item.alternate_group_color_16)
                  for item in captions),
            ((0x2000, 0xFFFF, 0x0000),) * 4,
        )
        self.assertEqual(captions[0].native_color_for_group(0), 0xFFFF)
        self.assertEqual(captions[0].native_color_for_group(1), 0x0000)
        self.assertEqual(captions[0].native_color_for_group(2), 0xFFFF)
        with self.assertRaises(ValueError):
            captions[0].native_color_for_group(3)

    def test_missing_mandatory_idx_is_rejected_not_replaced_by_guessed_text(self):
        font = EAFont.from_bytes(build_fixture())
        strings, index = parse_language_pair(
            make_str(("AB",)), struct.pack("<3H", 0, 0, 0)
        )
        with self.assertRaises(IndexError):
            prepare_original_pstartmenu_captions(font, strings, index)

    @unittest.skipUnless(
        os.environ.get("FM2001_ORIGINAL_FONT_20")
        and os.environ.get("FM2001_ORIGINAL_LANGUAGE_DIR"),
        "Original licensed source bytes intentionally excluded from CI",
    )
    def test_opt_in_real_source_zurich_and_english_first_screen_masks(self):
        font_bytes = Path(os.environ["FM2001_ORIGINAL_FONT_20"]).read_bytes()
        english = Path(os.environ["FM2001_ORIGINAL_LANGUAGE_DIR"])
        str_bytes = (english / "English.str").read_bytes()
        idx_bytes = (english / "English.idx").read_bytes()
        self.assertEqual(
            hashlib.sha256(font_bytes).hexdigest(),
            "47e3b21f07a3013ba19d257f31e1e876c9b03856c930a8fa5fe58103974ed166",
        )
        self.assertEqual(
            hashlib.sha256(str_bytes).hexdigest(),
            "aa594a55ad95c672b69184e5f3ff8349e41fe95b48c5dcb3c8fcfe2bcdf5b601",
        )
        self.assertEqual(
            hashlib.sha256(idx_bytes).hexdigest(),
            "98fcbe9e9eb5d1068739a58cc46aaaedab2749b2c65460861b18beeac7361db1",
        )
        captions = prepare_original_pstartmenu_captions(
            EAFont.from_bytes(font_bytes), *parse_language_pair(str_bytes, idx_bytes)
        )
        self.assertEqual(
            tuple((item.event, item.original_text,
                   item.glyph_mask.width, item.glyph_mask.height)
                  for item in captions),
            ((1, "Continue", 63, 19),
             (2, "Start New Game", 117, 19),
             (3, "Load Game", 81, 19),
             (4, "Quit to Windows", 120, 19)),
        )
        self.assertEqual(
            tuple((item.line_origin_x, item.line_origin_y) for item in captions),
            ((234, 480), (33, 480), (399, 480), (205, 510)),
        )
        self.assertEqual(
            tuple(item.clip_rect for item in captions),
            tuple(action.rect for action in PSTARTMENU_ACTIONS),
        )
        self.assertEqual(
            tuple(hashlib.sha256(item.glyph_mask.alpha).hexdigest()
                  for item in captions),
            (
                "6af205e0d5ee04c063770438919a3418b18cd8e91ab615bdc8bb21a7e9137ae2",
                "4b44e56c14963f59e5cdd6343f124e6674c45b96ccf8bc810480001da0462e60",
                "53d3f619416f77f04cac75543287d1ca23095f70de4417ec2fcdad492a7dc804",
                "98458644c31c322d1bd6e64e20f59bc6e8c50291b3eef4b61a0da4c9fe91e421",
            ),
        )


if __name__ == "__main__":
    unittest.main()
