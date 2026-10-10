from pathlib import Path
from types import SimpleNamespace
import os
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

    @unittest.skipUnless(os.environ.get('FM2001_ORIGINAL_EXE'),
                         'authorized canonical executable not supplied')
    def test_canonical_loader_binds_32pixel_path_to_caption_font_object(self):
        from gate13_button_source_trace import OriginalPE32
        # OriginalPE32 rejects noncanonical executable identities by default.
        pe = OriginalPE32.parse(Path(os.environ['FM2001_ORIGINAL_EXE']).read_bytes())
        path = b'Fonts\\Zurich_BdXCn_BT_32pixel.fnt\0'
        self.assertEqual(pe.read(0x839E94, len(path)), path)
        self.assertEqual(pe.read(0x6043AA, 5), b'\x68\x94\x9e\x83\x00')
        self.assertEqual(pe.read(0x6043F2, 5), b'\xb9\xb0\x21\x8f\x00')
        self.assertEqual(pe.read(0x430651, 5), b'\x68\xb0\x21\x8f\x00')


if __name__ == '__main__':
    unittest.main()
