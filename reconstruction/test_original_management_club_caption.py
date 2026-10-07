from pathlib import Path
from types import SimpleNamespace
import unittest

from original_management_club_caption import (
    CLUB_CAPTION_RECT, CLUB_CAPTION_FLAGS, CLUB_CAPTION_FONT_PATH,
    load_verified_management_club_font, management_club_caption_pixels,
)


class FakeFont:
    def measure_text(self, text):
        return len(text) * 10

    def native_line_height(self):
        return 37

    def render_text_alpha(self, text):
        width = self.measure_text(text)
        return SimpleNamespace(width=width, height=37, alpha=bytes([255]) * width * 37)


class ManagementClubCaptionTests(unittest.TestCase):
    def test_native_right_alignment_centering_and_control_clip(self):
        self.assertEqual(CLUB_CAPTION_RECT, (172, 1, 378, 32))
        self.assertEqual(CLUB_CAPTION_FLAGS, 0x2102)
        x, y, width, height, rgba = management_club_caption_pixels(FakeFont(), 'Southport', '')
        self.assertEqual((x, y, width, height), (460, 1, 90, 32))
        self.assertEqual(rgba, bytes([255]) * 90 * 32 * 4)

    def test_explicit_custom_caption_precedes_club_name_and_unknown_is_withheld(self):
        self.assertEqual(management_club_caption_pixels(FakeFont(), 'Southport', 'X')[:4],
                         (540, 1, 10, 32))
        self.assertIsNone(management_club_caption_pixels(FakeFont(), 'Southport', None))

    def test_long_native_caption_clips_to_control_not_an_invented_font_size(self):
        self.assertEqual(management_club_caption_pixels(FakeFont(), 'X' * 60, '')[:4],
                         CLUB_CAPTION_RECT)

    def test_exact_packaged_font_and_real_southport_pixels(self):
        source = Path(__file__).resolve().parents[1] / 'original_assets/source'
        font = load_verified_management_club_font(source)
        self.assertEqual(CLUB_CAPTION_FONT_PATH, 'Fonts/Zurich_BdXCn_BT_32pixel.fnt')
        self.assertEqual(font.measure_text('Southport'), 90)
        pixels = management_club_caption_pixels(font, 'Southport', '')
        self.assertEqual(pixels[:4], (460, 1, 90, 32))
        self.assertGreater(sum(pixels[4][3::4]), 0)


if __name__ == '__main__':
    unittest.main()
