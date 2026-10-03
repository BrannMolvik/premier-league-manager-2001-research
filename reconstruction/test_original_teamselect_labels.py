from hashlib import sha256
from pathlib import Path
import unittest

from ea_font import EAFont
from ea_language_strings import parse_language_pair
from original_teamselect_labels import (
    TEAMSELECT_ACTION_FONT_PATH, TEAMSELECT_ACTION_FONT_SHA256,
    prepare_original_teamselect_captions,
)


class TeamSelectCaptionTests(unittest.TestCase):
    def test_canonical_labels_font_geometry_clipping_and_button_colors(self):
        root = Path(__file__).resolve().parents[1] / "original_assets/source"
        data = (root / TEAMSELECT_ACTION_FONT_PATH).read_bytes()
        self.assertEqual(sha256(data).hexdigest(), TEAMSELECT_ACTION_FONT_SHA256)
        font = EAFont.from_bytes(data)
        strings, index = parse_language_pair(
            (root / "English.str").read_bytes(), (root / "English.idx").read_bytes(),
        )
        captions = prepare_original_teamselect_captions(font, strings, index)
        self.assertEqual(font.native_line_height(), 32)
        self.assertEqual([(c.event, c.source_idx_position, c.original_text,
                           c.glyph_mask.width, c.line_origin_x, c.line_origin_y)
                          for c in captions],
                         [(0x29, 2487, "MAIN MENU", 97, 251, 301),
                          (0x2A, 2485, "START GAME", 102, 450, 301)])
        for caption in captions:
            self.assertEqual(caption.clip_rect, caption.control_rect)
            self.assertTrue(any(caption.glyph_mask.alpha))
            self.assertEqual([caption.native_color_for_group(g) for g in range(3)],
                             [0xFFFF, 0, 0xFFFF])
