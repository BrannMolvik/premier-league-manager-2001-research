"""Source-backed PStartMenu resource loader and integration tests.

Synthetic tests are deliberately graphical-desktop-free. The opt-in test
requires the original licensed EAUK source and canonical executable.
"""
import os
from pathlib import Path
import struct
import tempfile
import unittest

from ea444_decoder import EA444DecodedImage
from ea_font import EAFont
from ea_language_strings import parse_language_pair
from original_button_frames import (
    OriginalButtonAtlas,
    PSTARTMENU_BUTTON_ATLAS,
    TEAMSELECT_BUTTON_ATLAS,
    split_original_button_atlas,
)
from original_front_end_layout import SCREEN_SIZE
from original_pstartmenu_labels import prepare_original_pstartmenu_captions
from original_pstartmenu_resources import (
    COMPOSED_BACKGROUND_RGBA_SHA256,
    ENGLISH_ACTION_TEXTS,
    OriginalPStartMenuResourceError,
    _read_verified,
    assemble_original_pstartmenu_inputs,
    load_verified_english_pstartmenu_inputs,
)
from test_ea_font import build_fixture
from test_ea_language_strings import make_str


def fixture():
    base = EA444DecodedImage(800, 600, bytes((1, 2, 3, 255)) * (800 * 600), 0, 0)
    menu = EA444DecodedImage(532, 532, bytes((4, 5, 6, 255)) * (532 * 532), 0, 0)
    spec = PSTARTMENU_BUTTON_ATLAS
    raw_frames = EA444DecodedImage(
        spec.source_width, spec.source_height,
        bytes((9, 8, 7, 255)) * (spec.source_width * spec.source_height), 0, 0,
    )
    buttons = split_original_button_atlas(raw_frames, spec)
    strings, index = parse_language_pair(
        make_str(("B", "AB", "A", "BA")),
        struct.pack("<7H", 1, 3, 2, 0, 0, 2, 0),
    )
    captions = prepare_original_pstartmenu_captions(
        EAFont.from_bytes(build_fixture()), strings, index
    )
    return base, menu, buttons, captions


class OriginalPStartMenuResourcesTests(unittest.TestCase):
    def test_assembles_proven_background_and_unrendered_source_controls(self):
        resources = assemble_original_pstartmenu_inputs(*fixture())
        self.assertEqual(len(resources.background_rgba), 800 * 600 * 4)
        self.assertEqual(resources.button_atlas.spec, PSTARTMENU_BUTTON_ATLAS)
        self.assertEqual(len(resources.button_atlas.frames), 23)
        self.assertEqual(
            tuple(item.original_text for item in resources.captions),
            ("AB", "BA", "A", "B"),
        )

        def pixel(x, y):
            start = (y * SCREEN_SIZE[0] + x) * 4
            return resources.background_rgba[start:start + 4]

        self.assertEqual(pixel(0, 0), bytes((1, 2, 3, 255)))
        self.assertEqual(pixel(133, 34), bytes((1, 2, 3, 255)))
        self.assertEqual(pixel(134, 34), bytes((4, 5, 6, 255)))
        self.assertEqual(pixel(665, 565), bytes((4, 5, 6, 255)))
        self.assertEqual(pixel(666, 565), bytes((1, 2, 3, 255)))

    def test_rejects_other_atlas_missing_frames_or_mutated_event_layout(self):
        base, menu, buttons, captions = fixture()
        for bad_atlas in (
            OriginalButtonAtlas(TEAMSELECT_BUTTON_ATLAS, buttons.frames),
            OriginalButtonAtlas(PSTARTMENU_BUTTON_ATLAS, buttons.frames[:-1]),
        ):
            with self.subTest(spec=bad_atlas.spec):
                with self.assertRaises(OriginalPStartMenuResourceError):
                    assemble_original_pstartmenu_inputs(
                        base, menu, bad_atlas, captions
                    )
        with self.assertRaises(OriginalPStartMenuResourceError):
            assemble_original_pstartmenu_inputs(
                base, menu, buttons, tuple(reversed(captions))
            )

    def test_refuses_any_source_asset_with_incorrect_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "English.str"
            path.write_bytes(b"fake replacement English language strings")
            with self.assertRaisesRegex(
                OriginalPStartMenuResourceError, "checksum mismatch"
            ):
                _read_verified(path, "0" * 64)

    @unittest.skipUnless(
        os.environ.get("FM2001_ORIGINAL_EXE")
        and os.environ.get("FM2001_ORIGINAL_444_ROOT")
        and os.environ.get("FM2001_ORIGINAL_FONT_20")
        and os.environ.get("FM2001_ORIGINAL_LANGUAGE_DIR"),
        "Original licensed source executable/art/font/language not bundled with CI",
    )
    def test_opt_in_real_source_complete_original_pstartmenu_inputs(self):
        from hashlib import sha256
        original = load_verified_english_pstartmenu_inputs(
            original_executable=Path(os.environ["FM2001_ORIGINAL_EXE"]),
            original_art_dir=Path(os.environ["FM2001_ORIGINAL_444_ROOT"]),
            original_zurich_font20=Path(os.environ["FM2001_ORIGINAL_FONT_20"]),
            original_language_dir=Path(os.environ["FM2001_ORIGINAL_LANGUAGE_DIR"]),
        )
        self.assertEqual(
            sha256(original.background_rgba).hexdigest(),
            COMPOSED_BACKGROUND_RGBA_SHA256,
        )
        self.assertEqual(len(original.button_atlas.frames), 23)
        self.assertEqual(
            tuple(item.original_text for item in original.captions),
            ENGLISH_ACTION_TEXTS,
        )
        self.assertEqual(
            tuple((item.glyph_mask.width, item.glyph_mask.height)
                  for item in original.captions),
            ((63, 19), (117, 19), (81, 19), (120, 19)),
        )


if __name__ == "__main__":
    unittest.main()
