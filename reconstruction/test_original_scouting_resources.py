"""Tests for the exact PScouting2K source-resource composition fragment."""
from hashlib import sha256
import os
from pathlib import Path
import unittest

from ea444_decoder import EA444DecodedImage
from ea444_header import parse_ea444_header
from original_scouting_resources import (
    OriginalScoutingResourceError,
    SCOUTING_BOTTOM_ORIGIN,
    SCOUTING_BOTTOM_SHA256,
    SCOUTING_BOTTOM_SIZE,
    SCOUTING_BOTTOM_SOURCE_PATH,
    SCOUTING_REPEATED_ORIGINS,
    SCOUTING_REPEATED_SHA256,
    SCOUTING_REPEATED_SIZE,
    SCOUTING_REPEATED_SOURCE_PATH,
    assemble_original_scouting_composition,
    load_verified_original_scouting_composition,
)


def solid(width, height, rgba):
    return EA444DecodedImage(
        width, height, bytes(rgba) * (width * height), 0, 0
    )


class OriginalScoutingResourceTests(unittest.TestCase):
    def test_imported_original_bytes_match_proven_hashes_and_header_geometry(self):
        root = Path(__file__).resolve().parent.parent / "original_assets" / "source"
        for path, expected_sha, expected_size in (
            (SCOUTING_REPEATED_SOURCE_PATH, SCOUTING_REPEATED_SHA256,
             SCOUTING_REPEATED_SIZE),
            (SCOUTING_BOTTOM_SOURCE_PATH, SCOUTING_BOTTOM_SHA256,
             SCOUTING_BOTTOM_SIZE),
        ):
            with self.subTest(path=path):
                raw = (root / path).read_bytes()
                self.assertEqual(sha256(raw).hexdigest(), expected_sha)
                header = parse_ea444_header(raw)
                self.assertEqual((header.width, header.height), expected_size)

    def test_exact_setup_method_geometry_and_transparent_composition(self):
        repeated = solid(*SCOUTING_REPEATED_SIZE, (10, 20, 30, 255))
        bottom = solid(*SCOUTING_BOTTOM_SIZE, (40, 50, 60, 255))
        result = assemble_original_scouting_composition(repeated, bottom)

        self.assertEqual(len(SCOUTING_REPEATED_ORIGINS), 20)
        self.assertEqual(SCOUTING_REPEATED_ORIGINS[0], (207, 192))
        self.assertEqual(SCOUTING_REPEATED_ORIGINS[-1], (207, 515))
        self.assertTrue(all(
            b[1] - a[1] == 17
            for a, b in zip(
                SCOUTING_REPEATED_ORIGINS,
                SCOUTING_REPEATED_ORIGINS[1:],
            )
        ))
        self.assertEqual(SCOUTING_BOTTOM_ORIGIN, (206, 543))
        self.assertEqual(len(result.placements), 21)

        rgba = result.transparent_overlay_rgba()
        def pixel(x, y):
            pos = (y * 800 + x) * 4
            return tuple(rgba[pos:pos + 4])

        self.assertEqual(pixel(207, 192), (10, 20, 30, 255))
        self.assertEqual(pixel(777, 207), (10, 20, 30, 255))
        self.assertEqual(pixel(207, 208), (0, 0, 0, 0))
        self.assertEqual(pixel(207, 209), (10, 20, 30, 255))
        self.assertEqual(pixel(206, 543), (40, 50, 60, 255))
        self.assertEqual(pixel(500, 587), (40, 50, 60, 255))
        self.assertEqual(pixel(501, 587), (0, 0, 0, 0))

    def test_wrong_geometry_and_partial_alpha_fail_closed(self):
        with self.assertRaises(OriginalScoutingResourceError):
            assemble_original_scouting_composition(
                solid(570, 16, (1, 2, 3, 255)),
                solid(*SCOUTING_BOTTOM_SIZE, (4, 5, 6, 255)),
            )
        result = assemble_original_scouting_composition(
            solid(*SCOUTING_REPEATED_SIZE, (1, 2, 3, 128)),
            solid(*SCOUTING_BOTTOM_SIZE, (4, 5, 6, 255)),
        )
        with self.assertRaisesRegex(OriginalScoutingResourceError, "partial alpha"):
            result.transparent_overlay_rgba()

    @unittest.skipUnless(
        os.environ.get("FM2001_ORIGINAL_EXE")
        and os.environ.get("FM2001_ORIGINAL_444_ROOT"),
        "Canonical licensed original executable not distributed in hosted CI",
    )
    def test_opt_in_decodes_the_two_exact_original_resources(self):
        result = load_verified_original_scouting_composition(
            original_art_dir=Path(os.environ["FM2001_ORIGINAL_444_ROOT"]),
            original_executable=Path(os.environ["FM2001_ORIGINAL_EXE"]),
        )
        self.assertEqual(
            (result.repeated_strip.width, result.repeated_strip.height),
            SCOUTING_REPEATED_SIZE,
        )
        self.assertEqual(
            (result.bottom_panel.width, result.bottom_panel.height),
            SCOUTING_BOTTOM_SIZE,
        )
        self.assertEqual(len(result.transparent_overlay_rgba()), 800 * 600 * 4)


if __name__ == "__main__":
    unittest.main()
