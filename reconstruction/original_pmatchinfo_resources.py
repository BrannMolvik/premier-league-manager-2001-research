"""Source-backed PMatchInfo / Match_report resource inventory.

Recovery 156 correlates the canonical executable's contiguous Match_report
static-loader family with the authorized original disc. Every source file below
is byte/hash/geometry verified. Direct per-control consumer addresses are
recorded only where bounded executable code has been traced; an empty consumer
tuple is deliberately not treated as missing ownership because the static
loader family and PMatchInfo/subpanel consumers establish the resource family
without inventing a final widget placement.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_header import parse_ea444_header
from original_pmenu_chrome import (
    PMENU_FONT_NATIVE_LINE_HEIGHT,
    PMENU_FONT_SHA256,
    PMENU_FONT_SOURCE_PATH,
    PMENU_RUNTIME_FONT_GLOBAL_VA,
)
from original_league_fixtures_resources import (
    LEAGUE_FIXTURES_MATCH_INFO_CLASS,
    LEAGUE_FIXTURES_MATCH_INFO_CONSTRUCTOR_VA,
    LEAGUE_FIXTURES_MATCH_INFO_TYPE_DESCRIPTOR_VA,
    LEAGUE_FIXTURES_MATCH_INFO_VFTABLE_VA,
)


class OriginalPMatchInfoResourceError(ValueError):
    pass


PMATCHINFO_SUBPANEL_BASE_CLASS = "PMatchInfoSubPanelBase"
PMATCHINFO_SUBPANEL_BASE_TYPE_DESCRIPTOR_VA = 0x81D078
PMATCHINFO_SUBPANEL_BASE_VFTABLE_VA = 0x7C42B8
PMATCHINFO_SUBPANEL_BASE_COL_VA = 0x7E4C08

PMATCHINFO_SUBPANEL_CLASS = "PMatchInfoSubPanel"
PMATCHINFO_SUBPANEL_TYPE_DESCRIPTOR_VA = 0x81D0A0
PMATCHINFO_SUBPANEL_VFTABLE_VA = 0x7C426C
PMATCHINFO_SUBPANEL_COL_VA = 0x7E4BD0


PMATCHINFO_BITMAP_DESCRIPTOR_SETUP_VA = 0x64E500
PMATCHINFO_CONTROL_RECT_SETUP_VA = 0x64F380

# The fifth argument to 0x64F380 is stored at control+0x28 and receives a
# virtual callback with the control. Fresh RTTI proves the concrete global
# passed by these PMatchInfo setup paths is eCDBitmap, not a text/font object.
# Keep its role neutral rather than inventing a modern widget-owner label.
PMATCHINFO_CONTROL_CALLBACK_TARGET_VA = 0x87BF00
PMATCHINFO_CONTROL_CALLBACK_TARGET_CLASS = "eCDBitmap"
PMATCHINFO_CONTROL_CALLBACK_TARGET_TYPE_DESCRIPTOR_VA = 0x819C48
PMATCHINFO_CONTROL_CALLBACK_TARGET_COL_VA = 0x7E1248
PMATCHINFO_CONTROL_CALLBACK_TARGET_VFTABLE_VA = 0x7BFE14


PMATCHINFO_TEXT_SETUP_VA = 0x6503F0
PMATCHINFO_TEXT_FONT_GLOBAL_VA = PMENU_RUNTIME_FONT_GLOBAL_VA
PMATCHINFO_TEXT_FONT_SOURCE_PATH = PMENU_FONT_SOURCE_PATH
PMATCHINFO_TEXT_FONT_SHA256 = PMENU_FONT_SHA256
PMATCHINFO_TEXT_FONT_NATIVE_LINE_HEIGHT = PMENU_FONT_NATIVE_LINE_HEIGHT


@dataclass(frozen=True)
class OriginalPMatchInfoTextPlacement:
    owner_method_va: int
    setup_call_va: int
    x: int
    y: int
    width: int
    height: int
    font_global_va: int = PMATCHINFO_TEXT_FONT_GLOBAL_VA

    @property
    def rect(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.width, self.height)


PMATCHINFO_SCRIPT_ROW1_CLASS = "PScriptRow1"
PMATCHINFO_SCRIPT_ROW1_TYPE_DESCRIPTOR_VA = 0x81CEE8
PMATCHINFO_SCRIPT_ROW1_COL_VA = 0x7E4890
PMATCHINFO_SCRIPT_ROW1_VFTABLE_VA = 0x7C3F34
PMATCHINFO_SCRIPT_ROW1_SETUP_VA = 0x483500
PMATCHINFO_SCRIPT_ROW1_UPDATE_VA = 0x4858E0

PMATCHINFO_SCRIPT_ROW2_CLASS = "PScriptRow2"
PMATCHINFO_SCRIPT_ROW2_TYPE_DESCRIPTOR_VA = 0x81CF08
PMATCHINFO_SCRIPT_ROW2_COL_VA = 0x7E48E0
PMATCHINFO_SCRIPT_ROW2_VFTABLE_VA = 0x7C3F88
PMATCHINFO_SCRIPT_ROW2_SETUP_VA = 0x483500
PMATCHINFO_SCRIPT_ROW2_UPDATE_VA = 0x485F50

PMATCHINFO_DYNAMIC_INCIDENT_CONTROL_OFFSET = 0x1C8
PMATCHINFO_DYNAMIC_INCIDENT_RESOURCE_SLOT_OFFSET = 0x1F4
PMATCHINFO_DYNAMIC_INCIDENT_RECT = (191, 11, 14, 14)
PMATCHINFO_DYNAMIC_INCIDENT_RESOURCE_NAMES = (
    "score",
    "injured",
    "yellow_card",
    "red_card",
    "red_card_single",
    "sub_on",
    "sub_off",
)


@dataclass(frozen=True)
class OriginalPMatchInfoLanguageBinding:
    global_va: int
    english_index: int
    original_text: str


# The complete English.idx loader at 0x635F30..0x64C7D4 has exactly 2,714
# assignments, one per English.idx entry. These are the exact globals consumed
# by the PMatchInfo text producer paths bounded below.
PMATCHINFO_ENGLISH_LOADER_START_VA = 0x635F30
PMATCHINFO_ENGLISH_LOADER_END_VA = 0x64C7D4
PMATCHINFO_ENGLISH_LOADER_ENTRY_COUNT = 2714
PMATCHINFO_LANGUAGE_BINDINGS = (
    OriginalPMatchInfoLanguageBinding(0x982BA4, 1813, "O.G."),
    OriginalPMatchInfoLanguageBinding(0x982BA0, 1814, "(%d-%d pen)"),
    OriginalPMatchInfoLanguageBinding(0x9826B8, 2128, "Mom"),
    OriginalPMatchInfoLanguageBinding(0x9822E4, 2373, "Sent off"),
    OriginalPMatchInfoLanguageBinding(0x982164, 2469, "Goal"),
    OriginalPMatchInfoLanguageBinding(0x982160, 2470, "Sub Off"),
    OriginalPMatchInfoLanguageBinding(0x98215C, 2471, "Sub On"),
    OriginalPMatchInfoLanguageBinding(0x982158, 2472, "Booking"),
    OriginalPMatchInfoLanguageBinding(0x982154, 2473, "Injury"),
    OriginalPMatchInfoLanguageBinding(0x982100, 2494, "Shoot Out"),
    OriginalPMatchInfoLanguageBinding(0x98200C, 2555, "Ref."),
    OriginalPMatchInfoLanguageBinding(0x982008, 2556, "FINANCIAL"),
    OriginalPMatchInfoLanguageBinding(0x981EA4, 2645, "%s: %s %s"),
    OriginalPMatchInfoLanguageBinding(0x981E98, 2648, "first leg"),
    OriginalPMatchInfoLanguageBinding(0x981E94, 2649, "second leg"),
    OriginalPMatchInfoLanguageBinding(0x982C40, 1774, "Attendance"),
    OriginalPMatchInfoLanguageBinding(0x982C3C, 1775, "TEAM INFO"),
    OriginalPMatchInfoLanguageBinding(0x982C38, 1776, "MATCH INFO"),
)
PMATCHINFO_LANGUAGE_BY_GLOBAL = {
    binding.global_va: binding for binding in PMATCHINFO_LANGUAGE_BINDINGS
}


def pmatchinfo_original_english(global_va: int) -> str:
    if type(global_va) is not int:
        raise OriginalPMatchInfoResourceError(
            "PMatchInfo language global must be an integer address"
        )
    try:
        return PMATCHINFO_LANGUAGE_BY_GLOBAL[global_va].original_text
    except KeyError as exc:
        raise OriginalPMatchInfoResourceError(
            f"Unbound PMatchInfo English global: {global_va:#x}"
        ) from exc


PMATCHINFO_CONTROL_EVENT_BIND_VA = 0x64F3C0
PMATCHINFO_TAB_EVENT_HANDLER_VA = 0x488B70
PMATCHINFO_KEY_EVENT_HANDLER_VA = 0x488C60

PMATCHINFO_TAB_CONTROL_CLASS = "fmRadioButton6"
PMATCHINFO_TAB_CONTROL_TYPE_DESCRIPTOR_VA = 0x81D108
PMATCHINFO_TAB_CONTROL_COL_VA = 0x7E4D10
PMATCHINFO_TAB_CONTROL_VFTABLE_VA = 0x7C4474
PMATCHINFO_TAB_CONTROL_CONSTRUCTOR_VA = 0x488570
PMATCHINFO_TAB_CONTROL_COUNT = 3
PMATCHINFO_TAB_CONTROL_STRIDE = 0x54

PMATCHINFO_TEAM_INFO_SUBPANEL_CLASS = "PTeamInfoSubPanel"
PMATCHINFO_TEAM_INFO_SUBPANEL_TYPE_DESCRIPTOR_VA = 0x81D038
PMATCHINFO_TEAM_INFO_SUBPANEL_COL_VA = 0x7E4B10
PMATCHINFO_TEAM_INFO_SUBPANEL_VFTABLE_VA = 0x7C4220

PMATCHINFO_FINANCE_SUBPANEL_CLASS = "PFinanceSubPanel"
PMATCHINFO_FINANCE_SUBPANEL_TYPE_DESCRIPTOR_VA = 0x81D1E8
PMATCHINFO_FINANCE_SUBPANEL_COL_VA = 0x7E4D60
PMATCHINFO_FINANCE_SUBPANEL_VFTABLE_VA = 0x7C4530
PMATCHINFO_FINANCE_SUBPANEL_CONSTRUCTOR_VA = 0x488DE0

PMATCHINFO_TAB_HOST_CLASS = "eCSubPanel"
PMATCHINFO_TAB_HOST_TYPE_DESCRIPTOR_VA = 0x81B780
PMATCHINFO_TAB_HOST_COL_VA = 0x7E1BF0
PMATCHINFO_TAB_HOST_VFTABLE_VA = 0x7C0668
PMATCHINFO_TAB_HOST_OFFSET = 0x17A8
PMATCHINFO_TAB_HOST_TARGET_OFFSET = 0x2C
PMATCHINFO_TAB_HOST_SETUP_VA = 0x650B20
PMATCHINFO_TAB_PANEL_RECT_SETUP_VA = 0x653320
PMATCHINFO_TAB_HOST_REFRESH_VA = 0x64F600
PMATCHINFO_DEFAULT_PANEL_POINTER_OFFSET = 0x1390
PMATCHINFO_DEFAULT_PANEL_POINTER_ASSIGN_VA = 0x4879C6

PMATCHINFO_CROSS_BUTTON_CLASS = "fmCrossButton"
PMATCHINFO_CROSS_BUTTON_TYPE_DESCRIPTOR_VA = 0x81BBD8
PMATCHINFO_CROSS_BUTTON_COL_VA = 0x7E2358
PMATCHINFO_CROSS_BUTTON_VFTABLE_VA = 0x7C0DA0
PMATCHINFO_CROSS_BUTTON_OFFSET = 0x17D8
PMATCHINFO_EXIT_EVENT_ID = 7
PMATCHINFO_ESCAPE_CODE = 0x1B
PMATCHINFO_EVENT_CODE_OFFSET = 0x20
PMATCHINFO_EVENT_OWNER_OFFSET = 0x24
PMATCHINFO_EXIT_MESSAGE_HELPER_VA = 0x6539F0
PMATCHINFO_POST_MESSAGE_WRAPPER_VA = 0x659650
PMATCHINFO_EXIT_MESSAGE_ID = 0x400
PMATCHINFO_EXIT_MESSAGE_WPARAM = 7
PMATCHINFO_EXIT_MESSAGE_LPARAM = 0
PMATCHINFO_POST_MESSAGE_API = "PostMessageA"


@dataclass(frozen=True)
class OriginalPMatchInfoTab:
    event_id: int
    control_offset: int
    label_global_va: int
    label: str
    panel_offset: int
    panel_class: str
    panel_type_descriptor_va: int
    panel_col_va: int
    panel_vftable_va: int


PMATCHINFO_TABS = (
    OriginalPMatchInfoTab(
        1,
        0x14A4,
        0x982C38,
        "MATCH INFO",
        0x1C0,
        PMATCHINFO_SUBPANEL_CLASS,
        PMATCHINFO_SUBPANEL_TYPE_DESCRIPTOR_VA,
        PMATCHINFO_SUBPANEL_COL_VA,
        PMATCHINFO_SUBPANEL_VFTABLE_VA,
    ),
    OriginalPMatchInfoTab(
        2,
        0x14F8,
        0x982C3C,
        "TEAM INFO",
        0x8F0,
        PMATCHINFO_TEAM_INFO_SUBPANEL_CLASS,
        PMATCHINFO_TEAM_INFO_SUBPANEL_TYPE_DESCRIPTOR_VA,
        PMATCHINFO_TEAM_INFO_SUBPANEL_COL_VA,
        PMATCHINFO_TEAM_INFO_SUBPANEL_VFTABLE_VA,
    ),
    OriginalPMatchInfoTab(
        3,
        0x154C,
        0x982008,
        "FINANCIAL",
        0xB10,
        PMATCHINFO_FINANCE_SUBPANEL_CLASS,
        PMATCHINFO_FINANCE_SUBPANEL_TYPE_DESCRIPTOR_VA,
        PMATCHINFO_FINANCE_SUBPANEL_COL_VA,
        PMATCHINFO_FINANCE_SUBPANEL_VFTABLE_VA,
    ),
)

PMATCHINFO_DEFAULT_TAB_EVENT_ID = 1
PMATCHINFO_DEFAULT_PANEL_OFFSET = 0x1C0
PMATCHINFO_TAB_PANEL_STATE_VALUE = 2
PMATCHINFO_TAB_PANEL_STATE_OFFSET = 0x04
PMATCHINFO_TAB_PANEL_HOST_POINTER_OFFSET = 0x08


def pmatchinfo_tab_for_event(event_id: int) -> OriginalPMatchInfoTab:
    if type(event_id) is not int:
        raise OriginalPMatchInfoResourceError(
            "PMatchInfo tab event id must be an integer"
        )
    for tab in PMATCHINFO_TABS:
        if tab.event_id == event_id:
            return tab
    raise OriginalPMatchInfoResourceError(
        f"Unbound PMatchInfo tab event id: {event_id}"
    )


def pmatchinfo_tab_for_control_offset(control_offset: int) -> OriginalPMatchInfoTab:
    if type(control_offset) is not int:
        raise OriginalPMatchInfoResourceError(
            "PMatchInfo tab control offset must be an integer"
        )
    for tab in PMATCHINFO_TABS:
        if tab.control_offset == control_offset:
            return tab
    raise OriginalPMatchInfoResourceError(
        f"Unbound PMatchInfo tab control offset: {control_offset:#x}"
    )


# PScriptRow1/2 share these two text controls. The first control receives an
# incident/event description buffer; the second receives a decimal rendering
# of event_record+0x00. The higher-level meaning of event_record+0x00 remains
# deliberately neutral.
PMATCHINFO_SCRIPT_EVENT_LABEL_CONTROL_OFFSET = 0x1F8
PMATCHINFO_SCRIPT_EVENT_LABEL_TEXT_POINTER_OFFSET = 0x224
PMATCHINFO_SCRIPT_EVENT_LABEL_BUFFER_OFFSET = 0xA0
PMATCHINFO_SCRIPT_EVENT_DECIMAL_CONTROL_OFFSET = 0x238
PMATCHINFO_SCRIPT_EVENT_DECIMAL_TEXT_POINTER_OFFSET = 0x264
PMATCHINFO_SCRIPT_EVENT_DECIMAL_BUFFER_OFFSET = 0x80
PMATCHINFO_SCRIPT_EVENT_DECIMAL_SOURCE_OFFSET = 0x00
PMATCHINFO_SCRIPT_EVENT_DECIMAL_FORMAT_VA = 0x81B1A8
PMATCHINFO_SCRIPT_EVENT_DECIMAL_FORMAT = "%d"
PMATCHINFO_SCRIPT_ROW1_LABEL_ASSIGN_VA = 0x485AE6
PMATCHINFO_SCRIPT_ROW1_DECIMAL_ASSIGN_VA = 0x485AEC
PMATCHINFO_SCRIPT_ROW2_LABEL_ASSIGN_VA = 0x486156
PMATCHINFO_SCRIPT_ROW2_DECIMAL_ASSIGN_VA = 0x48615C
PMATCHINFO_SCRIPT_EMPTY_BUFFER_VA = 0x874BA0

# Source byte table used by the event-type dispatch. Types 0..4 take the first
# family, type 5 the second, types 6..9 the no-incident family, and type 10 the
# substitution family.
PMATCHINFO_SCRIPT_EVENT_TYPE_CLASS_BYTES = (0, 0, 0, 0, 0, 1, 3, 3, 3, 3, 2)
PMATCHINFO_SCRIPT_ROW1_EVENT_CLASS_TARGETS = (
    0x48597B,
    0x4859E4,
    0x485A68,
    0x485AA8,
)


@dataclass(frozen=True)
class OriginalPMatchInfoIncidentSelection:
    label_global_va: int
    label: str
    resource_name: str


def _pmatchinfo_incident(
    label_global_va: int,
    resource_name: str,
) -> OriginalPMatchInfoIncidentSelection:
    if resource_name not in PMATCHINFO_DYNAMIC_INCIDENT_RESOURCE_NAMES:
        raise OriginalPMatchInfoResourceError(
            f"Unbound PMatchInfo dynamic incident resource: {resource_name}"
        )
    return OriginalPMatchInfoIncidentSelection(
        label_global_va,
        pmatchinfo_original_english(label_global_va),
        resource_name,
    )


def pmatchinfo_script_incident_selection(
    event_type: int,
    *,
    row_field_74: int = 0,
    row_field_78: int = 0,
    event_field_20: int = 0,
    event_field_18: int = 0,
    event_field_1c: int = 0,
) -> OriginalPMatchInfoIncidentSelection | None:
    """Mirror the bounded PScriptRow1/2 incident label/resource predicates.

    Field names intentionally preserve source offsets instead of assigning
    unproven gameplay semantics to the backing flags.
    """
    values = (
        event_type,
        row_field_74,
        row_field_78,
        event_field_20,
        event_field_18,
        event_field_1c,
    )
    if any(type(value) is not int for value in values):
        raise OriginalPMatchInfoResourceError(
            "PMatchInfo incident selector requires integer source fields"
        )
    if event_type < 0:
        raise OriginalPMatchInfoResourceError(
            "PMatchInfo incident event type cannot be negative"
        )
    if event_type > 10:
        return None

    family = PMATCHINFO_SCRIPT_EVENT_TYPE_CLASS_BYTES[event_type]
    if family == 0:
        if row_field_74:
            return _pmatchinfo_incident(0x982BA4, "score")
        if row_field_78:
            return _pmatchinfo_incident(0x982100, "score")
        return _pmatchinfo_incident(0x982164, "score")

    if family == 1:
        if event_field_20:
            return _pmatchinfo_incident(0x982154, "injured")
        if event_field_18:
            return _pmatchinfo_incident(0x982158, "yellow_card")
        if event_field_1c:
            return _pmatchinfo_incident(
                0x9822E4,
                "red_card" if row_field_74 else "red_card_single",
            )
        return None

    if family == 2:
        if row_field_74:
            return _pmatchinfo_incident(0x98215C, "sub_on")
        return _pmatchinfo_incident(0x982160, "sub_off")

    return None


# The 29x16 player-strip text call resolves a DBTPositions entry instead of an
# English-loader string. The source chain keeps the surrounding player/context
# table neutral but RTTI-proves the selected 20-byte table as DBTPositions.
PMATCHINFO_PLAYER_TEXT_SETUP_CALL_VA = 0x483918
PMATCHINFO_PLAYER_TEXT_CONTROL_OFFSET = 0xB0
PMATCHINFO_PLAYER_CONTEXT_INDEX_OFFSET = 0x70
PMATCHINFO_PLAYER_CONTEXT_TABLE_VA = 0x875640
PMATCHINFO_PLAYER_CONTEXT_RECORD_SIZE = 0x250
PMATCHINFO_PLAYER_POSITION_CONTEXT_OFFSET = 0x248
PMATCHINFO_POSITION_SELECTOR_VA = 0x4EA3C0
PMATCHINFO_POSITION_SELECTOR_BYTE_OFFSET = 0x03
PMATCHINFO_POSITION_SELECTOR_MASK = 0x1F
PMATCHINFO_POSITIONS_CLASS = "DBTPositions"
PMATCHINFO_POSITIONS_OBJECT_VA = 0x874B60
PMATCHINFO_POSITIONS_RECORD_BASE_VA = 0x874B68
PMATCHINFO_POSITIONS_VFTABLE_VA = 0x7BD394
PMATCHINFO_POSITIONS_COL_VA = 0x7DE8B8
PMATCHINFO_POSITIONS_TYPE_DESCRIPTOR_VA = 0x8182F8
PMATCHINFO_POSITIONS_RECORD_SIZE = 20
PMATCHINFO_POSITIONS_STRING_FIELD_OFFSET = 0x0C


@dataclass(frozen=True)
class OriginalPMatchInfoPopupTextProducer:
    setup_call_va: int
    control_offset: int
    text_pointer_offset: int
    buffer_offset: int
    assign_va: int
    leading_global_va: int


PMATCHINFO_POPUP_TEXT_UPDATE_VA = 0x4885A0
PMATCHINFO_POPUP_TEXT_PRODUCERS = (
    OriginalPMatchInfoPopupTextProducer(
        0x485091, 0x13E4, 0x1410, 0xB8, 0x48899A, 0x982C40
    ),
    OriginalPMatchInfoPopupTextProducer(
        0x4850C9, 0x1424, 0x1450, 0x140, 0x488A79, 0x98200C
    ),
    OriginalPMatchInfoPopupTextProducer(
        0x485101, 0x1464, 0x1490, 0x180, 0x488AD2, 0x9826B8
    ),
)

PMATCHINFO_POPUP_ATTENDANCE_VALUE_OFFSET = 0x30
PMATCHINFO_POPUP_ATTENDANCE_DECIMAL_FORMAT_VA = 0x81B1A8
PMATCHINFO_POPUP_ATTENDANCE_DECIMAL_FORMAT = "%d"
PMATCHINFO_POPUP_ATTENDANCE_GROUP_FORMAT_VA = 0x81D140
PMATCHINFO_POPUP_ATTENDANCE_GROUP_FORMAT = "%.3d"
PMATCHINFO_POPUP_ATTENDANCE_COMMA_VA = 0x81D148
PMATCHINFO_POPUP_ATTENDANCE_COMMA = ","
PMATCHINFO_POPUP_SPACE_LITERAL_VA = 0x81AF38
PMATCHINFO_POPUP_SPACE_LITERAL = " "
PMATCHINFO_POPUP_FIRST_LEG_GLOBAL_VA = 0x981E98
PMATCHINFO_POPUP_SECOND_LEG_GLOBAL_VA = 0x981E94

PMATCHINFO_POPUP_REFEREE_STRING_PRODUCER_VA = 0x60BEB0
PMATCHINFO_POPUP_PENALTY_STATE_OFFSET = 0x1C
PMATCHINFO_POPUP_PENALTY_FORMAT_GLOBAL_VA = 0x982BA0

PMATCHINFO_POPUP_MOM_INDEX_OFFSET = 0x9C
PMATCHINFO_POPUP_MOM_ABSENT_VALUE = -1
PMATCHINFO_POPUP_MOM_PLAYER_TABLE_VA = 0x875640
PMATCHINFO_POPUP_MOM_PLAYER_RECORD_SIZE = 0x250
PMATCHINFO_POPUP_MOM_PLAYER_STRING_OFFSETS = (0x08, 0x0C)
PMATCHINFO_POPUP_MOM_FORMAT_GLOBAL_VA = 0x981EA4
PMATCHINFO_POPUP_MOM_LABEL_GLOBAL_VA = 0x9826B8


PMATCHINFO_TEXT_PLACEMENTS = (
    OriginalPMatchInfoTextPlacement(0x483500, 0x4836AC, 210, 2, 185, 12),
    OriginalPMatchInfoTextPlacement(0x483500, 0x4836E4, 210, 18, 185, 12),
    OriginalPMatchInfoTextPlacement(0x483840, 0x483918, 33, 0, 29, 16),
    OriginalPMatchInfoTextPlacement(0x484F90, 0x485091, 172, 50, 416, 16),
    OriginalPMatchInfoTextPlacement(0x484F90, 0x4850C9, 380, 68, 208, 16),
    OriginalPMatchInfoTextPlacement(0x484F90, 0x485101, 172, 68, 208, 16),
)


@dataclass(frozen=True)
class OriginalPMatchInfoPlacement:
    resource_name: str
    owner_method_va: int
    resource_bind_va: int
    rect_setup_call_va: int
    x: int
    y: int
    width: int
    height: int
    callback_target_va: int | None = PMATCHINFO_CONTROL_CALLBACK_TARGET_VA

    @property
    def rect(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.width, self.height)


PMATCHINFO_RESOURCE_PLACEMENTS = (
    OriginalPMatchInfoPlacement(
        "match_name_grid", 0x483500, 0x483541, 0x483591, 0, 0, 185, 36
    ),
    OriginalPMatchInfoPlacement(
        "match_incid_grid", 0x483500, 0x4835AD, 0x4835E7, 189, 0, 142, 36
    ),
    OriginalPMatchInfoPlacement(
        "yellow_card", 0x483500, 0x48366D, 0x483674, 191, 11, 14, 14
    ),
    OriginalPMatchInfoPlacement(
        "match_name_grid", 0x483750, 0x483784, 0x4837D0, 0, 0, 185, 36
    ),
    OriginalPMatchInfoPlacement(
        "match_incid_grid", 0x483750, 0x4837EC, 0x483826, 189, 0, 142, 36
    ),
    OriginalPMatchInfoPlacement(
        "info_player", 0x483840, 0x4838AC, 0x4838B3, 0, 0, 274, 16
    ),
    OriginalPMatchInfoPlacement(
        "info_player_disabled", 0x483A30, 0x483A81, 0x483A88, 0, 0, 252, 16
    ),
    OriginalPMatchInfoPlacement(
        "pitch_normal", 0x483AA0, 0x483B1E, 0x483B72, 233, -2, 294, 78
    ),
    OriginalPMatchInfoPlacement(
        "info_popup", 0x484F90, 0x484FFF, 0x485059, 0, 0, 760, 500
    ),
)


@dataclass(frozen=True)
class OriginalPMatchInfoResource:
    name: str
    source_path: str
    sha256: str
    byte_size: int
    size: tuple[int, int]
    path_literal_va: int
    raw_handle_va: int
    wrapper_va: int
    direct_consumer_vas: tuple[int, ...] = ()
    direct_consumer_handle: str | None = None


def _r(
    name: str,
    source_path: str,
    digest: str,
    byte_size: int,
    size: tuple[int, int],
    path_literal_va: int,
    raw_handle_va: int,
    wrapper_va: int,
    direct_consumer_vas: tuple[int, ...] = (),
    direct_consumer_handle: str | None = None,
) -> OriginalPMatchInfoResource:
    return OriginalPMatchInfoResource(
        name,
        source_path,
        digest,
        byte_size,
        size,
        path_literal_va,
        raw_handle_va,
        wrapper_va,
        direct_consumer_vas,
        direct_consumer_handle,
    )


PMATCHINFO_RESOURCES = (
    _r(
        "info_player",
        "FM2001_Art/Generic/match_report/info_player.444",
        "c128d82caadb24ec932c0786e5b6b714c08f63fe1acad01c9f0ff6b459ac1033",
        4688, (274, 16), 0x837E9C, 0x943570, 0x943550, (0x4838AC,), "wrapper",
    ),
    _r(
        "info_player_disabled",
        "FM2001_Art/Generic/match_report/info_player_disabled.444",
        "537ab4f3f36a9246838e84f33a520d0fd26ec818b160a9fcae891b929cee2f34",
        3972, (274, 16), 0x837ECC, 0x943530, 0x943510, (0x483A81,), "wrapper",
    ),
    _r(
        "info_popup",
        "FM2001_Art/Generic/match_report/info_popup.444",
        "d4bcf7d57b5e38de01d43e214d937045529e6434d1c40bb0f04620753c18f5e6",
        179988, (760, 500), 0x837F08, 0x9434F0, 0x9434D0, (0x484FFF,), "raw",
    ),
    _r(
        "red_card",
        "FM2001_Art/Generic/match_report/red_card.444",
        "215c223e62062f7f61745f6f72a85e25459becd4b2f05f8164997664f51ef019",
        688, (14, 14), 0x837F38, 0x9434B0, 0x943490, (0x485A50, 0x4860C0), "wrapper",
    ),
    _r(
        "yellow_card",
        "FM2001_Art/Generic/match_report/yellow_card.444",
        "b6b13283b398da35cc7af76a8f1d8a2327e9445397efba1766753c3ee6891ff8",
        724, (14, 14), 0x837F68, 0x943470, 0x943450, (0x48366D, 0x485A24, 0x486094), "wrapper",
    ),
    _r(
        "sub_on",
        "FM2001_Art/Generic/match_report/Sub_on.444",
        "cee9c2b9b17834606d9414d9c04f8a1f0e1f7ee621f9d2695c7f45e4d4b28fe1",
        528, (14, 14), 0x837F98, 0x943430, 0x943410, (0x485A81, 0x4860F1), "wrapper",
    ),
    _r(
        "sub_off",
        "FM2001_Art/Generic/match_report/sub_off.444",
        "5f9837e6444eb1d724d0e845ac0f70d02180f1d3a6d7a4c9a3d45bef0598eb32",
        576, (14, 14), 0x837FC4, 0x9433F0, 0x9433D0, (0x485A9E, 0x48610E), "wrapper",
    ),
    _r(
        "injured",
        "FM2001_Art/Generic/match_report/injured.444",
        "ab0820167dd7ebf2840906a16beaec7b8895202a3f6be77995eab94b33dfc41f",
        736, (14, 14), 0x837FF0, 0x9433B0, 0x943390, (0x4859FD, 0x48606D), "wrapper",
    ),
    _r(
        "score",
        "FM2001_Art/Generic/match_report/score.444",
        "49b2ef946e1934d25ab23cb30e35035ef0c6c0bf07eee950ba5b676d01d9bcae",
        700, (14, 14), 0x83801C, 0x943370, 0x943350, (0x4859D5, 0x486045), "wrapper",
    ),
    _r(
        "red_card_single",
        "FM2001_Art/Generic/match_report/red_card_single.444",
        "f5f721db52098a1a9b14ddac30c76265e478e49ee53db09ab0f2d1e04656ee25",
        700, (14, 14), 0x838048, 0x943330, 0x943310, (0x485A5C, 0x4860CC), "wrapper",
    ),
    _r(
        "name_block_1",
        "FM2001_Art/Generic/match_report/name_block_1.444",
        "79a1eddbdd497992aa85f564269b396dbc6bf00eee95eca280e3e4268f81c832",
        3528, (195, 36), 0x83807C, 0x9432F0, 0x9432D0,
    ),
    _r(
        "name_block_2",
        "FM2001_Art/Generic/match_report/name_block_2.444",
        "aa4b9e3976d6f84a74bd0bc60bd4cd64701e2bd5bae68ce282b6ca9eed462272",
        3228, (195, 36), 0x8380B0, 0x9432B0, 0x943290,
    ),
    _r(
        "name_block_3",
        "FM2001_Art/Generic/match_report/name_block_3.444",
        "fedd753e3eba4dcc125af7493401e2f0371636856a9a6f4814e243e896c3b24c",
        3536, (195, 36), 0x8380E4, 0x943270, 0x943250,
    ),
    _r(
        "name_block_4",
        "FM2001_Art/Generic/match_report/name_block_4.444",
        "9b1f5e3dc6eb4099cef0be89038cd2776035c0e9c95bf8751f361a44d927a211",
        3212, (195, 36), 0x838118, 0x943230, 0x943210,
    ),
    _r(
        "match_name_grid",
        "FM2001_Art/Generic/match_report/match_name_grid.444",
        "03ee3fca92ce681dbf8d4c2a00958bc00447a15822c5efaf6341073609dfc068",
        3036, (185, 36), 0x83814C, 0x9431F0, 0x9431D0, (0x483541, 0x483784), "raw",
    ),
    _r(
        "poss_back",
        "FM2001_Art/Generic/match_report/poss_back.444",
        "e8090259d1f38e13f22918475a8057a9ffd29145d7d6950dd214cb16982b7392",
        7140, (294, 25), 0x838180, 0x9431B0, 0x943190,
    ),
    _r(
        "poss_blue",
        "FM2001_Art/Generic/match_report/poss_blue.444",
        "18a440005bfc980aadf30be1ce583c2cc089d6a5c7b38d0ac08aa1e89a852119",
        8372, (264, 21), 0x8381B0, 0x943170, 0x943150,
    ),
    _r(
        "poss_yellow",
        "FM2001_Art/Generic/match_report/poss_yellow.444",
        "396cfe3a52263e3c24ab59b3d4f240e42c408afc9182125eb967ef5d56570c94",
        7976, (264, 21), 0x8381E0, 0x943130, 0x943110,
    ),
    _r(
        "pitch_normal",
        "FM2001_Art/Generic/match_report/pitch_normal.444",
        "73f6c0ecc57a383c63288064c371f947772f584800dfd3f4d2b1323063d9a6ba",
        15932, (294, 78), 0x838210, 0x9430F0, 0x9430D0, (0x483B1E,), "raw",
    ),
    _r(
        "match_incid_grid",
        "FM2001_Art/Generic/match_report/match_incid_grid.444",
        "0d7ba8c3de23ac24f0610233eb9381b0e5a7e620299acd52781a27966f8c50f3",
        2788, (142, 36), 0x838244, 0x9430B0, 0x943090, (0x4835AD, 0x4837EC), "raw",
    ),
)

PMATCHINFO_RESOURCE_BY_NAME = {resource.name: resource for resource in PMATCHINFO_RESOURCES}


PMATCHINFO_RUNTIME_PRESENTATION_RESOURCE_NAMES = tuple(
    resource.name for resource in PMATCHINFO_RESOURCES
    if resource.direct_consumer_vas
)
PMATCHINFO_STAGED_PRESENTATION_RESOURCE_NAMES = tuple(
    PMATCHINFO_RUNTIME_PRESENTATION_RESOURCE_NAMES
)
PMATCHINFO_PENDING_PRESENTATION_RESOURCE_NAMES = ()
PMATCHINFO_IMPORT_ROOT = Path("original_assets/source")


def pmatchinfo_import_path(repo_root: Path, resource_name: str) -> Path:
    try:
        resource = PMATCHINFO_RESOURCE_BY_NAME[resource_name]
    except KeyError as exc:
        raise OriginalPMatchInfoResourceError(
            f"Unknown PMatchInfo import resource: {resource_name}"
        ) from exc
    return Path(repo_root) / PMATCHINFO_IMPORT_ROOT / resource.source_path


def validate_staged_pmatchinfo_presentation_assets(
    repo_root: Path,
) -> tuple[OriginalPMatchInfoResource, ...]:
    """Verify every byte-identical runtime-consumed PMatchInfo asset in Git."""
    validated = []
    for name in PMATCHINFO_STAGED_PRESENTATION_RESOURCE_NAMES:
        resource = PMATCHINFO_RESOURCE_BY_NAME[name]
        path = pmatchinfo_import_path(repo_root, name)
        try:
            data = path.read_bytes()
        except FileNotFoundError as exc:
            raise OriginalPMatchInfoResourceError(
                f"Missing staged PMatchInfo asset: {resource.source_path}"
            ) from exc
        if len(data) != resource.byte_size:
            raise OriginalPMatchInfoResourceError(
                f"Staged PMatchInfo byte-size mismatch: {resource.source_path}"
            )
        if sha256(data).hexdigest() != resource.sha256:
            raise OriginalPMatchInfoResourceError(
                f"Staged PMatchInfo checksum mismatch: {resource.source_path}"
            )
        header = parse_ea444_header(data)
        if (header.width, header.height) != resource.size:
            raise OriginalPMatchInfoResourceError(
                f"Staged PMatchInfo geometry mismatch: {resource.source_path}"
            )
        validated.append(resource)
    return tuple(validated)

@dataclass(frozen=True)
class OriginalPMatchInfoUnconsumedResourceAudit:
    resource_name: str
    raw_handle_va: int
    wrapper_va: int
    raw_literal_xrefs: tuple[int, ...]
    wrapper_literal_xrefs: tuple[int, ...]
    wrapper_field_literal_xrefs: tuple[int, ...]


# Recovery 159 exhaustively scanned canonical footballmanager.exe for literal
# references to every address in the seven previously unresolved 0x20-byte
# wrapper objects and their raw handles. No PMatchInfo/TeamInfo/Finance/runtime
# presentation method references any of them. The exact hits below are confined
# to static resource construction/teardown and two family-wide lifetime sweeps.
PMATCHINFO_UNCONSUMED_RESOURCE_NAMES = (
    "name_block_1",
    "name_block_2",
    "name_block_3",
    "name_block_4",
    "poss_back",
    "poss_blue",
    "poss_yellow",
)

PMATCHINFO_UNCONSUMED_RESOURCE_AUDIT = (
    OriginalPMatchInfoUnconsumedResourceAudit(
        "name_block_1", 0x9432F0, 0x9432D0,
        (0x5FB839, 0x5FB860, 0x5FB894, 0x6017C8, 0x60296A),
        (0x5FB899,), (0x5FB89E,),
    ),
    OriginalPMatchInfoUnconsumedResourceAudit(
        "name_block_2", 0x9432B0, 0x943290,
        (0x5FB8C9, 0x5FB8F0, 0x5FB924, 0x6017D2, 0x602975),
        (0x5FB929,), (0x5FB92E,),
    ),
    OriginalPMatchInfoUnconsumedResourceAudit(
        "name_block_3", 0x943270, 0x943250,
        (0x5FB959, 0x5FB980, 0x5FB9B4, 0x6017DC, 0x602980),
        (0x5FB9B9,), (0x5FB9BE,),
    ),
    OriginalPMatchInfoUnconsumedResourceAudit(
        "name_block_4", 0x943230, 0x943210,
        (0x5FB9E9, 0x5FBA10, 0x5FBA44, 0x6017E6, 0x60298B),
        (0x5FBA49,), (0x5FBA4E,),
    ),
    OriginalPMatchInfoUnconsumedResourceAudit(
        "poss_back", 0x9431B0, 0x943190,
        (0x5FBB09, 0x5FBB30, 0x5FBB64, 0x6017FA, 0x6029A1),
        (0x5FBB69,), (0x5FBB6E,),
    ),
    OriginalPMatchInfoUnconsumedResourceAudit(
        "poss_blue", 0x943170, 0x943150,
        (0x5FBB99, 0x5FBBC0, 0x5FBBF4, 0x601804, 0x6029AC),
        (0x5FBBF9,), (0x5FBBFE,),
    ),
    OriginalPMatchInfoUnconsumedResourceAudit(
        "poss_yellow", 0x943130, 0x943110,
        (0x5FBC29, 0x5FBC50, 0x5FBC84, 0x60180E, 0x6029B7),
        (0x5FBC89,), (0x5FBC8E,),
    ),
)


def assert_pmatchinfo_unconsumed_resource_boundary() -> None:
    """Fail if unresolved artwork is silently promoted to a UI consumer."""
    if tuple(a.resource_name for a in PMATCHINFO_UNCONSUMED_RESOURCE_AUDIT) != (
        PMATCHINFO_UNCONSUMED_RESOURCE_NAMES
    ):
        raise OriginalPMatchInfoResourceError(
            "PMatchInfo unconsumed-resource audit order drifted"
        )
    for audit in PMATCHINFO_UNCONSUMED_RESOURCE_AUDIT:
        resource = PMATCHINFO_RESOURCE_BY_NAME[audit.resource_name]
        if resource.raw_handle_va != audit.raw_handle_va:
            raise OriginalPMatchInfoResourceError(
                f"Raw handle drift for {audit.resource_name}"
            )
        if resource.wrapper_va != audit.wrapper_va:
            raise OriginalPMatchInfoResourceError(
                f"Wrapper handle drift for {audit.resource_name}"
            )
        if resource.direct_consumer_vas:
            raise OriginalPMatchInfoResourceError(
                f"Unproven presentation consumer added for {audit.resource_name}"
            )




def pmatchinfo_dynamic_incident_resources() -> tuple[OriginalPMatchInfoResource, ...]:
    """Return the exact seven wrappers switched through the shared row icon slot."""
    return tuple(
        PMATCHINFO_RESOURCE_BY_NAME[name]
        for name in PMATCHINFO_DYNAMIC_INCIDENT_RESOURCE_NAMES
    )


def pmatchinfo_placements_for_resource(
    resource_name: str,
) -> tuple[OriginalPMatchInfoPlacement, ...]:
    """Return only source-proven local 0x64F380 placements for a resource."""
    if not isinstance(resource_name, str) or not resource_name:
        raise OriginalPMatchInfoResourceError(
            "PMatchInfo placement resource name must be a non-empty string"
        )
    if resource_name not in PMATCHINFO_RESOURCE_BY_NAME:
        raise OriginalPMatchInfoResourceError(
            f"Unknown PMatchInfo resource for placement: {resource_name}"
        )
    return tuple(
        placement
        for placement in PMATCHINFO_RESOURCE_PLACEMENTS
        if placement.resource_name == resource_name
    )


def assert_pmatchinfo_placement_resources_are_bound() -> None:
    """Reject geometry that points at a resource outside the verified family."""
    for placement in PMATCHINFO_RESOURCE_PLACEMENTS:
        try:
            resource = PMATCHINFO_RESOURCE_BY_NAME[placement.resource_name]
        except KeyError as exc:
            raise OriginalPMatchInfoResourceError(
                f"Placement references unbound PMatchInfo resource: "
                f"{placement.resource_name}"
            ) from exc
        if placement.width <= 0 or placement.height <= 0:
            raise OriginalPMatchInfoResourceError(
                f"Invalid PMatchInfo placement size for {placement.resource_name}"
            )
        if placement.width > resource.size[0] or placement.height > resource.size[1]:
            raise OriginalPMatchInfoResourceError(
                f"PMatchInfo placement exceeds source geometry: "
                f"{placement.resource_name}"
            )


def validate_original_pmatchinfo_resources(
    source_root: Path,
) -> tuple[OriginalPMatchInfoResource, ...]:
    """Require all exact firsthand-verified PMatchInfo Match_report files."""
    root = Path(source_root)
    for resource in PMATCHINFO_RESOURCES:
        path = root / resource.source_path
        try:
            data = path.read_bytes()
        except FileNotFoundError as exc:
            raise OriginalPMatchInfoResourceError(
                f"Missing original PMatchInfo resource: {resource.source_path}"
            ) from exc
        if len(data) != resource.byte_size:
            raise OriginalPMatchInfoResourceError(
                f"PMatchInfo byte-size mismatch: {resource.source_path}"
            )
        if sha256(data).hexdigest() != resource.sha256:
            raise OriginalPMatchInfoResourceError(
                f"PMatchInfo checksum mismatch: {resource.source_path}"
            )
        header = parse_ea444_header(data)
        if (header.width, header.height) != resource.size:
            raise OriginalPMatchInfoResourceError(
                f"PMatchInfo geometry mismatch: {resource.source_path}"
            )
    return PMATCHINFO_RESOURCES


def assert_pmatchinfo_identity_contract() -> None:
    """Guard the PMatchInfo identity already proven by populated fixture navigation."""
    if (
        LEAGUE_FIXTURES_MATCH_INFO_CLASS != "PMatchInfo"
        or LEAGUE_FIXTURES_MATCH_INFO_TYPE_DESCRIPTOR_VA != 0x81D058
        or LEAGUE_FIXTURES_MATCH_INFO_VFTABLE_VA != 0x7C41D4
        or LEAGUE_FIXTURES_MATCH_INFO_CONSTRUCTOR_VA != 0x487580
    ):
        raise OriginalPMatchInfoResourceError(
            "PMatchInfo resources require the source-proven PMatchInfo RTTI contract"
        )
