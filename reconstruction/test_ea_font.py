import hashlib
import os
from pathlib import Path
import struct
import unittest

from ea_font import (
    EAFont,
    EAFontError,
    GLYPH_COUNT,
    GLYPH_RECORD_SIZE,
)


def build_fixture() -> bytes:
    width, height = 4, 2
    data = bytearray(struct.pack("<5I", width, height, 1, 0x8000, 0xFFFF))
    records = [bytearray(GLYPH_RECORD_SIZE) for _ in range(GLYPH_COUNT)]

    def set_glyph(ch, atlas_x, glyph_width, glyph_height, draw_y):
        index = ord(ch) - 32
        struct.pack_into(
            "<4I", records[index], 0,
            atlas_x, glyph_width, glyph_height, draw_y,
        )
        return records[index]

    a = set_glyph("A", 0, 2, 2, 0)
    set_glyph("B", 2, 2, 1, 1)
    # Signed pair adjustment A -> B = -1.
    struct.pack_into("<b", a, 16 + ord("B") - 32, -1)

    for record in records:
        data.extend(record)
    # Row-major one-byte alpha atlas.
    data.extend(bytes((255, 0, 128, 64, 0, 255, 0, 0)))
    return bytes(data)


class EAFontTests(unittest.TestCase):
    def test_parses_glyph_metrics_signed_pair_spacing_and_alpha(self):
        font = EAFont.from_bytes(build_fixture())
        self.assertEqual((font.atlas_width, font.atlas_height), (4, 2))
        self.assertEqual(
            (font.header_value_2, font.header_value_3, font.header_value_4),
            (1, 0x8000, 0xFFFF),
        )
        a = font.glyph_for_byte(ord("A"))
        self.assertEqual(
            (a.atlas_x, a.width, a.height, a.draw_y),
            (0, 2, 2, 0),
        )
        self.assertEqual(a.pair_adjustment(ord("B")), -1)
        self.assertEqual(font.glyph_alpha(ord("A")), bytes((255, 0, 0, 255)))
        self.assertEqual(font.measure_text("AB"), 3)

    def test_rasterizes_with_draw_y_and_negative_pair_spacing(self):
        mask = EAFont.from_bytes(build_fixture()).render_text_alpha("AB")
        self.assertEqual((mask.width, mask.height), (3, 2))
        self.assertEqual(
            mask.alpha,
            bytes((
                255, 0, 0,
                0, 255, 64,
            )),
        )

    def test_rejects_bad_size_geometry_and_unrepresentable_text(self):
        data = build_fixture()
        with self.assertRaises(EAFontError):
            EAFont.from_bytes(data[:-1])

        damaged = bytearray(data)
        # A width extends beyond atlas.
        struct.pack_into(
            "<I", damaged,
            20 + (ord("A") - 32) * GLYPH_RECORD_SIZE + 4,
            100,
        )
        with self.assertRaises(EAFontError):
            EAFont.from_bytes(bytes(damaged))

        font = EAFont.from_bytes(data)
        with self.assertRaises(EAFontError):
            font.measure_text("\n")
        with self.assertRaises(EAFontError):
            font.measure_text("🙂")

    @unittest.skipUnless(
        os.environ.get("FM2001_ORIGINAL_FONT_20"),
        "Original licensed Zurich font not bundled with CI",
    )
    def test_real_original_zurich_20_pixel_font_and_menu_labels(self):
        path = Path(os.environ["FM2001_ORIGINAL_FONT_20"])
        data = path.read_bytes()
        self.assertEqual(
            hashlib.sha256(data).hexdigest(),
            "47e3b21f07a3013ba19d257f31e1e876c9b03856c930a8fa5fe58103974ed166",
        )
        font = EAFont.from_bytes(data)
        self.assertEqual(
            (
                font.atlas_width,
                font.atlas_height,
                font.header_value_2,
                font.header_value_3,
                font.header_value_4,
            ),
            (1789, 21, 1, 32768, 65535),
        )
        expected = {
            "Continue": (
                63, 19,
                "6af205e0d5ee04c063770438919a3418b18cd8e91ab615bdc8bb21a7e9137ae2",
            ),
            "Start New Game": (
                117, 19,
                "2fa38f32908de0f08b66c7c6d7f0f900ab9ba141cac4ae38abc3e7236134378a",
            ),
            "Load Game": (
                81, 19,
                "5f5b62250acce9bce3a46ee101db3b9357b8b8f6a139940e06ba5e43cd7312ea",
            ),
            "Quit to Windows": (
                120, 19,
                "6f0030a88479d55ece7b77ac5b32f99b699ceff748be890e04614c22e5bb2140",
            ),
        }
        for text, (width, height, digest) in expected.items():
            mask = font.render_text_alpha(text)
            self.assertEqual((mask.width, mask.height), (width, height))
            self.assertEqual(hashlib.sha256(mask.alpha).hexdigest(), digest)


if __name__ == "__main__":
    unittest.main()
