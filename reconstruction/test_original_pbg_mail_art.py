"""Native PBg direct Inbox authentic 40x95 *initial* sprite source regression."""
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase, main
from unittest.mock import patch

from ea444_decoder import EA444DecodedImage
from original_pbg_mail_art import (
    OriginalPBgMailArt, OriginalPBgMailArtError,
    PBG_MAIL_NATIVE_CONTROL_DEFAULT_FLAGS,
    PBG_MAIL_NATIVE_SOURCE_IDLE_RECT,
    native_pbg_mail_bitmap_frame, native_pbg_mail_idle_bitmap_pixels,
    load_verified_original_pbg_mail_art,
)
from original_game_host import OriginalGameTkHost
from original_pbg_back3_source import verified_original_pbg_back3_bytes


class NativePBgMailIdleTests(TestCase):
    def test_original_40x95_source_crop_and_byte_identical_atlas(self):
        original = Path(__file__).resolve().parents[1] / "original_assets/source"
        self.assertEqual(len(verified_original_pbg_back3_bytes(original)), 5932)
        self.assertEqual(PBG_MAIL_NATIVE_CONTROL_DEFAULT_FLAGS, 0x183)
        self.assertEqual(PBG_MAIL_NATIVE_SOURCE_IDLE_RECT, (0, 0, 40, 95))
        strips = [bytes((index, 40+index, 80+index, 255)) * (40*95)
                  for index in range(4)]
        art = OriginalPBgMailArt(EA444DecodedImage(
            40, 380, b"".join(strips), 0, 0))
        self.assertEqual(
            native_pbg_mail_idle_bitmap_pixels(art),
            (558, 0, 40, 95, strips[0]),
        )
        with self.assertRaisesRegex(OriginalPBgMailArtError, "hover/pressed"):
            native_pbg_mail_idle_bitmap_pixels(art, control_flags=0x18B)
        with self.assertRaises(OriginalPBgMailArtError):
            OriginalPBgMailArt(EA444DecodedImage(40, 95, strips[0], 0, 0))
        return art

    def test_exact_original_generic_virtual_90_state_precedence(self):
        select = native_pbg_mail_bitmap_frame
        for image_flags in (0, 1, 2, 4, 8, 16, 31, 0xffff):
            self.assertEqual(select(0x183, image_flags), 0)
        self.assertEqual(select(0, 8), 3)
        self.assertEqual(select(0, 0), 0)
        self.assertEqual(select(0x12, 2), 1)
        self.assertEqual(select(0x22, 2), 1)
        self.assertEqual(select(0x6, 16), 4)
        self.assertEqual(select(0xA, 4), 2)
        self.assertEqual(select(0x1E, 18), 1)
        for flags in (-1, True, "2", 0x100000000):
            with self.assertRaises(OriginalPBgMailArtError):
                select(flags, 0)
        with self.assertRaises(OriginalPBgMailArtError):
            select(0x183, True)

    def test_source_corruption_fails_before_executable_decode(self):
        with patch("original_pbg_mail_art.verified_original_pbg_back3_bytes",
                   side_effect=ValueError("bad authentic bitmap")):
            with self.assertRaises(ValueError):
                load_verified_original_pbg_mail_art("bad source", "absent.exe")

    def test_live_host_draws_real_initial_header_pixel_cropped_not_placeholder(self):
        strips = [bytes((i*20, i*20, i*20, 255))*(40*95) for i in range(4)]
        host = OriginalGameTkHost.__new__(OriginalGameTkHost)
        host.management_mail_art = OriginalPBgMailArt(
            EA444DecodedImage(40, 380, b"".join(strips), 0, 0))
        host.tk = SimpleNamespace(NW="nw")
        layers = []
        host._rgba_photo = lambda w,h,rgba: (w,h,rgba)
        host._create_native_image = lambda x,y,**kw: layers.append((x,y,kw))
        self.assertEqual(host._draw_management_mail_control(), 1)
        self.assertEqual(layers[0][:2], (558, 0))
        self.assertEqual(layers[0][2]["image"], (40, 95, strips[0]))
        host.management_mail_art = None
        self.assertEqual(host._draw_management_mail_control(), 0)


if __name__ == "__main__":
    main()
