import unittest

from ea444_decoder import EA444DecodedImage
from gate14_fastview_chrome import REJECTED_UNBOUND_BACKGROUND_PATH
from original_fastview_chrome_art import (
    OriginalFastViewChromeArtError,
    build_fastview_chrome_art,
)


def image(width, height, value):
    return EA444DecodedImage(
        width=width,
        height=height,
        rgba=bytes([value]) * (width * height * 4),
        consumed_bits=0,
        transparent_pixels=0,
    )


class OriginalFastViewChromeArtTests(unittest.TestCase):
    def test_exact_direct_owned_placements_only(self):
        art = build_fastview_chrome_art(
            {
                "top_bar": image(800, 95, 1),
                "ticker": image(800, 33, 2),
            }
        )
        self.assertEqual(
            [(x.resource_name, x.rect) for x in art.placements],
            [
                ("top_bar", (0, 0, 800, 95)),
                ("ticker", (0, 557, 800, 590)),
            ],
        )
        self.assertEqual(
            art.rejected_unbound_background_path,
            REJECTED_UNBOUND_BACKGROUND_PATH,
        )
        self.assertFalse(art.complete_fastview_frame_available)

    def test_wrong_or_missing_decoded_art_fails_closed(self):
        with self.assertRaisesRegex(OriginalFastViewChromeArtError, "Missing decoded"):
            build_fastview_chrome_art({"top_bar": image(800, 95, 1)})
        with self.assertRaisesRegex(OriginalFastViewChromeArtError, "geometry mismatch"):
            build_fastview_chrome_art(
                {
                    "top_bar": image(799, 95, 1),
                    "ticker": image(800, 33, 2),
                }
            )


if __name__ == "__main__":
    unittest.main()
