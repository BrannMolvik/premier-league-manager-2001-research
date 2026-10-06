from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from original_squad_status import (
    FRAME_COUNT,
    FRAME_SIZE,
    NON_EU_ALTERNATE_FRAME_INDEX,
    ON_LOAN_ALTERNATE_FRAME_INDEX,
    ORDINARY_STATUS_FRAME_COUNT,
    SOURCE_DIMENSIONS,
    SOURCE_PATH,
    STATUS_DEFINITION_TEXT,
    OriginalSquadStatusError,
    validate_original_squad_status_atlas,
)


class OriginalSquadStatusTests(unittest.TestCase):
    def test_exact_original_status_atlas_is_verified_and_sliced_vertically(self):
        source_root = Path(__file__).resolve().parents[1] / "original_assets" / "source"
        atlas = validate_original_squad_status_atlas(source_root)

        self.assertEqual((atlas.width, atlas.height), SOURCE_DIMENSIONS)
        self.assertEqual((atlas.frame_width, atlas.frame_height), FRAME_SIZE)
        self.assertEqual(atlas.frame_count, FRAME_COUNT)
        self.assertEqual(len(atlas.frame_rectangles), 14)
        self.assertEqual(atlas.frame_rectangles[0], (0, 0, 18, 14))
        self.assertEqual(atlas.frame_rectangles[11], (0, 154, 18, 168))
        self.assertEqual(atlas.frame_rectangles[12], (0, 168, 18, 182))
        self.assertEqual(atlas.frame_rectangles[13], (0, 182, 18, 196))
        self.assertTrue((source_root / SOURCE_PATH).is_file())

    def test_static_status_definition_order_and_two_alternate_frames_are_explicit(self):
        self.assertEqual(
            STATUS_DEFINITION_TEXT,
            (
                "Injured",
                "Banned",
                "International",
                "Cup Tied",
                "First Team",
                "Subsitute",
                "On loan",
                "Out of contract",
                "Transfer listed",
                "Bid in",
                "Wanted",
                "Non EU",
            ),
        )
        self.assertEqual(ORDINARY_STATUS_FRAME_COUNT, 12)
        self.assertEqual(NON_EU_ALTERNATE_FRAME_INDEX, 12)
        self.assertEqual(ON_LOAN_ALTERNATE_FRAME_INDEX, 13)

    def test_status_atlas_validator_fails_closed_without_exact_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaises(OriginalSquadStatusError):
                validate_original_squad_status_atlas(root)


if __name__ == "__main__":
    unittest.main()
