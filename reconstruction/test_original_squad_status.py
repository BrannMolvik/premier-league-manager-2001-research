from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from original_squad_status import (
    DIRECT_STATUS_FRAME_INDICES,
    DIRECT_STATUS_TEXT,
    FRAME_COUNT,
    FRAME_SIZE,
    NON_EU_ALTERNATE_FRAME_INDEX,
    ON_LOAN_ALTERNATE_FRAME_INDEX,
    ORDINARY_STATUS_FRAME_COUNT,
    SOURCE_DIMENSIONS,
    SOURCE_PATH,
    SOURCE_QUALIFIED_STATUS_FRAME_INDICES,
    STATUS_DEFINITION_TEXT,
    OriginalSquadStatusError,
    build_first_roster_direct_status_overlays,
    direct_squad_status_frame_index,
    source_qualified_squad_status_frame_index,
    load_verified_squad_status_resources,
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

    def test_direct_status_priority_is_exact_and_override_safe(self):
        self.assertEqual(DIRECT_STATUS_FRAME_INDICES, (0, 1, 2))
        self.assertEqual(
            DIRECT_STATUS_TEXT,
            ("Injured", "Banned", "International"),
        )
        self.assertEqual(
            direct_squad_status_frame_index(
                injured=True,
                banned=True,
                international=True,
            ),
            0,
        )
        self.assertEqual(
            direct_squad_status_frame_index(
                injured=False,
                banned=True,
                international=True,
            ),
            1,
        )
        self.assertEqual(
            direct_squad_status_frame_index(
                injured=False,
                banned=False,
                international=True,
            ),
            2,
        )
        self.assertIsNone(
            direct_squad_status_frame_index(
                injured=False,
                banned=False,
                international=False,
            )
        )

    def test_source_qualified_status_priority_uses_registration_expiry_before_cup_tied(self):
        self.assertEqual(
            SOURCE_QUALIFIED_STATUS_FRAME_INDICES,
            (0, 1, 2, 3, 12, 13),
        )
        self.assertEqual(
            source_qualified_squad_status_frame_index(
                injured=True,
                banned=True,
                international=True,
                alternate_on_loan=True,
                non_eu=True,
                non_eu_registration_expired=True,
                cup_tied_positive=True,
            ),
            0,
        )
        self.assertEqual(
            source_qualified_squad_status_frame_index(
                injured=False,
                banned=False,
                international=False,
                alternate_on_loan=True,
                non_eu=True,
                non_eu_registration_expired=True,
                cup_tied_positive=True,
            ),
            ON_LOAN_ALTERNATE_FRAME_INDEX,
        )
        self.assertEqual(
            source_qualified_squad_status_frame_index(
                injured=False,
                banned=False,
                international=False,
                alternate_on_loan=False,
                non_eu=True,
                non_eu_registration_expired=True,
                cup_tied_positive=True,
            ),
            NON_EU_ALTERNATE_FRAME_INDEX,
        )
        self.assertIsNone(
            source_qualified_squad_status_frame_index(
                injured=False,
                banned=False,
                international=False,
                alternate_on_loan=False,
                non_eu=True,
                non_eu_registration_expired=None,
                cup_tied_positive=True,
            )
        )
        self.assertEqual(
            source_qualified_squad_status_frame_index(
                injured=False,
                banned=False,
                international=False,
                alternate_on_loan=False,
                non_eu=True,
                non_eu_registration_expired=False,
                cup_tied_positive=True,
            ),
            3,
        )
        self.assertEqual(
            source_qualified_squad_status_frame_index(
                injured=False,
                banned=False,
                international=False,
                alternate_on_loan=False,
                non_eu=False,
                non_eu_registration_expired=False,
                cup_tied_positive=True,
            ),
            3,
        )
        self.assertIsNone(
            source_qualified_squad_status_frame_index(
                injured=False,
                banned=False,
                international=False,
                alternate_on_loan=False,
                non_eu=False,
                non_eu_registration_expired=False,
                cup_tied_positive=False,
            )
        )
        with self.assertRaises(OriginalSquadStatusError):
            source_qualified_squad_status_frame_index(
                injured=False,
                banned=False,
                international=False,
                alternate_on_loan=False,
                non_eu=False,
                non_eu_registration_expired=True,
                cup_tied_positive=False,
            )

    def test_verified_status_png_decodes_to_fourteen_exact_rgba_frames(self):
        source_root = Path(__file__).resolve().parents[1] / "original_assets" / "source"
        resources = load_verified_squad_status_resources(source_root)

        self.assertEqual(len(resources.frames), 14)
        self.assertEqual(
            tuple((frame.width, frame.height) for frame in resources.frames),
            (FRAME_SIZE,) * 14,
        )
        self.assertTrue(all(len(frame.rgba) == 18 * 14 * 4 for frame in resources.frames))
        self.assertEqual(
            tuple(frame.index for frame in resources.frames),
            tuple(range(14)),
        )

    def test_direct_status_overlay_uses_exact_first_roster_pscf_geometry(self):
        source_root = Path(__file__).resolve().parents[1] / "original_assets" / "source"
        resources = load_verified_squad_status_resources(source_root)
        rows = (
            type("Row", (), {"y": 154, "native_status_frame_index": 0})(),
            type("Row", (), {"y": 171, "native_status_frame_index": None})(),
            type("Row", (), {"y": 188, "native_status_frame_index": 2})(),
        )
        overlays = build_first_roster_direct_status_overlays(rows, resources)

        self.assertEqual(tuple(item.frame_index for item in overlays), (0, 2))
        self.assertEqual(tuple((item.x, item.y) for item in overlays), ((277, 234), (277, 268)))
        self.assertEqual(tuple((item.width, item.height) for item in overlays), (FRAME_SIZE, FRAME_SIZE))

    def test_status_atlas_validator_fails_closed_without_exact_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaises(OriginalSquadStatusError):
                validate_original_squad_status_atlas(root)


if __name__ == "__main__":
    unittest.main()
