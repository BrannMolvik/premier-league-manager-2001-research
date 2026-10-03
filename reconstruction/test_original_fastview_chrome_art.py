import unittest

from ea444_decoder import EA444DecodedImage
from original_fastview_chrome_art import (
    OriginalFastViewChromeArtError,
    build_fastview_chrome_art,
)


def image(width, height, value):
    return EA444DecodedImage(width=width, height=height, rgba=bytes([value]) * width * height * 4)


class OriginalFastViewChromeArtTests(unittest.TestCase):
    def test_exact_top_and_ticker_placements_without_middle_claim(self):
        art = build_fastview_chrome_art(
            {
                "top_bar.444": image(800, 95, 1),
                "ticker.444": image(800, 33, 2),
            }
        )
        self.assertEqual(
            [placement.rect for placement in art.placements],
            [(0, 0, 800, 95), (0, 557, 800, 590)],
        )
        self.assertFalse(art.middle_surface_recovered)
        self.assertFalse(art.complete_800x600_frame_available)

    def test_missing_or_wrong_geometry_fails_closed(self):
        with self.assertRaises(OriginalFastViewChromeArtError):
            build_fastview_chrome_art({})
        with self.assertRaises(OriginalFastViewChromeArtError):
            build_fastview_chrome_art(
                {
                    "top_bar.444": image(799, 95, 1),
                    "ticker.444": image(800, 33, 2),
                }
            )


if __name__ == "__main__":
    unittest.main()
