"""Tests for the four exact executable-correlated Squad resources."""
from pathlib import Path
import tempfile
import unittest

from original_squad_resources import (
    CBASE_PLAYER_LIST_CLASS,
    CBASE_PLAYER_LIST_TYPE_DESCRIPTOR_VA,
    CBASE_PLAYER_LIST_VFTABLE_VA,
    FORMATION_TEXT_BAR_FRAME_SIZE,
    FORMATION_TEXT_BAR_SETUP_VA,
    FORMATION_TEXT_CLASS,
    FORMATION_TEXT_FORM_FRAME_SIZE,
    FORMATION_TEXT_FORM_SETUP_VA,
    FORMATION_TEXT_ROWS,
    FORMATION_TEXT_TYPE_DESCRIPTOR_VA,
    FORMATION_TEXT_VFTABLE_VA,
    FORMATION_TEXT_GROUP_LENGTHS,
    FORMATION_TEXT_GROUP_SELECTOR_VA,
    FORMATION_TEXT_SOURCE_OFFSET_VA,
    OriginalSquadResourceError,
    SQUAD_BUTTONS,
    SQUAD_BUTTON_ORIGINS,
    SQUAD_RESOURCES,
    SQUAD_SCREEN_CLASS,
    SQUAD_SCREEN_SETUP_VA,
    SQUAD_SCREEN_TYPE_DESCRIPTOR_VA,
    SQUAD_SCREEN_VFTABLE_VA,
    SQUAD_PANEL_FACTORY_VA,
    SQUAD_PANEL_FACTORY_BRANCH_VA,
    SQUAD_PANEL_LAYOUT_CALL_VA,
    SQUAD_PANEL_RECT,
    SQUAD_FIRST_ROSTER_OFFSET,
    SQUAD_FIRST_ROSTER_RECT,
    SQUAD_PITCH_CLASS,
    SQUAD_PITCH_OFFSET,
    SQUAD_PITCH_RECT,
    SQUAD_PITCH_SETUP_VA,
    SQUAD_PITCH_TYPE_DESCRIPTOR_VA,
    SQUAD_PITCH_VFTABLE_VA,
    SQUAD_RESERVE_ROSTER_OFFSET,
    SQUAD_RESERVE_ROSTER_RECT,
    SQUAD_SCREEN_EVENT_HANDLER_VA,
    SQUAD_VIEW_TRANSITIONS,
    PSQUAD_LIST_TYPE_DESCRIPTOR_VA,
    PSQUAD_LIST_VFTABLE_VA,
    PSQUAD_LIST_SETUP_VA,
    CSQUAD_PLAYER_LIST_TYPE_DESCRIPTOR_VA,
    CSQUAD_SCF_LIST_TYPE_DESCRIPTOR_VA,
    PSQUAD_PLAYER_ROW_TYPE_DESCRIPTOR_VA,
    PSCF_ROW_TYPE_DESCRIPTOR_VA,
    PPLAYER_EMPTY_ROW_TYPE_DESCRIPTOR_VA,
    PSCF_EMPTY_ROW_TYPE_DESCRIPTOR_VA,
    SQUAD_VISIBLE_ROW_COUNT,
    SQUAD_VISIBLE_ROW_Y_ORIGINS,
    SQUAD_PLAYER_COLUMNS,
    SQUAD_SCF_COLUMNS,
    SQUAD_STATUS_FILTER_CODE_BY_MASK,
    formation_text_source_row,
    formation_text_source_y,
    validate_imported_original_squad_resources,
    validate_original_squad_button_labels,
)


class OriginalSquadResourceTests(unittest.TestCase):
    def test_imported_bytes_match_hashes_and_header_geometry(self):
        root = Path(__file__).resolve().parent.parent / "original_assets" / "source"
        self.assertEqual(
            validate_imported_original_squad_resources(root), SQUAD_RESOURCES
        )

    def test_native_owner_boundary_does_not_promote_blue_toggle_to_squad_screen(self):
        by_name = {Path(item.source_path).name: item for item in SQUAD_RESOURCES}
        self.assertEqual(
            by_name["squad_but_anim.444"].native_owners,
            (SQUAD_SCREEN_CLASS,),
        )
        self.assertNotIn(
            SQUAD_SCREEN_CLASS, by_name["blue_toggle.444"].native_owners
        )
        self.assertEqual(
            by_name["blue_toggle.444"].native_owners,
            ("PFormation2k", "PSCFTitle", "PTraining", "PYouthTeam"),
        )

    def test_native_squad_screen_identity_and_button_origins_are_locked(self):
        self.assertEqual(SQUAD_SCREEN_TYPE_DESCRIPTOR_VA, 0x819D48)
        self.assertEqual(SQUAD_SCREEN_VFTABLE_VA, 0x7C5CA4)
        self.assertEqual(SQUAD_SCREEN_SETUP_VA, 0x4B5720)
        self.assertEqual(SQUAD_BUTTON_ORIGINS, ((37, 92), (113, 92), (189, 92)))
        self.assertEqual(SQUAD_PANEL_FACTORY_VA, 0x47AEC0)
        self.assertEqual(SQUAD_PANEL_FACTORY_BRANCH_VA, 0x47AF2D)
        self.assertEqual(SQUAD_PANEL_LAYOUT_CALL_VA, 0x47AF80)
        self.assertEqual(SQUAD_PANEL_RECT, (0, 79, 800, 520))

    def test_native_button_ids_offsets_globals_and_language_bindings_are_locked(self):
        self.assertEqual(
            tuple(
                (
                    item.control_id,
                    item.object_offset,
                    item.label_global_va,
                    item.language_index,
                    item.original_text,
                    item.origin,
                )
                for item in SQUAD_BUTTONS
            ),
            (
                (3, 0x37A4, 0x982110, 2490, "1ST & RES", (37, 92)),
                (4, 0x37F8, 0x98210C, 2491, "1ST FORM", (113, 92)),
                (5, 0x384C, 0x982108, 2492, "RES. FORM", (189, 92)),
            ),
        )

    def test_original_language_pair_resolves_native_squad_labels(self):
        root = Path(__file__).resolve().parent.parent / "original_assets" / "source"
        self.assertEqual(
            validate_original_squad_button_labels(
                root / "English.str", root / "English.idx"
            ),
            SQUAD_BUTTONS,
        )

    def test_roster_panels_pitch_bounds_and_event_transitions_are_locked(self):
        self.assertEqual(CBASE_PLAYER_LIST_CLASS, "CBasePlayerList")
        self.assertEqual(CBASE_PLAYER_LIST_TYPE_DESCRIPTOR_VA, 0x81DCB8)
        self.assertEqual(CBASE_PLAYER_LIST_VFTABLE_VA, 0x7C5BC8)
        self.assertEqual(SQUAD_FIRST_ROSTER_OFFSET, 0x130)
        self.assertEqual(SQUAD_RESERVE_ROSTER_OFFSET, 0x1030)
        self.assertEqual(SQUAD_PITCH_OFFSET, 0x1F30)
        self.assertEqual(tuple(SQUAD_FIRST_ROSTER_RECT.__dict__.values()), (37, 0, 228, 520))
        self.assertEqual(tuple(SQUAD_RESERVE_ROSTER_RECT.__dict__.values()), (418, 0, 228, 520))
        self.assertEqual(tuple(SQUAD_PITCH_RECT.__dict__.values()), (388, 92, 412, 432))
        self.assertEqual(SQUAD_SCREEN_EVENT_HANDLER_VA, 0x4B8E70)
        self.assertEqual(
            tuple(
                (
                    item.control_id,
                    item.original_text,
                    item.left_roster,
                    item.second_roster_mask1,
                    item.pitch_mask1,
                    item.pitch_team_index,
                )
                for item in SQUAD_VIEW_TRANSITIONS
            ),
            (
                (3, "1ST & RES", "first", True, False, None),
                (4, "1ST FORM", "first", False, True, 0),
                (5, "RES. FORM", "reserve", False, True, 1),
            ),
        )

    def test_formation_text_rows_have_exact_native_geometry_and_ids(self):
        self.assertEqual(SQUAD_PITCH_CLASS, "PSquadPitch")
        self.assertEqual(SQUAD_PITCH_TYPE_DESCRIPTOR_VA, 0x81DB30)
        self.assertEqual(SQUAD_PITCH_VFTABLE_VA, 0x7C54A8)
        self.assertEqual(SQUAD_PITCH_SETUP_VA, 0x4B3C80)
        self.assertEqual(FORMATION_TEXT_CLASS, "FormationText")
        self.assertEqual(FORMATION_TEXT_TYPE_DESCRIPTOR_VA, 0x81DBC0)
        self.assertEqual(FORMATION_TEXT_VFTABLE_VA, 0x7C5700)
        self.assertEqual(FORMATION_TEXT_FORM_SETUP_VA, 0x4B6C30)
        self.assertEqual(FORMATION_TEXT_BAR_SETUP_VA, 0x4B6B60)
        self.assertEqual(FORMATION_TEXT_FORM_FRAME_SIZE, (23, 16))
        self.assertEqual(FORMATION_TEXT_BAR_FRAME_SIZE, (81, 16))
        self.assertEqual(len(FORMATION_TEXT_ROWS), 22)
        self.assertEqual(
            (
                FORMATION_TEXT_ROWS[0].form_control_id,
                FORMATION_TEXT_ROWS[0].bar_control_id,
                FORMATION_TEXT_ROWS[0].form_object_offset,
                FORMATION_TEXT_ROWS[0].bar_object_offset,
                tuple(FORMATION_TEXT_ROWS[0].form_rect.__dict__.values()),
                tuple(FORMATION_TEXT_ROWS[0].bar_rect.__dict__.values()),
            ),
            (12, 13, 0x8C0, 0x1050, (279, 25, 23, 16), (303, 25, 81, 16)),
        )
        self.assertEqual(
            (
                FORMATION_TEXT_ROWS[-1].form_control_id,
                FORMATION_TEXT_ROWS[-1].bar_control_id,
                FORMATION_TEXT_ROWS[-1].form_object_offset,
                FORMATION_TEXT_ROWS[-1].bar_object_offset,
                tuple(FORMATION_TEXT_ROWS[-1].form_rect.__dict__.values()),
                tuple(FORMATION_TEXT_ROWS[-1].bar_rect.__dict__.values()),
            ),
            (54, 55, 0xFF8, 0x1788, (279, 382, 23, 16), (303, 382, 81, 16)),
        )
        self.assertTrue(
            all(
                row.form_rect.y == 25 + row.index * 17
                and row.bar_rect.y == row.form_rect.y
                for row in FORMATION_TEXT_ROWS
            )
        )

    def test_concrete_squad_list_row_hierarchy_and_columns_are_locked(self):
        self.assertEqual(
            (
                PSQUAD_LIST_TYPE_DESCRIPTOR_VA,
                PSQUAD_LIST_VFTABLE_VA,
                PSQUAD_LIST_SETUP_VA,
            ),
            (0x81DC60, 0x7C5864, 0x4B4FE0),
        )
        self.assertEqual(CSQUAD_PLAYER_LIST_TYPE_DESCRIPTOR_VA, 0x81DD00)
        self.assertEqual(CSQUAD_SCF_LIST_TYPE_DESCRIPTOR_VA, 0x81DC98)
        self.assertEqual(PSQUAD_PLAYER_ROW_TYPE_DESCRIPTOR_VA, 0x81DBE0)
        self.assertEqual(PSCF_ROW_TYPE_DESCRIPTOR_VA, 0x81D348)
        self.assertEqual(PPLAYER_EMPTY_ROW_TYPE_DESCRIPTOR_VA, 0x81D2B0)
        self.assertEqual(PSCF_EMPTY_ROW_TYPE_DESCRIPTOR_VA, 0x81DC40)
        self.assertEqual(SQUAD_VISIBLE_ROW_COUNT, 20)
        self.assertEqual(SQUAD_VISIBLE_ROW_Y_ORIGINS, tuple(range(154, 478, 17)))
        self.assertEqual(
            [(c.name, c.x, c.width) for c in SQUAD_PLAYER_COLUMNS],
            [
                ("club_relative_assignment", 1, 22),
                ("assigned_role", 28, 38),
                ("display_name", 76, 144),
            ],
        )
        self.assertEqual(
            [(c.name, c.x, c.width) for c in SQUAD_SCF_COLUMNS],
            [
                ("native_status_icon", 1, None),
                ("condition", 24, 19),
                ("recent_form_average", 47, 19),
                ("current_role_rating", 70, 19),
            ],
        )
        self.assertEqual(
            SQUAD_STATUS_FILTER_CODE_BY_MASK,
            ((1, 3), (2, 0), (4, 1), (8, 2)),
        )

    def test_formation_text_native_state_to_source_row_transform_is_locked(self):
        self.assertEqual(FORMATION_TEXT_GROUP_LENGTHS, (2, 1, 1))
        self.assertEqual(FORMATION_TEXT_GROUP_SELECTOR_VA, 0x652AE0)
        self.assertEqual(FORMATION_TEXT_SOURCE_OFFSET_VA, 0x5D4D70)
        self.assertEqual(
            formation_text_source_row(enabled=True, complete=False, subframe=0), 0
        )
        self.assertEqual(
            formation_text_source_row(enabled=True, complete=False, subframe=1), 1
        )
        self.assertEqual(formation_text_source_row(enabled=True, complete=True), 2)
        self.assertEqual(formation_text_source_y(enabled=True, complete=True), 32)
        self.assertEqual(formation_text_source_row(enabled=False, complete=False), 4)
        with self.assertRaises(OriginalSquadResourceError):
            formation_text_source_row(enabled=True, complete=True, subframe=1)

    def test_wrong_imported_bytes_fail_closed(self):
        source = Path(__file__).resolve().parent.parent / "original_assets" / "source"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for resource in SQUAD_RESOURCES:
                target = root / resource.source_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((source / resource.source_path).read_bytes())
            first = root / SQUAD_RESOURCES[0].source_path
            first.write_bytes(first.read_bytes() + b"corrupt")
            with self.assertRaisesRegex(
                OriginalSquadResourceError, "checksum mismatch"
            ):
                validate_imported_original_squad_resources(root)


if __name__ == "__main__":
    unittest.main()
