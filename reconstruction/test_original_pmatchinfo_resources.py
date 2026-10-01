"""Regressions for source-backed PMatchInfo Match_report resources."""
from pathlib import Path
import tempfile
import unittest

import original_pmatchinfo_resources as pmatch

from original_pmatchinfo_resources import (
    PMATCHINFO_RESOURCE_BY_NAME,
    PMATCHINFO_RESOURCES,
    PMATCHINFO_RESOURCE_PLACEMENTS,
    PMATCHINFO_SCRIPT_ROW1_CLASS,
    PMATCHINFO_SCRIPT_ROW1_TYPE_DESCRIPTOR_VA,
    PMATCHINFO_SCRIPT_ROW1_COL_VA,
    PMATCHINFO_SCRIPT_ROW1_VFTABLE_VA,
    PMATCHINFO_SCRIPT_ROW1_SETUP_VA,
    PMATCHINFO_SCRIPT_ROW1_UPDATE_VA,
    PMATCHINFO_SCRIPT_ROW2_CLASS,
    PMATCHINFO_SCRIPT_ROW2_TYPE_DESCRIPTOR_VA,
    PMATCHINFO_SCRIPT_ROW2_COL_VA,
    PMATCHINFO_SCRIPT_ROW2_VFTABLE_VA,
    PMATCHINFO_SCRIPT_ROW2_SETUP_VA,
    PMATCHINFO_SCRIPT_ROW2_UPDATE_VA,
    PMATCHINFO_DYNAMIC_INCIDENT_CONTROL_OFFSET,
    PMATCHINFO_DYNAMIC_INCIDENT_RESOURCE_SLOT_OFFSET,
    PMATCHINFO_DYNAMIC_INCIDENT_RECT,
    PMATCHINFO_DYNAMIC_INCIDENT_RESOURCE_NAMES,
    PMATCHINFO_BITMAP_DESCRIPTOR_SETUP_VA,
    PMATCHINFO_CONTROL_RECT_SETUP_VA,
    PMATCHINFO_CONTROL_CALLBACK_TARGET_VA,
    PMATCHINFO_CONTROL_CALLBACK_TARGET_CLASS,
    PMATCHINFO_CONTROL_CALLBACK_TARGET_TYPE_DESCRIPTOR_VA,
    PMATCHINFO_CONTROL_CALLBACK_TARGET_COL_VA,
    PMATCHINFO_CONTROL_CALLBACK_TARGET_VFTABLE_VA,
    PMATCHINFO_TEXT_SETUP_VA,
    PMATCHINFO_TEXT_PLACEMENTS,
    PMATCHINFO_TEXT_FONT_GLOBAL_VA,
    PMATCHINFO_TEXT_FONT_SOURCE_PATH,
    PMATCHINFO_TEXT_FONT_SHA256,
    PMATCHINFO_TEXT_FONT_NATIVE_LINE_HEIGHT,
    PMATCHINFO_SUBPANEL_BASE_CLASS,
    PMATCHINFO_SUBPANEL_BASE_COL_VA,
    PMATCHINFO_SUBPANEL_BASE_TYPE_DESCRIPTOR_VA,
    PMATCHINFO_SUBPANEL_BASE_VFTABLE_VA,
    PMATCHINFO_SUBPANEL_CLASS,
    PMATCHINFO_SUBPANEL_COL_VA,
    PMATCHINFO_SUBPANEL_TYPE_DESCRIPTOR_VA,
    PMATCHINFO_SUBPANEL_VFTABLE_VA,
    OriginalPMatchInfoResourceError,
    assert_pmatchinfo_identity_contract,
    assert_pmatchinfo_placement_resources_are_bound,
    pmatchinfo_dynamic_incident_resources,
    pmatchinfo_placements_for_resource,
    validate_original_pmatchinfo_resources,
)


class OriginalPMatchInfoResourceTests(unittest.TestCase):
    def test_twenty_exact_match_report_resources_are_bound(self):
        self.assertEqual(len(PMATCHINFO_RESOURCES), 20)
        self.assertEqual(
            [resource.name for resource in PMATCHINFO_RESOURCES],
            [
                "info_player",
                "info_player_disabled",
                "info_popup",
                "red_card",
                "yellow_card",
                "sub_on",
                "sub_off",
                "injured",
                "score",
                "red_card_single",
                "name_block_1",
                "name_block_2",
                "name_block_3",
                "name_block_4",
                "match_name_grid",
                "poss_back",
                "poss_blue",
                "poss_yellow",
                "pitch_normal",
                "match_incid_grid",
            ],
        )

    def test_static_raw_and_wrapper_handles_form_exact_contiguous_family(self):
        self.assertEqual(
            [resource.raw_handle_va for resource in PMATCHINFO_RESOURCES],
            [0x943570 - 0x40 * index for index in range(20)],
        )
        self.assertEqual(
            [resource.wrapper_va for resource in PMATCHINFO_RESOURCES],
            [0x943550 - 0x40 * index for index in range(20)],
        )
        self.assertTrue(
            all(
                resource.raw_handle_va - resource.wrapper_va == 0x20
                for resource in PMATCHINFO_RESOURCES
            )
        )

    def test_path_literals_are_exact_and_monotonic_source_family(self):
        expected = [
            0x837E9C, 0x837ECC, 0x837F08, 0x837F38, 0x837F68,
            0x837F98, 0x837FC4, 0x837FF0, 0x83801C, 0x838048,
            0x83807C, 0x8380B0, 0x8380E4, 0x838118, 0x83814C,
            0x838180, 0x8381B0, 0x8381E0, 0x838210, 0x838244,
        ]
        self.assertEqual(
            [resource.path_literal_va for resource in PMATCHINFO_RESOURCES],
            expected,
        )
        self.assertTrue(
            all(
                resource.source_path.startswith(
                    "FM2001_Art/Generic/match_report/"
                )
                for resource in PMATCHINFO_RESOURCES
            )
        )

    def test_background_and_core_grid_geometries_match_firsthand_source(self):
        self.assertEqual(PMATCHINFO_RESOURCE_BY_NAME["info_popup"].size, (760, 500))
        self.assertEqual(PMATCHINFO_RESOURCE_BY_NAME["info_player"].size, (274, 16))
        self.assertEqual(
            PMATCHINFO_RESOURCE_BY_NAME["info_player_disabled"].size,
            (274, 16),
        )
        self.assertEqual(PMATCHINFO_RESOURCE_BY_NAME["match_name_grid"].size, (185, 36))
        self.assertEqual(PMATCHINFO_RESOURCE_BY_NAME["match_incid_grid"].size, (142, 36))
        self.assertEqual(PMATCHINFO_RESOURCE_BY_NAME["pitch_normal"].size, (294, 78))

    def test_local_resource_placements_preserve_exact_64f380_rectangles(self):
        expected = [
            ("match_name_grid", 0x483500, 0x483541, 0x483591, (0, 0, 185, 36)),
            ("match_incid_grid", 0x483500, 0x4835AD, 0x4835E7, (189, 0, 142, 36)),
            ("yellow_card", 0x483500, 0x48366D, 0x483674, (191, 11, 14, 14)),
            ("match_name_grid", 0x483750, 0x483784, 0x4837D0, (0, 0, 185, 36)),
            ("match_incid_grid", 0x483750, 0x4837EC, 0x483826, (189, 0, 142, 36)),
            ("info_player", 0x483840, 0x4838AC, 0x4838B3, (0, 0, 274, 16)),
            (
                "info_player_disabled",
                0x483A30,
                0x483A81,
                0x483A88,
                (0, 0, 252, 16),
            ),
            ("pitch_normal", 0x483AA0, 0x483B1E, 0x483B72, (233, -2, 294, 78)),
            ("info_popup", 0x484F90, 0x484FFF, 0x485059, (0, 0, 760, 500)),
        ]
        self.assertEqual(
            [
                (
                    placement.resource_name,
                    placement.owner_method_va,
                    placement.resource_bind_va,
                    placement.rect_setup_call_va,
                    placement.rect,
                )
                for placement in PMATCHINFO_RESOURCE_PLACEMENTS
            ],
            expected,
        )
        self.assertEqual(PMATCHINFO_CONTROL_RECT_SETUP_VA, 0x64F380)
        self.assertEqual(PMATCHINFO_BITMAP_DESCRIPTOR_SETUP_VA, 0x64E500)

    def test_disabled_player_strip_is_source_clipped_not_stretched(self):
        source = PMATCHINFO_RESOURCE_BY_NAME["info_player_disabled"]
        placement = pmatchinfo_placements_for_resource("info_player_disabled")
        self.assertEqual(source.size, (274, 16))
        self.assertEqual(len(placement), 1)
        self.assertEqual(placement[0].rect, (0, 0, 252, 16))
        self.assertLess(placement[0].width, source.size[0])

    def test_pitch_preserves_negative_local_y_origin(self):
        placement = pmatchinfo_placements_for_resource("pitch_normal")
        self.assertEqual(len(placement), 1)
        self.assertEqual(placement[0].rect, (233, -2, 294, 78))

    def test_reused_name_and_incident_grids_keep_same_local_geometry(self):
        self.assertEqual(
            [placement.rect for placement in pmatchinfo_placements_for_resource("match_name_grid")],
            [(0, 0, 185, 36), (0, 0, 185, 36)],
        )
        self.assertEqual(
            [placement.rect for placement in pmatchinfo_placements_for_resource("match_incid_grid")],
            [(189, 0, 142, 36), (189, 0, 142, 36)],
        )

    def test_64f380_callback_target_is_ecdbitmap_not_a_guessed_font(self):
        self.assertEqual(PMATCHINFO_CONTROL_CALLBACK_TARGET_VA, 0x87BF00)
        self.assertEqual(PMATCHINFO_CONTROL_CALLBACK_TARGET_CLASS, "eCDBitmap")
        self.assertEqual(
            PMATCHINFO_CONTROL_CALLBACK_TARGET_TYPE_DESCRIPTOR_VA,
            0x819C48,
        )
        self.assertEqual(PMATCHINFO_CONTROL_CALLBACK_TARGET_COL_VA, 0x7E1248)
        self.assertEqual(PMATCHINFO_CONTROL_CALLBACK_TARGET_VFTABLE_VA, 0x7BFE14)
        self.assertTrue(
            all(
                placement.callback_target_va == PMATCHINFO_CONTROL_CALLBACK_TARGET_VA
                for placement in PMATCHINFO_RESOURCE_PLACEMENTS
            )
        )

    def test_placement_lookup_fails_closed_and_geometry_stays_within_source(self):
        assert_pmatchinfo_placement_resources_are_bound()
        self.assertEqual(pmatchinfo_placements_for_resource("poss_back"), ())
        for bad in ("", "not-a-resource", None, 1):
            with self.subTest(bad=bad):
                with self.assertRaises(OriginalPMatchInfoResourceError):
                    pmatchinfo_placements_for_resource(bad)

    def test_text_setup_uses_source_bound_zurich_16_font_and_exact_rectangles(self):
        self.assertEqual(PMATCHINFO_TEXT_SETUP_VA, 0x6503F0)
        self.assertEqual(PMATCHINFO_TEXT_FONT_GLOBAL_VA, 0x87BEA0)
        self.assertEqual(
            PMATCHINFO_TEXT_FONT_SOURCE_PATH,
            "Fonts/Zurich_BdXCn_BT_16pixel.fnt",
        )
        self.assertEqual(
            PMATCHINFO_TEXT_FONT_SHA256,
            "9dc371caba34823b0d6ba6fd4c5e82f94775de1168daa5dad936b70a6e4f9732",
        )
        self.assertEqual(PMATCHINFO_TEXT_FONT_NATIVE_LINE_HEIGHT, 18)
        self.assertEqual(
            [
                (placement.owner_method_va, placement.setup_call_va, placement.rect)
                for placement in PMATCHINFO_TEXT_PLACEMENTS
            ],
            [
                (0x483500, 0x4836AC, (210, 2, 185, 12)),
                (0x483500, 0x4836E4, (210, 18, 185, 12)),
                (0x483840, 0x483918, (33, 0, 29, 16)),
                (0x484F90, 0x485091, (172, 50, 416, 16)),
                (0x484F90, 0x4850C9, (380, 68, 208, 16)),
                (0x484F90, 0x485101, (172, 68, 208, 16)),
            ],
        )
        self.assertTrue(
            all(
                placement.font_global_va == PMATCHINFO_TEXT_FONT_GLOBAL_VA
                for placement in PMATCHINFO_TEXT_PLACEMENTS
            )
        )

    def test_text_control_height_does_not_get_replaced_by_font_line_height(self):
        self.assertEqual(PMATCHINFO_TEXT_FONT_NATIVE_LINE_HEIGHT, 18)
        self.assertEqual(
            [placement.height for placement in PMATCHINFO_TEXT_PLACEMENTS[:2]],
            [12, 12],
        )
        self.assertNotEqual(
            PMATCHINFO_TEXT_PLACEMENTS[0].height,
            PMATCHINFO_TEXT_FONT_NATIVE_LINE_HEIGHT,
        )

    def test_dynamic_incident_control_is_one_shared_exact_row_slot(self):
        self.assertEqual(PMATCHINFO_SCRIPT_ROW1_CLASS, "PScriptRow1")
        self.assertEqual(PMATCHINFO_SCRIPT_ROW1_TYPE_DESCRIPTOR_VA, 0x81CEE8)
        self.assertEqual(PMATCHINFO_SCRIPT_ROW1_COL_VA, 0x7E4890)
        self.assertEqual(PMATCHINFO_SCRIPT_ROW1_VFTABLE_VA, 0x7C3F34)
        self.assertEqual(PMATCHINFO_SCRIPT_ROW1_SETUP_VA, 0x483500)
        self.assertEqual(PMATCHINFO_SCRIPT_ROW1_UPDATE_VA, 0x4858E0)

        self.assertEqual(PMATCHINFO_SCRIPT_ROW2_CLASS, "PScriptRow2")
        self.assertEqual(PMATCHINFO_SCRIPT_ROW2_TYPE_DESCRIPTOR_VA, 0x81CF08)
        self.assertEqual(PMATCHINFO_SCRIPT_ROW2_COL_VA, 0x7E48E0)
        self.assertEqual(PMATCHINFO_SCRIPT_ROW2_VFTABLE_VA, 0x7C3F88)
        self.assertEqual(PMATCHINFO_SCRIPT_ROW2_SETUP_VA, 0x483500)
        self.assertEqual(PMATCHINFO_SCRIPT_ROW2_UPDATE_VA, 0x485F50)

        self.assertEqual(PMATCHINFO_DYNAMIC_INCIDENT_CONTROL_OFFSET, 0x1C8)
        self.assertEqual(PMATCHINFO_DYNAMIC_INCIDENT_RESOURCE_SLOT_OFFSET, 0x1F4)
        self.assertEqual(PMATCHINFO_DYNAMIC_INCIDENT_RECT, (191, 11, 14, 14))
        self.assertEqual(
            PMATCHINFO_DYNAMIC_INCIDENT_RESOURCE_NAMES,
            (
                "score",
                "injured",
                "yellow_card",
                "red_card",
                "red_card_single",
                "sub_on",
                "sub_off",
            ),
        )

        resources = pmatchinfo_dynamic_incident_resources()
        self.assertEqual(
            tuple(resource.name for resource in resources),
            PMATCHINFO_DYNAMIC_INCIDENT_RESOURCE_NAMES,
        )
        self.assertTrue(all(resource.size == (14, 14) for resource in resources))

        yellow_setup = pmatchinfo_placements_for_resource("yellow_card")
        self.assertEqual(len(yellow_setup), 1)
        self.assertEqual(yellow_setup[0].owner_method_va, 0x483500)
        self.assertEqual(yellow_setup[0].rect_setup_call_va, 0x483674)
        self.assertEqual(yellow_setup[0].rect, PMATCHINFO_DYNAMIC_INCIDENT_RECT)

        row_consumers = {
            "score": (0x4859D5, 0x486045),
            "injured": (0x4859FD, 0x48606D),
            "yellow_card": (0x485A24, 0x486094),
            "red_card": (0x485A50, 0x4860C0),
            "red_card_single": (0x485A5C, 0x4860CC),
            "sub_on": (0x485A81, 0x4860F1),
            "sub_off": (0x485A9E, 0x48610E),
        }
        for resource in resources:
            with self.subTest(resource=resource.name):
                row1, row2 = row_consumers[resource.name]
                self.assertIn(row1, resource.direct_consumer_vas)
                self.assertIn(row2, resource.direct_consumer_vas)
                self.assertGreaterEqual(row1, PMATCHINFO_SCRIPT_ROW1_UPDATE_VA)
                self.assertLess(row1, PMATCHINFO_SCRIPT_ROW2_UPDATE_VA)
                self.assertGreaterEqual(row2, PMATCHINFO_SCRIPT_ROW2_UPDATE_VA)

    def test_pmatchinfo_english_globals_match_complete_loader_entries(self):
        self.assertEqual(pmatch.PMATCHINFO_ENGLISH_LOADER_START_VA, 0x635F30)
        self.assertEqual(pmatch.PMATCHINFO_ENGLISH_LOADER_END_VA, 0x64C7D4)
        self.assertEqual(pmatch.PMATCHINFO_ENGLISH_LOADER_ENTRY_COUNT, 2714)
        expected = {
            0x982C40: (1774, "Attendance"),
            0x982C3C: (1775, "TEAM INFO"),
            0x982C38: (1776, "MATCH INFO"),
            0x982BA4: (1813, "O.G."),
            0x982BA0: (1814, "(%d-%d pen)"),
            0x9826B8: (2128, "Mom"),
            0x9822E4: (2373, "Sent off"),
            0x982164: (2469, "Goal"),
            0x982160: (2470, "Sub Off"),
            0x98215C: (2471, "Sub On"),
            0x982158: (2472, "Booking"),
            0x982154: (2473, "Injury"),
            0x982100: (2494, "Shoot Out"),
            0x98200C: (2555, "Ref."),
            0x981EA4: (2645, "%s: %s %s"),
            0x981E98: (2648, "first leg"),
            0x981E94: (2649, "second leg"),
        }
        self.assertEqual(
            {
                binding.global_va: (binding.english_index, binding.original_text)
                for binding in pmatch.PMATCHINFO_LANGUAGE_BINDINGS
            },
            expected,
        )
        for global_va, (_, original_text) in expected.items():
            self.assertEqual(
                pmatch.pmatchinfo_original_english(global_va),
                original_text,
            )
        for bad in (None, "0x982164", 0xDEADBEEF):
            with self.subTest(bad=bad):
                with self.assertRaises(OriginalPMatchInfoResourceError):
                    pmatch.pmatchinfo_original_english(bad)

    def test_script_row_text_producers_preserve_label_and_neutral_decimal_fields(self):
        self.assertEqual(
            (
                pmatch.PMATCHINFO_SCRIPT_EVENT_LABEL_CONTROL_OFFSET,
                pmatch.PMATCHINFO_SCRIPT_EVENT_LABEL_TEXT_POINTER_OFFSET,
                pmatch.PMATCHINFO_SCRIPT_EVENT_LABEL_BUFFER_OFFSET,
            ),
            (0x1F8, 0x224, 0xA0),
        )
        self.assertEqual(
            (
                pmatch.PMATCHINFO_SCRIPT_EVENT_DECIMAL_CONTROL_OFFSET,
                pmatch.PMATCHINFO_SCRIPT_EVENT_DECIMAL_TEXT_POINTER_OFFSET,
                pmatch.PMATCHINFO_SCRIPT_EVENT_DECIMAL_BUFFER_OFFSET,
                pmatch.PMATCHINFO_SCRIPT_EVENT_DECIMAL_SOURCE_OFFSET,
            ),
            (0x238, 0x264, 0x80, 0x00),
        )
        self.assertEqual(
            (
                pmatch.PMATCHINFO_SCRIPT_ROW1_LABEL_ASSIGN_VA,
                pmatch.PMATCHINFO_SCRIPT_ROW1_DECIMAL_ASSIGN_VA,
                pmatch.PMATCHINFO_SCRIPT_ROW2_LABEL_ASSIGN_VA,
                pmatch.PMATCHINFO_SCRIPT_ROW2_DECIMAL_ASSIGN_VA,
            ),
            (0x485AE6, 0x485AEC, 0x486156, 0x48615C),
        )
        self.assertEqual(pmatch.PMATCHINFO_SCRIPT_EVENT_DECIMAL_FORMAT, "%d")
        self.assertEqual(pmatch.PMATCHINFO_SCRIPT_EVENT_DECIMAL_FORMAT_VA, 0x81B1A8)
        self.assertEqual(pmatch.PMATCHINFO_SCRIPT_EMPTY_BUFFER_VA, 0x874BA0)

    def test_script_incident_selection_matches_source_precedence(self):
        self.assertEqual(
            pmatch.PMATCHINFO_SCRIPT_EVENT_TYPE_CLASS_BYTES,
            (0, 0, 0, 0, 0, 1, 3, 3, 3, 3, 2),
        )
        self.assertEqual(
            pmatch.PMATCHINFO_SCRIPT_ROW1_EVENT_CLASS_TARGETS,
            (0x48597B, 0x4859E4, 0x485A68, 0x485AA8),
        )

        cases = [
            ((0,), ("Goal", "score")),
            ((4,), ("Goal", "score")),
            ((0,), ("O.G.", "score"), {"row_field_74": 1}),
            ((0,), ("Shoot Out", "score"), {"row_field_78": 1}),
            ((5,), ("Injury", "injured"), {"event_field_20": 1}),
            ((5,), ("Booking", "yellow_card"), {"event_field_18": 1}),
            (
                (5,),
                ("Sent off", "red_card"),
                {"event_field_1c": 1, "row_field_74": 1},
            ),
            ((5,), ("Sent off", "red_card_single"), {"event_field_1c": 1}),
            ((10,), ("Sub On", "sub_on"), {"row_field_74": 1}),
            ((10,), ("Sub Off", "sub_off")),
        ]
        for case in cases:
            args, expected, *rest = case
            kwargs = rest[0] if rest else {}
            with self.subTest(args=args, kwargs=kwargs):
                selection = pmatch.pmatchinfo_script_incident_selection(
                    *args, **kwargs
                )
                self.assertIsNotNone(selection)
                self.assertEqual(
                    (selection.label, selection.resource_name),
                    expected,
                )

        # Source precedence is injury -> booking -> sent-off for event type 5.
        selection = pmatch.pmatchinfo_script_incident_selection(
            5,
            event_field_20=1,
            event_field_18=1,
            event_field_1c=1,
        )
        self.assertEqual(
            (selection.label, selection.resource_name),
            ("Injury", "injured"),
        )
        self.assertIsNone(pmatch.pmatchinfo_script_incident_selection(5))
        for event_type in (6, 7, 8, 9, 11):
            self.assertIsNone(
                pmatch.pmatchinfo_script_incident_selection(event_type)
            )
        with self.assertRaises(OriginalPMatchInfoResourceError):
            pmatch.pmatchinfo_script_incident_selection(-1)
        with self.assertRaises(OriginalPMatchInfoResourceError):
            pmatch.pmatchinfo_script_incident_selection("5")

    def test_player_strip_text_is_source_bound_to_dbtpositions_label(self):
        self.assertEqual(pmatch.PMATCHINFO_PLAYER_TEXT_SETUP_CALL_VA, 0x483918)
        self.assertEqual(pmatch.PMATCHINFO_PLAYER_TEXT_CONTROL_OFFSET, 0xB0)
        self.assertEqual(pmatch.PMATCHINFO_PLAYER_CONTEXT_INDEX_OFFSET, 0x70)
        self.assertEqual(pmatch.PMATCHINFO_PLAYER_CONTEXT_TABLE_VA, 0x875640)
        self.assertEqual(pmatch.PMATCHINFO_PLAYER_CONTEXT_RECORD_SIZE, 0x250)
        self.assertEqual(pmatch.PMATCHINFO_PLAYER_POSITION_CONTEXT_OFFSET, 0x248)
        self.assertEqual(pmatch.PMATCHINFO_POSITION_SELECTOR_VA, 0x4EA3C0)
        self.assertEqual(pmatch.PMATCHINFO_POSITION_SELECTOR_BYTE_OFFSET, 0x03)
        self.assertEqual(pmatch.PMATCHINFO_POSITION_SELECTOR_MASK, 0x1F)
        self.assertEqual(pmatch.PMATCHINFO_POSITIONS_CLASS, "DBTPositions")
        self.assertEqual(pmatch.PMATCHINFO_POSITIONS_OBJECT_VA, 0x874B60)
        self.assertEqual(pmatch.PMATCHINFO_POSITIONS_RECORD_BASE_VA, 0x874B68)
        self.assertEqual(pmatch.PMATCHINFO_POSITIONS_VFTABLE_VA, 0x7BD394)
        self.assertEqual(pmatch.PMATCHINFO_POSITIONS_COL_VA, 0x7DE8B8)
        self.assertEqual(
            pmatch.PMATCHINFO_POSITIONS_TYPE_DESCRIPTOR_VA,
            0x8182F8,
        )
        self.assertEqual(pmatch.PMATCHINFO_POSITIONS_RECORD_SIZE, 20)
        self.assertEqual(pmatch.PMATCHINFO_POSITIONS_STRING_FIELD_OFFSET, 0x0C)

    def test_popup_text_producers_bind_attendance_referee_and_mom_lines(self):
        self.assertEqual(pmatch.PMATCHINFO_POPUP_TEXT_UPDATE_VA, 0x4885A0)
        self.assertEqual(
            [
                (
                    producer.setup_call_va,
                    producer.control_offset,
                    producer.text_pointer_offset,
                    producer.buffer_offset,
                    producer.assign_va,
                    pmatch.pmatchinfo_original_english(
                        producer.leading_global_va
                    ),
                )
                for producer in pmatch.PMATCHINFO_POPUP_TEXT_PRODUCERS
            ],
            [
                (0x485091, 0x13E4, 0x1410, 0xB8, 0x48899A, "Attendance"),
                (0x4850C9, 0x1424, 0x1450, 0x140, 0x488A79, "Ref."),
                (0x485101, 0x1464, 0x1490, 0x180, 0x488AD2, "Mom"),
            ],
        )
        self.assertEqual(pmatch.PMATCHINFO_POPUP_ATTENDANCE_VALUE_OFFSET, 0x30)
        self.assertEqual(
            (
                pmatch.PMATCHINFO_POPUP_ATTENDANCE_DECIMAL_FORMAT_VA,
                pmatch.PMATCHINFO_POPUP_ATTENDANCE_DECIMAL_FORMAT,
                pmatch.PMATCHINFO_POPUP_ATTENDANCE_GROUP_FORMAT_VA,
                pmatch.PMATCHINFO_POPUP_ATTENDANCE_GROUP_FORMAT,
                pmatch.PMATCHINFO_POPUP_ATTENDANCE_COMMA_VA,
                pmatch.PMATCHINFO_POPUP_ATTENDANCE_COMMA,
            ),
            (0x81B1A8, "%d", 0x81D140, "%.3d", 0x81D148, ","),
        )
        self.assertEqual(pmatch.PMATCHINFO_POPUP_SPACE_LITERAL_VA, 0x81AF38)
        self.assertEqual(pmatch.PMATCHINFO_POPUP_SPACE_LITERAL, " ")
        self.assertEqual(
            pmatch.pmatchinfo_original_english(
                pmatch.PMATCHINFO_POPUP_FIRST_LEG_GLOBAL_VA
            ),
            "first leg",
        )
        self.assertEqual(
            pmatch.pmatchinfo_original_english(
                pmatch.PMATCHINFO_POPUP_SECOND_LEG_GLOBAL_VA
            ),
            "second leg",
        )

        self.assertEqual(
            pmatch.PMATCHINFO_POPUP_REFEREE_STRING_PRODUCER_VA,
            0x60BEB0,
        )
        self.assertEqual(pmatch.PMATCHINFO_POPUP_PENALTY_STATE_OFFSET, 0x1C)
        self.assertEqual(
            pmatch.pmatchinfo_original_english(
                pmatch.PMATCHINFO_POPUP_PENALTY_FORMAT_GLOBAL_VA
            ),
            "(%d-%d pen)",
        )

        self.assertEqual(pmatch.PMATCHINFO_POPUP_MOM_INDEX_OFFSET, 0x9C)
        self.assertEqual(pmatch.PMATCHINFO_POPUP_MOM_ABSENT_VALUE, -1)
        self.assertEqual(pmatch.PMATCHINFO_POPUP_MOM_PLAYER_TABLE_VA, 0x875640)
        self.assertEqual(pmatch.PMATCHINFO_POPUP_MOM_PLAYER_RECORD_SIZE, 0x250)
        self.assertEqual(
            pmatch.PMATCHINFO_POPUP_MOM_PLAYER_STRING_OFFSETS,
            (0x08, 0x0C),
        )
        self.assertEqual(
            pmatch.pmatchinfo_original_english(
                pmatch.PMATCHINFO_POPUP_MOM_FORMAT_GLOBAL_VA
            ),
            "%s: %s %s",
        )
        self.assertEqual(
            pmatch.pmatchinfo_original_english(
                pmatch.PMATCHINFO_POPUP_MOM_LABEL_GLOBAL_VA
            ),
            "Mom",
        )

    def test_incident_icon_family_is_exact_fourteen_square_pixels(self):
        for name in (
            "red_card",
            "yellow_card",
            "sub_on",
            "sub_off",
            "injured",
            "score",
            "red_card_single",
        ):
            with self.subTest(name=name):
                self.assertEqual(PMATCHINFO_RESOURCE_BY_NAME[name].size, (14, 14))

    def test_direct_consumers_are_recorded_only_where_source_traced(self):
        expected_direct = {
            "info_player",
            "info_player_disabled",
            "info_popup",
            "red_card",
            "yellow_card",
            "sub_on",
            "sub_off",
            "injured",
            "score",
            "red_card_single",
            "match_name_grid",
            "pitch_normal",
            "match_incid_grid",
        }
        actual_direct = {
            resource.name
            for resource in PMATCHINFO_RESOURCES
            if resource.direct_consumer_vas
        }
        self.assertEqual(actual_direct, expected_direct)
        self.assertEqual(
            PMATCHINFO_RESOURCE_BY_NAME["info_popup"].direct_consumer_handle,
            "raw",
        )
        self.assertEqual(
            PMATCHINFO_RESOURCE_BY_NAME["red_card"].direct_consumer_handle,
            "wrapper",
        )
        self.assertEqual(
            PMATCHINFO_RESOURCE_BY_NAME["name_block_1"].direct_consumer_vas,
            (),
        )

    def test_pmatchinfo_subpanel_rtti_is_source_bound(self):
        self.assertEqual(PMATCHINFO_SUBPANEL_BASE_CLASS, "PMatchInfoSubPanelBase")
        self.assertEqual(PMATCHINFO_SUBPANEL_BASE_TYPE_DESCRIPTOR_VA, 0x81D078)
        self.assertEqual(PMATCHINFO_SUBPANEL_BASE_VFTABLE_VA, 0x7C42B8)
        self.assertEqual(PMATCHINFO_SUBPANEL_BASE_COL_VA, 0x7E4C08)
        self.assertEqual(PMATCHINFO_SUBPANEL_CLASS, "PMatchInfoSubPanel")
        self.assertEqual(PMATCHINFO_SUBPANEL_TYPE_DESCRIPTOR_VA, 0x81D0A0)
        self.assertEqual(PMATCHINFO_SUBPANEL_VFTABLE_VA, 0x7C426C)
        self.assertEqual(PMATCHINFO_SUBPANEL_COL_VA, 0x7E4BD0)

    def test_every_resource_has_canonical_sha_and_positive_source_size(self):
        for resource in PMATCHINFO_RESOURCES:
            with self.subTest(name=resource.name):
                self.assertEqual(len(resource.sha256), 64)
                self.assertTrue(all(c in "0123456789abcdef" for c in resource.sha256))
                self.assertGreater(resource.byte_size, 0)
                self.assertGreater(resource.size[0], 0)
                self.assertGreater(resource.size[1], 0)

    def test_resource_validator_fails_closed_on_synthetic_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for resource in PMATCHINFO_RESOURCES:
                path = root / resource.source_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"x" * resource.byte_size)
            with self.assertRaisesRegex(
                OriginalPMatchInfoResourceError,
                "checksum mismatch",
            ):
                validate_original_pmatchinfo_resources(root)

    def test_pmatchinfo_identity_guard_uses_populated_fixture_contract(self):
        assert_pmatchinfo_identity_contract()


if __name__ == "__main__":
    unittest.main()
