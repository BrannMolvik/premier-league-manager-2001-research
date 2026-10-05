"""Tests for pure source-backed FastView surfaced resource selection."""
from datetime import date
from types import SimpleNamespace
import unittest

from gate14_fastview_surfaced_picture_selection import (
    FastViewSurfacedSelectionError,
    build_fastview_surfaced_resource_selection,
    surfaced_resource_selection_contract,
)
from gate14_fastview_surfaced_picture_source import (
    BADGE_GENERIC_FALLBACK,
    COMPACT_CLUB_READER_VA,
    MASTER_CLUB_FAN_BASE_INDEX_OFFSET,
    RUNTIME_CLUB_IMPORT_VA,
)


def club(country_id, basename, fan_base_index):
    return SimpleNamespace(
        country_id=country_id,
        graphics_basename=basename,
        fan_base_index=fan_base_index,
    )


class FastViewSurfacedPictureSelectionTests(unittest.TestCase):
    def setUp(self):
        self.clubs = {
            10: club(26, "arsenal", 25),
            11: club(26, "chelsea", 14),
            12: club(31, "psg", 8),
        }
        self.countries = {
            26: SimpleNamespace(graphics_directory="England"),
            31: SimpleNamespace(graphics_directory="France"),
        }

    def test_master_fan_base_binding_is_exact_compact_to_runtime_field(self):
        self.assertEqual(COMPACT_CLUB_READER_VA, 0x4022D0)
        self.assertEqual(RUNTIME_CLUB_IMPORT_VA, 0x403660)
        self.assertEqual(MASTER_CLUB_FAN_BASE_INDEX_OFFSET, 94)

        contract = surfaced_resource_selection_contract()
        self.assertEqual(contract["master_fan_base_index_offset"], 94)
        self.assertEqual(
            contract["cleanroom_fan_base_field"],
            "Club.fan_base_index",
        )

    def test_no_override_selects_home_background_and_exact_january_resources(self):
        selection = build_fastview_surfaced_resource_selection(
            match_date=date(2001, 1, 13),
            clubs=self.clubs,
            countries=self.countries,
            home_club_id=10,
            away_club_id=11,
            background_club_override_id=None,
        )

        self.assertEqual(selection.home.club_id, 10)
        self.assertEqual(selection.away.club_id, 11)
        self.assertEqual(selection.background.club_id, 10)
        self.assertIsNone(selection.background_override_club_id)
        self.assertEqual(selection.background_variant, 2)
        self.assertEqual(
            selection.background_source_candidates,
            (
                r"FM2001_Art\Generic\Team_backgrounds\England\arsenal_background2.444",
                r"FM2001_Art\Generic\Team_backgrounds\England\arsenal_background.444",
                r"FM2001_Art\Generic\Team_backgrounds\generic0_background2.444",
            ),
        )
        self.assertEqual(
            selection.home_badge_source_candidates,
            (
                r"FM2001_Art\Generic\Team_badge_stills\England\arsenal_badge_2.444",
                BADGE_GENERIC_FALLBACK,
            ),
        )
        self.assertEqual(
            selection.away_badge_source_candidates,
            (
                r"FM2001_Art\Generic\Team_badge_stills\England\chelsea_badge_2.444",
                BADGE_GENERIC_FALLBACK,
            ),
        )
        self.assertFalse(selection.source_bytes_loaded)
        self.assertFalse(selection.ea444_decoded)
        self.assertFalse(selection.complete_fastview_frame_recovered)

    def test_explicit_override_selects_that_club_and_its_fallback_tier(self):
        selection = build_fastview_surfaced_resource_selection(
            match_date=date(2001, 6, 2),
            clubs=self.clubs,
            countries=self.countries,
            home_club_id=10,
            away_club_id=11,
            background_club_override_id=12,
        )
        self.assertEqual(selection.background.club_id, 12)
        self.assertEqual(selection.background.country_graphics_directory, "France")
        self.assertEqual(selection.background_variant, 0)
        self.assertEqual(
            selection.background_source_candidates,
            (
                r"FM2001_Art\Generic\Team_backgrounds\France\psg_background0.444",
                r"FM2001_Art\Generic\Team_backgrounds\France\psg_background.444",
                r"FM2001_Art\Generic\Team_backgrounds\generic2_background0.444",
            ),
        )

    def test_missing_source_fields_or_unknown_ids_fail_closed(self):
        bad_clubs = dict(self.clubs)
        bad_clubs[13] = SimpleNamespace(
            country_id=26,
            graphics_basename="",
            fan_base_index=10,
        )
        with self.assertRaisesRegex(
            FastViewSurfacedSelectionError,
            "lacks exact original art-selection fields",
        ):
            build_fastview_surfaced_resource_selection(
                match_date=date(2001, 9, 1),
                clubs=bad_clubs,
                countries=self.countries,
                home_club_id=13,
                away_club_id=11,
                background_club_override_id=None,
            )
        with self.assertRaisesRegex(
            FastViewSurfacedSelectionError,
            "club 99 is unavailable",
        ):
            build_fastview_surfaced_resource_selection(
                match_date=date(2001, 9, 1),
                clubs=self.clubs,
                countries=self.countries,
                home_club_id=99,
                away_club_id=11,
                background_club_override_id=None,
            )
        with self.assertRaisesRegex(
            FastViewSurfacedSelectionError,
            "background override",
        ):
            build_fastview_surfaced_resource_selection(
                match_date=date(2001, 9, 1),
                clubs=self.clubs,
                countries=self.countries,
                home_club_id=10,
                away_club_id=11,
                background_club_override_id=-1,
            )
        with self.assertRaises(FastViewSurfacedSelectionError):
            build_fastview_surfaced_resource_selection(
                match_date=date(2001, 9, 1),
                clubs=self.clubs,
                countries=self.countries,
                home_club_id=True,
                away_club_id=11,
                background_club_override_id=None,
            )

    def test_contract_keeps_loading_decode_and_gate_completion_false(self):
        contract = surfaced_resource_selection_contract()
        self.assertTrue(contract["match_date_required"])
        self.assertTrue(contract["home_club_required"])
        self.assertTrue(contract["away_club_required"])
        self.assertTrue(contract["background_override_state_required"])
        self.assertTrue(contract["background_none_means_source_override_absent"])
        self.assertTrue(contract["background_selector_bound_to_cleanroom_state"])
        self.assertTrue(contract["badge_selector_bound_to_cleanroom_state"])
        self.assertFalse(contract["source_bytes_loaded"])
        self.assertFalse(contract["ea444_decoded"])
        self.assertFalse(contract["complete_fastview_frame_recovered"])
        self.assertFalse(contract["gate14_complete"])


if __name__ == "__main__":
    unittest.main()
