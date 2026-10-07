"""Regression coverage for source-closed PPreMatch XI shirt selection."""
from types import SimpleNamespace
import unittest

from gate14_prematch_shirt_selection import (
    PREMATCH_GENERIC_RECOLOR_VA,
    PREMATCH_KIT_CLASH_SELECTOR_VA,
    PREMATCH_KIT_CLASH_TABLE_VA,
    PREMATCH_KIT_CONTEXT_SELECTOR_VA,
    PREMATCH_PLAYER_SHIRT_NUMBER_SELECTOR_VA,
    PREMATCH_PLAYER_SHIRT_SELECTOR_VA,
    PREMATCH_TEAM_SHIRT_BUILDER_VA,
    PrematchClubShirtState,
    PrematchShirtSelectionError,
    club_shirt_state,
    prematch_player_shirt_frame_offset,
    prematch_shirt_selection_contract,
    select_prematch_team_kits,
)


def clash_table(*pairs):
    rows = [bytearray([23] * 6) for _ in range(23)]
    for left, right in pairs:
        rows[left][0] = right
    return b"".join(bytes(row) for row in rows)


def club(club_id, basename, primary_template, alternate_template, primary_color, alternate_color):
    return PrematchClubShirtState(
        club_id=club_id,
        graphics_basename=basename,
        primary_template_index=primary_template,
        alternate_template_index=alternate_template,
        primary_color_id=primary_color,
        alternate_color_id=alternate_color,
    )


class PrematchShirtSelectionTests(unittest.TestCase):
    def test_native_addresses_and_fail_closed_boundary_are_exact(self):
        self.assertEqual(PREMATCH_KIT_CONTEXT_SELECTOR_VA, 0x5EF940)
        self.assertEqual(PREMATCH_KIT_CLASH_SELECTOR_VA, 0x5EF9E0)
        self.assertEqual(PREMATCH_KIT_CLASH_TABLE_VA, 0x834AF8)
        self.assertEqual(PREMATCH_TEAM_SHIRT_BUILDER_VA, 0x408320)
        self.assertEqual(PREMATCH_GENERIC_RECOLOR_VA, 0x5E4C60)
        self.assertEqual(PREMATCH_PLAYER_SHIRT_SELECTOR_VA, 0x41E3F0)
        self.assertEqual(PREMATCH_PLAYER_SHIRT_NUMBER_SELECTOR_VA, 0x41E3D0)

        contract = prematch_shirt_selection_contract()
        self.assertTrue(contract["custom_primary_attempt_source_closed"])
        self.assertTrue(contract["alternate_skips_custom_source_closed"])
        self.assertTrue(contract["generic_template_fallback_source_closed"])
        self.assertTrue(contract["player_frame_offset_source_closed"])
        self.assertFalse(contract["generic_recolor_pixels_recovered"])
        self.assertFalse(contract["complete_marker_pixels_recovered"])
        self.assertFalse(contract["gate14_complete"])

    def test_no_clash_keeps_both_primary_and_custom_attempts(self):
        home = club(10, "Arsenal", 4, 7, 1, 9)
        away = club(11, "Chelsea", 8, 12, 2, 10)
        selected = select_prematch_team_kits(
            home,
            away,
            clash_table=clash_table(),
        )
        self.assertFalse(selected.home.use_alternate)
        self.assertFalse(selected.away.use_alternate)
        self.assertEqual(selected.home.selected_template_index, 4)
        self.assertEqual(selected.away.selected_template_index, 8)
        self.assertEqual(
            selected.home.custom_source_path,
            r"fm2001_art\Generic\front-end-shirts\custom\Arsenal.444",
        )
        self.assertEqual(
            selected.away.custom_source_path,
            r"fm2001_art\Generic\front-end-shirts\custom\Chelsea.444",
        )
        # 0x408320's generic branch reads DBRClub+0x47 and clamps 0..36.
        self.assertEqual(selected.home.generic_template_index, 7)
        self.assertEqual(selected.away.generic_template_index, 12)
        self.assertTrue(selected.home.generic_source_path.endswith(r"Team07.bmp"))
        self.assertTrue(selected.away.generic_source_path.endswith(r"Team12.bmp"))

    def test_primary_clash_uses_5ef940_away_alternate_first(self):
        home = club(10, "Home", 1, 5, 3, 7)
        away = club(11, "Away", 2, 6, 4, 8)
        selected = select_prematch_team_kits(
            home,
            away,
            clash_table=clash_table((3, 4)),
        )
        self.assertFalse(selected.home.use_alternate)
        self.assertTrue(selected.away.use_alternate)
        self.assertIsNotNone(selected.home.custom_source_path)
        self.assertIsNone(selected.away.custom_source_path)
        self.assertEqual(selected.away.selected_template_index, 6)

    def test_clash_falls_to_home_alternate_then_both_alternate(self):
        table = clash_table((3, 4))

        # Home primary == away alternate, but home alternate differs from away primary.
        home = club(10, "Home", 1, 5, 3, 9)
        away = club(11, "Away", 2, 6, 4, 3)
        selected = select_prematch_team_kits(home, away, clash_table=table)
        self.assertTrue(selected.home.use_alternate)
        self.assertFalse(selected.away.use_alternate)

        # Both cross-tests collide, but the two alternates differ.
        home = club(10, "Home", 1, 5, 3, 4)
        away = club(11, "Away", 2, 6, 4, 3)
        selected = select_prematch_team_kits(home, away, clash_table=table)
        self.assertTrue(selected.home.use_alternate)
        self.assertTrue(selected.away.use_alternate)

    def test_bidirectional_clash_table_and_invalid_table_fail_closed(self):
        # Native 0x5EF9E0 searches both rows, so a reverse-only table entry counts.
        home = club(10, "Home", 1, 5, 3, 9)
        away = club(11, "Away", 2, 6, 4, 8)
        selected = select_prematch_team_kits(
            home,
            away,
            clash_table=clash_table((4, 3)),
        )
        self.assertTrue(selected.away.use_alternate)

        with self.assertRaisesRegex(PrematchShirtSelectionError, "138 source bytes"):
            select_prematch_team_kits(home, away, clash_table=b"short")

    def test_club_adapter_requires_new_source_backed_fields(self):
        source = SimpleNamespace(
            index=10,
            graphics_basename="Arsenal",
            primary_shirt_template_index=1,
            alternate_shirt_template_index=2,
            primary_kit_color_id=3,
            alternate_kit_color_id=4,
        )
        state = club_shirt_state(source)
        self.assertEqual(
            (
                state.club_id,
                state.primary_template_index,
                state.alternate_template_index,
                state.primary_color_id,
                state.alternate_color_id,
            ),
            (10, 1, 2, 3, 4),
        )
        with self.assertRaisesRegex(PrematchShirtSelectionError, "lacks source-backed"):
            club_shirt_state(SimpleNamespace(index=10, graphics_basename="Arsenal"))

    def test_player_frame_offset_preserves_41e3d0_team_identity_branch(self):
        # Matching team club id reads DBRPlayer+0x70.
        self.assertEqual(
            prematch_player_shirt_frame_offset(
                player_registered_club_id=10,
                team_club_id=10,
                primary_shirt_number=7,
                alternate_shirt_number=19,
            ),
            (7 - 1) * 32,
        )
        # Mismatched team club id reads DBRPlayer+0x76.
        self.assertEqual(
            prematch_player_shirt_frame_offset(
                player_registered_club_id=10,
                team_club_id=99,
                primary_shirt_number=7,
                alternate_shirt_number=19,
            ),
            (19 - 1) * 32,
        )
        # Native PPreMatch does not clamp the byte before subtracting one frame.
        self.assertEqual(
            prematch_player_shirt_frame_offset(
                player_registered_club_id=10,
                team_club_id=10,
                primary_shirt_number=0,
                alternate_shirt_number=1,
            ),
            -32,
        )


if __name__ == "__main__":
    unittest.main()
