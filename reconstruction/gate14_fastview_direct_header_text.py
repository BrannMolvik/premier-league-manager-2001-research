"""Source-closed direct FastView header TextControl contract.

The outer FastViewPanel constructor creates two direct TextControls immediately
after PossessionFigures and before the FastViewScores wrapper. Their runtime
string semantics are now source-closed. Pixels remain fail-closed because the
exact source font bytes have been verified but are not yet provenance-staged in
the repository.
"""
from __future__ import annotations

from dataclasses import dataclass

from gate14_fastview_phase_text import language_entry_for_global


class FastViewDirectHeaderTextError(ValueError):
    pass


FASTVIEW_PANEL_CONSTRUCTOR_VA = 0x51F490
FASTVIEW_PANEL_SOLE_CALLSITE_VA = 0x53321A
FASTVIEW_MATCH_CONTEXT_OFFSET = 0x2A8

FIRST_TEXT_CONSTRUCTOR_CALLSITE_VA = 0x520A16
SECOND_TEXT_CONSTRUCTOR_CALLSITE_VA = 0x520A69
GENERIC_TEXT_CONSTRUCTOR_VA = 0x527960

FIRST_TEXT_RECT = (250, 45, 550, 75)
SECOND_TEXT_RECT = (250, 70, 550, 86)
TEXT_STYLE_INDEX = 3
TEXT_STYLE_WRAPPER_VA = 0x87BE30
TEXT_FONT_OBJECT_GLOBAL_VA = 0x8CAB80
TEXT_FONT_PATH_BUILD_CALLSITE_VA = 0x6044AC
TEXT_FONT_LOADER_CALLSITE_VA = 0x6044F9
TEXT_FONT_PATH_VA = 0x839E30
TEXT_FONT_PATH = r"Fonts\Zurich_XCn_BT_16pixel.fnt"
TEXT_FONT_SOURCE_SIZE = 75_217
TEXT_FONT_SOURCE_SHA256 = "e0fbe91421642a489721ab167ce3d2db1738802ef0f1e198df3c90ce25ec3d18"
TEXT_FONT_SOURCE_ARCHIVE_SHA256 = "677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4"
TEXT_NATIVE_COLOR_16 = 0xFFFF
TEXT_RAW_FLAGS = 0x24
TEXT_TOP_ALIGNMENT_FALLBACK_FLAG = 0x08
TEXT_RENDER_FLAGS = TEXT_RAW_FLAGS | TEXT_TOP_ALIGNMENT_FALLBACK_FLAG
TEXT_HORIZONTAL_ALIGNMENT = "center"
TEXT_VERTICAL_ALIGNMENT = "center"

MATCH_LABEL_GLOBAL_VA = 0x981EE4
REFEREE_LABEL_GLOBAL_VA = 0x982354
ATTENDANCE_LABEL_GLOBAL_VA = 0x982C40
FRIENDLY_LABEL_GLOBAL_VA = 0x9830C8
MATCH_TODAY_AT_GLOBAL_VA = 0x982050

MATCH_LABEL = ("%s MATCH", 2629, 21783)
REFEREE_LABEL = ("Referee", 2345, 21542)
ATTENDANCE_LABEL = ("Attendance", 1774, 20308)
FRIENDLY_LABEL = ("Friendly", 1484, 20885)
MATCH_TODAY_AT_LABEL = ("%s MATCH TODAY AT %s", 2538, 21705)

MATCH_TYPE_FIELD_OFFSET = 0xD20
ATTENDANCE_FIELD_OFFSET = 0xD84
NESTED_DISPLAY_OBJECT_OFFSET = 0xFE8
PERSON_FIRST_INDEX_OFFSET = 0xFE0
PERSON_SECOND_INDEX_OFFSET = 0xFE4

PERSON_FULL_NAME_FORMAT_VA = 0x81858C
PERSON_FULL_NAME_FORMAT = "%s %s"
PERSON_ABBREVIATE_HELPER_VA = 0x51F430
PERSON_ABBREVIATE_FORMAT_VA = 0x818EB0
PERSON_ABBREVIATE_FORMAT = "%c. %s"
PERSON_BUILD_HELPER_VA = 0x6310B0

MATCH_TEMPLATE_SUFFIX_VA = 0x829708
MATCH_TEMPLATE_SUFFIX = "  -  %s %s"
FIRST_FINAL_FORMAT = "%s MATCH  -  %s %s"

SECOND_FINAL_FORMAT_VA = 0x8296F8
SECOND_FINAL_FORMAT = "%s  -  %s %u"
NESTED_DISPLAY_GETTER_VA = 0x514270
NESTED_DISPLAY_OBJECT_GETTER_VA = 0x62AC80

MATCH_STADIUM_CLUB_ID_HELPER_VA = 0x514220
MATCH_STADIUM_DISPLAY_GETTER_VA = 0x514270
DBT_CLUBS_GLOBAL_VA = 0x874B9C
DBT_CLUBS_VTABLE_VA = 0x7BD718
DBR_ACCESS_CLUB_LOADER_VA = 0x4022D0
DBR_ACCESS_CLUB_STADIUM_NAME_OFFSET = 0x28
DBR_ACCESS_CLUB_STADIUM_STRING_READ_CALLSITE_VA = 0x402364
MATCH_RTTI_TYPES = (
    "Match",
    "LeagueMatch",
    "CupMatch",
    "FriendlyMatch",
    "CupMatchReplay",
    "SecondLegMatch",
)
ORIGINAL_STADIUM_STRINGS = {
    919: "Highbury",
    975: "Stamford Bridge",
    1031: "Anfield",
    1059: "Old Trafford",
}

MATCH_TYPE_LOOKUP_CONSTRUCTOR_VA = 0x4056D0
MATCH_TYPE_LOOKUP_STAGE2_VA = 0x4F3B10
MATCH_TYPE_DISPLAY_GETTER_VA = 0x49AB40


@dataclass(frozen=True)
class LocalizedHeaderString:
    global_va: int
    english_idx_entry: int
    english_string_id: int
    text: str

    def __post_init__(self) -> None:
        if language_entry_for_global(self.global_va) != self.english_idx_entry:
            raise FastViewDirectHeaderTextError(
                "header localization global/index mapping drifted"
            )
        if type(self.english_string_id) is not int or self.english_string_id < 0:
            raise FastViewDirectHeaderTextError("header STR id must be non-negative")
        if not isinstance(self.text, str) or not self.text:
            raise FastViewDirectHeaderTextError("header text must be non-empty")


LOCALIZED_HEADER_STRINGS = (
    LocalizedHeaderString(MATCH_LABEL_GLOBAL_VA, MATCH_LABEL[1], MATCH_LABEL[2], MATCH_LABEL[0]),
    LocalizedHeaderString(REFEREE_LABEL_GLOBAL_VA, REFEREE_LABEL[1], REFEREE_LABEL[2], REFEREE_LABEL[0]),
    LocalizedHeaderString(ATTENDANCE_LABEL_GLOBAL_VA, ATTENDANCE_LABEL[1], ATTENDANCE_LABEL[2], ATTENDANCE_LABEL[0]),
    LocalizedHeaderString(FRIENDLY_LABEL_GLOBAL_VA, FRIENDLY_LABEL[1], FRIENDLY_LABEL[2], FRIENDLY_LABEL[0]),
)


def direct_header_text_contract() -> dict:
    return {
        "fastview_panel_constructor_va": FASTVIEW_PANEL_CONSTRUCTOR_VA,
        "fastview_panel_sole_callsite_va": FASTVIEW_PANEL_SOLE_CALLSITE_VA,
        "match_context_offset": FASTVIEW_MATCH_CONTEXT_OFFSET,
        "first_text_constructor_callsite_va": FIRST_TEXT_CONSTRUCTOR_CALLSITE_VA,
        "second_text_constructor_callsite_va": SECOND_TEXT_CONSTRUCTOR_CALLSITE_VA,
        "first_text_rect": FIRST_TEXT_RECT,
        "second_text_rect": SECOND_TEXT_RECT,
        "style_index": TEXT_STYLE_INDEX,
        "style_wrapper_va": TEXT_STYLE_WRAPPER_VA,
        "font_object_global_va": TEXT_FONT_OBJECT_GLOBAL_VA,
        "font_path_build_callsite_va": TEXT_FONT_PATH_BUILD_CALLSITE_VA,
        "font_loader_callsite_va": TEXT_FONT_LOADER_CALLSITE_VA,
        "font_path": TEXT_FONT_PATH,
        "font_source_size": TEXT_FONT_SOURCE_SIZE,
        "font_source_sha256": TEXT_FONT_SOURCE_SHA256,
        "font_source_archive_sha256": TEXT_FONT_SOURCE_ARCHIVE_SHA256,
        "native_color_16": TEXT_NATIVE_COLOR_16,
        "raw_flags": TEXT_RAW_FLAGS,
        "top_alignment_fallback_flag": TEXT_TOP_ALIGNMENT_FALLBACK_FLAG,
        "render_flags": TEXT_RENDER_FLAGS,
        "horizontal_alignment": TEXT_HORIZONTAL_ALIGNMENT,
        "vertical_alignment": TEXT_VERTICAL_ALIGNMENT,
        "first_final_format": FIRST_FINAL_FORMAT,
        "second_final_format": SECOND_FINAL_FORMAT,
        "match_type_field_offset": MATCH_TYPE_FIELD_OFFSET,
        "attendance_field_offset": ATTENDANCE_FIELD_OFFSET,
        "nested_display_object_offset": NESTED_DISPLAY_OBJECT_OFFSET,
        "person_first_index_offset": PERSON_FIRST_INDEX_OFFSET,
        "person_second_index_offset": PERSON_SECOND_INDEX_OFFSET,
        "referee_display_name_source_closed": True,
        "match_type_source_closed": True,
        "attendance_numeric_source_closed": True,
        "second_line_leading_value_semantics_recovered": True,
        "second_line_leading_value_semantics": "stadium_display_name",
        "font_bytes_source_verified": True,
        "font_bytes_provenance_staged": True,
        "header_pixels_rasterized": False,
        "complete_fastview_frame_recovered": False,
        "gate14_complete": False,
    }
