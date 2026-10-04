"""Tests for source-closed direct FastView header text."""
from hashlib import sha256
from pathlib import Path
import unittest

from ea_language_strings import parse_language_pair
from gate14_fastview_direct_header_text import (
    ATTENDANCE_FIELD_OFFSET,
    ATTENDANCE_LABEL_GLOBAL_VA,
    FASTVIEW_MATCH_CONTEXT_OFFSET,
    FIRST_FINAL_FORMAT,
    FIRST_TEXT_CONSTRUCTOR_CALLSITE_VA,
    FIRST_TEXT_RECT,
    FRIENDLY_LABEL_GLOBAL_VA,
    LOCALIZED_HEADER_STRINGS,
    MATCH_LABEL_GLOBAL_VA,
    MATCH_RTTI_TYPES,
    MATCH_STADIUM_CLUB_ID_HELPER_VA,
    MATCH_STADIUM_DISPLAY_GETTER_VA,
    MATCH_TODAY_AT_GLOBAL_VA,
    MATCH_TODAY_AT_LABEL,
    MATCH_TYPE_FIELD_OFFSET,
    NESTED_DISPLAY_GETTER_VA,
    NESTED_DISPLAY_OBJECT_GETTER_VA,
    NESTED_DISPLAY_OBJECT_OFFSET,
    ORIGINAL_STADIUM_STRINGS,
    DBR_ACCESS_CLUB_LOADER_VA,
    DBR_ACCESS_CLUB_STADIUM_NAME_OFFSET,
    DBR_ACCESS_CLUB_STADIUM_STRING_READ_CALLSITE_VA,
    DBT_CLUBS_GLOBAL_VA,
    DBT_CLUBS_VTABLE_VA,
    PERSON_ABBREVIATE_FORMAT,
    PERSON_ABBREVIATE_HELPER_VA,
    PERSON_BUILD_HELPER_VA,
    PERSON_FULL_NAME_FORMAT,
    REFEREE_LABEL_GLOBAL_VA,
    SECOND_FINAL_FORMAT,
    SECOND_TEXT_CONSTRUCTOR_CALLSITE_VA,
    SECOND_TEXT_RECT,
    TEXT_FONT_OBJECT_GLOBAL_VA,
    TEXT_FONT_PATH,
    TEXT_FONT_SOURCE_ARCHIVE_SHA256,
    TEXT_FONT_SOURCE_SHA256,
    TEXT_FONT_SOURCE_SIZE,
    TEXT_NATIVE_COLOR_16,
    TEXT_RAW_FLAGS,
    TEXT_RENDER_FLAGS,
    TEXT_STYLE_INDEX,
    TEXT_STYLE_WRAPPER_VA,
    direct_header_text_contract,
)
from gate14_fastview_phase_text import (
    CANONICAL_ENGLISH_IDX_SHA256,
    CANONICAL_ENGLISH_IDX_SIZE,
    CANONICAL_ENGLISH_STR_SHA256,
    CANONICAL_ENGLISH_STR_SIZE,
    language_entry_for_global,
)


class FastViewDirectHeaderTextTests(unittest.TestCase):
    def test_two_outer_controls_have_exact_geometry_and_text_style(self):
        self.assertEqual(FIRST_TEXT_CONSTRUCTOR_CALLSITE_VA, 0x520A16)
        self.assertEqual(SECOND_TEXT_CONSTRUCTOR_CALLSITE_VA, 0x520A69)
        self.assertEqual(FIRST_TEXT_RECT, (250, 45, 550, 75))
        self.assertEqual(SECOND_TEXT_RECT, (250, 70, 550, 86))
        self.assertEqual(TEXT_STYLE_INDEX, 3)
        self.assertEqual(TEXT_STYLE_WRAPPER_VA, 0x87BE30)
        self.assertEqual(TEXT_FONT_OBJECT_GLOBAL_VA, 0x8CAB80)
        self.assertEqual(TEXT_FONT_PATH, r"Fonts\Zurich_XCn_BT_18pixel.fnt")
        self.assertEqual(TEXT_NATIVE_COLOR_16, 0xFFFF)
        self.assertEqual(TEXT_RAW_FLAGS, 0x24)
        self.assertEqual(TEXT_RENDER_FLAGS, 0x2C)

    def test_localization_globals_replay_exact_original_english_strings(self):
        root = Path(__file__).resolve().parent.parent / "original_assets" / "source"
        idx_bytes = (root / "English.idx").read_bytes()
        str_bytes = (root / "English.str").read_bytes()
        self.assertEqual(len(idx_bytes), CANONICAL_ENGLISH_IDX_SIZE)
        self.assertEqual(len(str_bytes), CANONICAL_ENGLISH_STR_SIZE)
        self.assertEqual(sha256(idx_bytes).hexdigest(), CANONICAL_ENGLISH_IDX_SHA256)
        self.assertEqual(sha256(str_bytes).hexdigest(), CANONICAL_ENGLISH_STR_SHA256)
        strings, index = parse_language_pair(str_bytes, idx_bytes)

        expected = {
            MATCH_LABEL_GLOBAL_VA: "%s MATCH",
            REFEREE_LABEL_GLOBAL_VA: "Referee",
            ATTENDANCE_LABEL_GLOBAL_VA: "Attendance",
            FRIENDLY_LABEL_GLOBAL_VA: "Friendly",
        }
        for item in LOCALIZED_HEADER_STRINGS:
            with self.subTest(global_va=hex(item.global_va)):
                self.assertEqual(item.text, expected[item.global_va])
                self.assertEqual(index.string_ids[item.english_idx_entry], item.english_string_id)
                self.assertEqual(index.resolve(strings, item.english_idx_entry), item.text)

    def test_first_line_source_shape_is_match_type_referee_and_abbreviated_name(self):
        self.assertEqual(FIRST_FINAL_FORMAT, "%s MATCH  -  %s %s")
        self.assertEqual(PERSON_FULL_NAME_FORMAT, "%s %s")
        self.assertEqual(PERSON_ABBREVIATE_FORMAT, "%c. %s")
        self.assertEqual(PERSON_BUILD_HELPER_VA, 0x6310B0)
        self.assertEqual(PERSON_ABBREVIATE_HELPER_VA, 0x51F430)
        self.assertEqual(MATCH_TYPE_FIELD_OFFSET, 0xD20)

    def test_second_line_source_closes_stadium_display_name_and_attendance(self):
        self.assertEqual(SECOND_FINAL_FORMAT, "%s  -  %s %u")
        self.assertEqual(NESTED_DISPLAY_OBJECT_OFFSET, 0xFE8)
        self.assertEqual(NESTED_DISPLAY_OBJECT_GETTER_VA, 0x62AC80)
        self.assertEqual(NESTED_DISPLAY_GETTER_VA, 0x514270)
        self.assertEqual(MATCH_STADIUM_CLUB_ID_HELPER_VA, 0x514220)
        self.assertEqual(MATCH_STADIUM_DISPLAY_GETTER_VA, 0x514270)
        self.assertEqual(DBT_CLUBS_GLOBAL_VA, 0x874B9C)
        self.assertEqual(DBT_CLUBS_VTABLE_VA, 0x7BD718)
        self.assertEqual(DBR_ACCESS_CLUB_LOADER_VA, 0x4022D0)
        self.assertEqual(DBR_ACCESS_CLUB_STADIUM_NAME_OFFSET, 0x28)
        self.assertEqual(DBR_ACCESS_CLUB_STADIUM_STRING_READ_CALLSITE_VA, 0x402364)
        self.assertEqual(
            MATCH_RTTI_TYPES,
            ("Match", "LeagueMatch", "CupMatch", "FriendlyMatch",
             "CupMatchReplay", "SecondLegMatch"),
        )
        self.assertEqual(ATTENDANCE_FIELD_OFFSET, 0xD84)
        self.assertEqual(FASTVIEW_MATCH_CONTEXT_OFFSET, 0x2A8)

        contract = direct_header_text_contract()
        self.assertTrue(contract["attendance_numeric_source_closed"])
        self.assertTrue(contract["second_line_leading_value_semantics_recovered"])
        self.assertEqual(contract["second_line_leading_value_semantics"], "stadium_display_name")

    def test_original_language_data_confirms_club_record_stadium_field(self):
        root = Path(__file__).resolve().parent.parent / "original_assets" / "source"
        strings, index = parse_language_pair(
            (root / "English.str").read_bytes(),
            (root / "English.idx").read_bytes(),
        )
        self.assertEqual(
            index.resolve(strings, MATCH_TODAY_AT_LABEL[1]),
            MATCH_TODAY_AT_LABEL[0],
        )
        self.assertEqual(
            language_entry_for_global(MATCH_TODAY_AT_GLOBAL_VA),
            MATCH_TODAY_AT_LABEL[1],
        )
        for string_id, expected in ORIGINAL_STADIUM_STRINGS.items():
            with self.subTest(string_id=string_id):
                self.assertEqual(strings[string_id], expected)

    def test_contract_keeps_pixels_and_gate_fail_closed(self):
        contract = direct_header_text_contract()
        self.assertTrue(contract["referee_display_name_source_closed"])
        self.assertTrue(contract["match_type_source_closed"])
        self.assertTrue(contract["font_bytes_source_verified"])
        self.assertEqual(contract["font_source_size"], TEXT_FONT_SOURCE_SIZE)
        self.assertEqual(contract["font_source_sha256"], TEXT_FONT_SOURCE_SHA256)
        self.assertEqual(
            contract["font_source_archive_sha256"], TEXT_FONT_SOURCE_ARCHIVE_SHA256
        )
        self.assertEqual(TEXT_FONT_SOURCE_SIZE, 79_734)
        self.assertEqual(
            TEXT_FONT_SOURCE_SHA256,
            "968936a5f5e42c4dd321f0a1096a8668c8f9ca3bd0b86243b585190969c1b71a",
        )
        self.assertEqual(
            TEXT_FONT_SOURCE_ARCHIVE_SHA256,
            "677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4",
        )
        self.assertFalse(contract["font_bytes_provenance_staged"])
        self.assertFalse(contract["header_pixels_rasterized"])
        self.assertFalse(contract["complete_fastview_frame_recovered"])
        self.assertFalse(contract["gate14_complete"])


if __name__ == "__main__":
    unittest.main()
