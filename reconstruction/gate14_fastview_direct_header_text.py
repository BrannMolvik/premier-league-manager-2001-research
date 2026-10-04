"""Source-closed direct FastView header TextControl contract.

The outer FastViewPanel constructor creates two direct TextControls immediately
after PossessionFigures and before the FastViewScores wrapper. Their pixels are
not rasterized here because one source font is not yet provenance-staged and
one leading runtime string still has deliberately neutral semantics.
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
TEXT_FONT_PATH_VA = 0x839E10
TEXT_FONT_PATH = r"Fonts\Zurich_XCn_BT_18pixel.fnt"
TEXT_NATIVE_COLOR_16 = 0xFFFF
TEXT_RAW_FLAGS = 0x24
TEXT_FORCED_RENDER_FLAG = 0x08
TEXT_RENDER_FLAGS = TEXT_RAW_FLAGS | TEXT_FORCED_RENDER_FLAG
TEXT_HORIZONTAL_ALIGNMENT = "center"
TEXT_VERTICAL_ALIGNMENT = "center"

MATCH_LABEL_GLOBAL_VA = 0x981EE4
REFEREE_LABEL_GLOBAL_VA = 0x982354
ATTENDANCE_LABEL_GLOBAL_VA = 0x982C40
FRIENDLY_LABEL_GLOBAL_VA = 0x9830C8

MATCH_LABEL = ("%s MATCH", 2629, 21783)
REFEREE_LABEL = ("Referee", 2345, 21542)
ATTENDANCE_LABEL = ("Attendance", 1774, 20308)
FRIENDLY_LABEL = ("Friendly", 1484, 20885)

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
        "font_path": TEXT_FONT_PATH,
        "native_color_16": TEXT_NATIVE_COLOR_16,
        "raw_flags": TEXT_RAW_FLAGS,
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
        "second_line_leading_value_semantics_recovered": False,
        "font_bytes_provenance_staged": False,
        "header_pixels_rasterized": False,
        "complete_fastview_frame_recovered": False,
        "gate14_complete": False,
    }
