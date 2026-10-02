"""Source-backed PLeagueTables selector and table-header shell.

Recovery 161 starts the League Tables presentation recovery from the canonical
FM2001 executable.  This module records only bounded source facts from
PLeagueTables::0x446F00 / 0x448640 / 0x448C40 and the complete English loader.
Recovery 162 extends that boundary through the concrete list/row composition,
visible field projection, and exact original league_tables graphic family.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_header import parse_ea444_header
from original_management_navigation import LEAGUE_TABLES_PANEL


class OriginalLeagueTablesError(ValueError):
    pass


LEAGUE_TABLES_CLASS = "PLeagueTables"
LEAGUE_TABLES_CONSTRUCTOR_VA = 0x448640
LEAGUE_TABLES_SETUP_VA = 0x446F00
LEAGUE_TABLES_EVENT_VA = 0x448C40
LEAGUE_TABLES_VFTABLE_VA = 0x7C00C8
LEAGUE_TABLES_TYPE_DESCRIPTOR_VA = 0x81B458

LEAGUE_TABLES_SELECTOR_CLASS = "fmRadioTextSm@fm2001_ctrls"
LEAGUE_TABLES_SELECTOR_CONSTRUCTOR_VA = 0x5D4B50
LEAGUE_TABLES_SELECTOR_SETUP_VA = 0x5D4C70
LEAGUE_TABLES_SELECTOR_STRIDE = 0x4C

LEAGUE_TABLES_ACTIVE_COUNTRY_INDEX_OFFSET = 0x64
LEAGUE_TABLES_COUNTRY_ID_BASE_OFFSET = 0x1D4
LEAGUE_TABLES_COUNTRY_CONTROL_BASE_OFFSET = 0x23C
LEAGUE_TABLES_COUNTRY_SELECTOR_COUNT = 8
LEAGUE_TABLES_COUNTRY_EVENT_FIRST = 1

# Constructor writes these eight literal country identities in this exact
# source order at object+0x1D4..+0x1F0.
LEAGUE_TABLES_COUNTRY_IDS = (26, 33, 40, 73, 66, 31, 24, 9)
LEAGUE_TABLES_COUNTRY_NAMES = (
    "England",
    "Germany",
    "Italy",
    "Spain",
    "Scotland",
    "France",
    "Holland",
    "Belgium",
)
LEAGUE_TABLES_COUNTRY_SETUP_CALLS = (
    0x446FE5,
    0x447044,
    0x4470A5,
    0x447103,
    0x447164,
    0x4471C4,
    0x447227,
    0x44728F,
)

# Recovery 161 continuation closes the two remaining selector families.
# Events 9..13 are a dynamic DIVISION selector over the active country's
# non-DummyLeague LeagueBase entries. Event IDs are stored at control+0x20;
# the event handler scans exactly five controls and loads the selected source
# identity from object+0xA0+4*index.
LEAGUE_TABLES_DIVISION_HEADER_CONTROL_OFFSET = 0x49C
LEAGUE_TABLES_DIVISION_HEADER_SETUP_VA = 0x5D6090
LEAGUE_TABLES_DIVISION_HEADER_CALL_VA = 0x4472C1
LEAGUE_TABLES_DIVISION_HEADER_GLOBAL_VA = 0x982678
LEAGUE_TABLES_DIVISION_HEADER_ENGLISH_INDEX = 2144
LEAGUE_TABLES_DIVISION_HEADER_TEXT = "DIVISION"
LEAGUE_TABLES_DIVISION_SELECTOR_BASE_OFFSET = 0x4E4
LEAGUE_TABLES_DIVISION_SELECTOR_COUNT = 5
LEAGUE_TABLES_DIVISION_EVENT_FIRST = 9
LEAGUE_TABLES_SELECTED_DIVISION_INDEX_OFFSET = 0x68
LEAGUE_TABLES_SELECTED_DIVISION_IDENTITY_OFFSET = 0x8C
LEAGUE_TABLES_DIVISION_IDENTITY_ARRAY_OFFSET = 0xA0
LEAGUE_TABLES_DIVISION_SETUP_CALLS = (
    0x447306,
    0x447353,
    0x4473A1,
    0x4473F2,
    0x447440,
)
LEAGUE_TABLES_DIVISION_REBUILD_VA = 0x448E60
LEAGUE_TABLES_DIVISION_SET_TEXT_VA = 0x5D3F10
LEAGUE_TABLES_LEAGUE_BASE_TYPE_DESCRIPTOR_VA = 0x818AA0
LEAGUE_TABLES_DUMMY_LEAGUE_TYPE_DESCRIPTOR_VA = 0x81B498
LEAGUE_TABLES_RTDYNAMICCAST_VA = 0x668995
LEAGUE_TABLES_COUNTRY_COMPETITION_ARRAY_OFFSET = 0x48
LEAGUE_TABLES_COUNTRY_COMPETITION_COUNT_OFFSET = 0x4C
LEAGUE_TABLES_DIVISION_CAPTION_OFFSET = 0x14
LEAGUE_TABLES_DIVISION_IDENTITY_WORD_OFFSET = 0x20

# Events 14 and 15 are an exact two-state Sort By family. The source initializes
# object+0x98 to 0, so League Position is the default; event 15 sets state 1.
LEAGUE_TABLES_SORT_HEADER_CONTROL_OFFSET = 0x660
LEAGUE_TABLES_SORT_HEADER_SETUP_VA = 0x5D6090
LEAGUE_TABLES_SORT_HEADER_CALL_VA = 0x447472
LEAGUE_TABLES_SORT_HEADER_GLOBAL_VA = 0x983A94
LEAGUE_TABLES_SORT_HEADER_ENGLISH_INDEX = 857
LEAGUE_TABLES_SORT_HEADER_TEXT = "Sort By"
LEAGUE_TABLES_SORT_SELECTOR_BASE_OFFSET = 0x6A8
LEAGUE_TABLES_SORT_SELECTOR_COUNT = 2
LEAGUE_TABLES_SORT_EVENT_FIRST = 14
LEAGUE_TABLES_SORT_STATE_OFFSET = 0x98
LEAGUE_TABLES_SORT_DEFAULT_STATE = 0
LEAGUE_TABLES_SORT_SETUP_CALLS = (0x4474B5, 0x447501)
LEAGUE_TABLES_SORT_OPTIONS = (
    ("League Position", 0x983C04, 765, 14, 0),
    ("Current Form", 0x983A90, 858, 15, 1),
)
LEAGUE_TABLES_SORT_APPLY_VA = 0x449090

# Recovery 164 private-source closure: the seven objects toggled by the sort
# apply routine are the P/W/D/L/F/A/Pts eCText header controls. State 0 calls
# vtable +0x30 on each object, forwarding boolean 1 to the shared bit-state
# method; state 1 calls +0x34, forwarding 0. The latter clears bits 0x8 and
# 0x1, while the former sets bit 0x1. Current Form row ordering remains a
# separate fail-closed boundary at 0x4F4A10.
LEAGUE_TABLES_STAT_HEADER_CLASS = "eCText"
LEAGUE_TABLES_STAT_HEADER_TYPE_DESCRIPTOR_VA = 0x8198F8
LEAGUE_TABLES_STAT_HEADER_COL_VA = 0x7E01D0
LEAGUE_TABLES_STAT_HEADER_VFTABLE_VA = 0x7BE340
LEAGUE_TABLES_STAT_HEADER_CONTROL_OFFSETS = (
    0x7FC, 0x83C, 0x87C, 0x8BC, 0x8FC, 0x93C, 0x97C,
)
LEAGUE_TABLES_STAT_HEADER_STRIDE = 0x40
LEAGUE_TABLES_STAT_HEADER_ENABLE_SLOT = 0x30
LEAGUE_TABLES_STAT_HEADER_DISABLE_SLOT = 0x34
LEAGUE_TABLES_STAT_HEADER_ENABLE_TARGET_VA = 0x64F510
LEAGUE_TABLES_STAT_HEADER_DISABLE_TARGET_VA = 0x64F520
LEAGUE_TABLES_STAT_HEADER_BOOL_STATE_VA = 0x64F3E0
LEAGUE_TABLES_STAT_HEADER_STATE_BITS_OFFSET = 0x18


@dataclass(frozen=True)
class OriginalLeagueTablesStatHeaderState:
    sort_state: int
    active: bool
    virtual_slot_offset: int
    boolean_argument: int
    set_bits: tuple[int, ...]
    cleared_bits: tuple[int, ...]


def league_tables_stat_header_state(
    sort_state: int,
) -> OriginalLeagueTablesStatHeaderState:
    """Return the exact seven-header state transform selected by 0x449090."""
    if type(sort_state) is not int or sort_state not in (0, 1):
        raise OriginalLeagueTablesError(
            "League Tables sort state must be source state 0 or 1"
        )
    if sort_state == 0:
        return OriginalLeagueTablesStatHeaderState(
            0, True, 0x30, 1, (0x1,), (),
        )
    return OriginalLeagueTablesStatHeaderState(
        1, False, 0x34, 0, (), (0x8, 0x1),
    )

# Backward-compatible structural aliases retained for callers/tests written at
# the earlier checkpoint.
LEAGUE_TABLES_SECONDARY_SELECTOR_BASE_OFFSET = LEAGUE_TABLES_DIVISION_SELECTOR_BASE_OFFSET
LEAGUE_TABLES_SECONDARY_SELECTOR_COUNT = LEAGUE_TABLES_DIVISION_SELECTOR_COUNT
LEAGUE_TABLES_SECONDARY_SETUP_CALLS = LEAGUE_TABLES_DIVISION_SETUP_CALLS
LEAGUE_TABLES_TERTIARY_SELECTOR_BASE_OFFSET = LEAGUE_TABLES_SORT_SELECTOR_BASE_OFFSET
LEAGUE_TABLES_TERTIARY_SELECTOR_COUNT = LEAGUE_TABLES_SORT_SELECTOR_COUNT
LEAGUE_TABLES_TERTIARY_SETUP_CALLS = LEAGUE_TABLES_SORT_SETUP_CALLS

LEAGUE_TABLES_COUNTRY_HEADER_CONTROL_OFFSET = 0x1F4
LEAGUE_TABLES_COUNTRY_HEADER_SETUP_VA = 0x5D6090
LEAGUE_TABLES_COUNTRY_HEADER_CALL_VA = 0x446F92
LEAGUE_TABLES_COUNTRY_HEADER_X = 27
LEAGUE_TABLES_COUNTRY_HEADER_WIDTH = 150
LEAGUE_TABLES_COUNTRY_HEADER_GLOBAL_VA = 0x982670
LEAGUE_TABLES_COUNTRY_HEADER_ENGLISH_INDEX = 2146
LEAGUE_TABLES_COUNTRY_HEADER_TEXT = "Country"

LEAGUE_TABLES_TEXT_SETUP_VA = 0x6503F0
# Factory case 0x47C6D1 calls the shared panel layout wrapper at 0x47F5C0.
# That wrapper forwards x=0, y=0 and fixed 800x600 to 0x653320.
LEAGUE_TABLES_PANEL_LAYOUT_WRAPPER_VA = 0x47F5C0
LEAGUE_TABLES_PANEL_LAYOUT_CALL_VA = 0x47C70A
LEAGUE_TABLES_PANEL_RECT = (0, 0, 800, 600)
LEAGUE_TABLES_HEADER_Y = 152
LEAGUE_TABLES_HEADER_HEIGHT = 19


# Recovery 162: concrete table/list and row presentation.
LEAGUE_TABLES_LIST_CLASS = "CLeagueTableList"
LEAGUE_TABLES_LIST_TYPE_DESCRIPTOR_VA = 0x81B478
LEAGUE_TABLES_LIST_COL_VA = 0x7E1520
LEAGUE_TABLES_LIST_VFTABLE_VA = 0x7C011C
LEAGUE_TABLES_LIST_SETUP_WRAPPER_VA = 0x4477E0
LEAGUE_TABLES_LIST_GENERIC_SETUP_VA = 0x6510F0
LEAGUE_TABLES_LIST_OBJECT_OFFSET = 0x9BC
LEAGUE_TABLES_LIST_RECT = (270, 184, 477, 384)
LEAGUE_TABLES_LIST_ROW_COUNT = 24
LEAGUE_TABLES_LIST_ROW_STEP = 16
LEAGUE_TABLES_LIST_AUX_VALUE = 8
LEAGUE_TABLES_LIST_SOURCE_POINTER_OFFSET = 0x4C
LEAGUE_TABLES_LIST_ROW_CREATE_VA = 0x447820
LEAGUE_TABLES_LIST_ROW_SPAN_VA = 0x4466E0
LEAGUE_TABLES_LIST_ROW_HEIGHT_VA = 0x446710

LEAGUE_TABLES_ROW_CLASS = "PLeagueTableRow"
LEAGUE_TABLES_ROW_TYPE_DESCRIPTOR_VA = 0x81B378
LEAGUE_TABLES_ROW_COL_VA = 0x7E1398
LEAGUE_TABLES_ROW_VFTABLE_VA = 0x7BFEC0
LEAGUE_TABLES_ROW_SETUP_VA = 0x446930
LEAGUE_TABLES_ROW_ALLOC_SIZE = 0x4A8
LEAGUE_TABLES_ROW_SOURCE_RECORD_OFFSET = 0x70
LEAGUE_TABLES_ROW_RANK_VALUE_OFFSET = 0xC4
LEAGUE_TABLES_ROW_CHILD_COUNT = 12
LEAGUE_TABLES_ROW_BACKGROUND_OFFSET = 0xC8
LEAGUE_TABLES_ROW_ICON_BACKGROUND_OFFSET = 0xF8
LEAGUE_TABLES_ROW_ICON_OFFSET = 0x12C
LEAGUE_TABLES_ROW_RANK_TEXT_OFFSET = 0x160
LEAGUE_TABLES_ROW_CLUB_TEXT_OFFSET = 0x1C0
LEAGUE_TABLES_ROW_STAT_TEXT_OFFSETS = (0x208, 0x268, 0x2C8, 0x328, 0x388, 0x3E8, 0x448)
LEAGUE_TABLES_ROW_STAT_SOURCE_OFFSETS = (0x10, 0x14, 0x18, 0x1C, 0x20, 0x24)
LEAGUE_TABLES_ROW_POINTS_SOURCE_OFFSETS = (0x14, 0x18)
LEAGUE_TABLES_ROW_POINTS_FORMULA = "3*field_0x14 + field_0x18"

# Local row coordinates. Adding list x=270 yields the recovered header x
# positions 316 and 532..706 exactly.
LEAGUE_TABLES_ROW_RANK_RECT = (23, 1, 21, 12)
LEAGUE_TABLES_ROW_CLUB_RECT = (46, 1, 214, 12)
LEAGUE_TABLES_ROW_STAT_RECTS = tuple(
    (x, 1, 27, 12) for x in (262, 291, 320, 349, 378, 407, 436)
)
LEAGUE_TABLES_ROW_COLUMN_LABELS = ("P", "W", "D", "L", "F", "A", "Pts")
LEAGUE_TABLES_ROW_COLUMN_SOURCE_OFFSETS = {
    "P": (0x10,),
    "W": (0x14,),
    "D": (0x18,),
    "L": (0x1C,),
    "F": (0x20,),
    "A": (0x24,),
    "Pts": (0x14, 0x18),
}
LEAGUE_TABLES_ROW_COLUMN_EXPRESSIONS = {
    "P": "field_0x10",
    "W": "field_0x14",
    "D": "field_0x18",
    "L": "field_0x1C",
    "F": "field_0x20",
    "A": "field_0x24",
    "Pts": "3*field_0x14 + field_0x18",
}

LEAGUE_TABLES_POSITION_SORT_VA = 0x4F4940
LEAGUE_TABLES_CURRENT_FORM_SORT_VA = 0x4F4A10
LEAGUE_TABLES_ROW_SOURCE_ARRAY_OFFSET = 0x34


@dataclass(frozen=True)
class OriginalLeagueTablesResource:
    name: str
    source_path: str
    sha256: str
    byte_size: int
    size: tuple[int, int]
    raw_handle_va: int
    wrapper_va: int


LEAGUE_TABLES_RESOURCES = (
    OriginalLeagueTablesResource("champion_grid", "FM2001_Art/Generic/league_tables/champion_grid.444", "f5aff1a476454aed18929b2066c4a5eb921541a417f728ba3ce31be5ed33f9f8", 8512, (477, 14), 0x944F10, 0x944EF0),
    OriginalLeagueTablesResource("promotion_grid", "FM2001_Art/Generic/league_tables/promotion_grid.444", "4e6e6a9fcf1d74e0b60d90a7d1e512cee8820aed29e7c6c5c3c1f9c458e551bd", 7096, (477, 14), 0x944ED0, 0x944EB0),
    OriginalLeagueTablesResource("relegation_grid", "FM2001_Art/Generic/league_tables/relegation_grid.444", "6d2d5b9ee4f748ffc30421b163aec587d00e13cadee9da8a75f0cf4308a9ad66", 7288, (477, 14), 0x944E90, 0x944E70),
    OriginalLeagueTablesResource("standard_grid", "FM2001_Art/Generic/league_tables/standard_grid.444", "2d86918c10c13270e072ac8a5e9043a3a180833eb609e98acf0b0fffc7445424", 7304, (477, 14), 0x944E50, 0x944E30),
    OriginalLeagueTablesResource("your_team_grid", "FM2001_Art/Generic/league_tables/your_team_grid.444", "6f76914a898050ccb4de268ac932f5258f11ef5fcc99a9359b85520417c1e65a", 8068, (477, 14), 0x944E10, 0x944DF0),
    OriginalLeagueTablesResource("playoff_grid", "FM2001_Art/Generic/league_tables/playoff_grid.444", "f238ed77c72e7a9a1df51f74479c8ff17a4d3481d3059cf75d878f75a6f83d1c", 7068, (477, 14), 0x944DD0, 0x944DB0),
    OriginalLeagueTablesResource("champion_icon", "FM2001_Art/Generic/league_tables/champion_icon.444", "dd287e3e8cef59e781c820d45b7ea31cd5dc760bdfe09934b1c3835ba3af970c", 688, (20, 12), 0x944D90, 0x944D70),
    OriginalLeagueTablesResource("promotion_icon", "FM2001_Art/Generic/league_tables/promotion_icon.444", "ac5875ba2c16fb7f9a3c79303626175007b1347003ea1f6e0052878af7ddb92d", 512, (20, 12), 0x944D50, 0x944D30),
    OriginalLeagueTablesResource("relegation_icon", "FM2001_Art/Generic/league_tables/relegation_icon.444", "77bce1f3747c6eb6809e86b8f212cf13434eaa5444c8552fc8f2ddaa1077fada", 644, (20, 12), 0x944D10, 0x944CF0),
    OriginalLeagueTablesResource("playoff_icon", "FM2001_Art/Generic/league_tables/playoff_icon.444", "e6077fd02c509e4383820c44cc43ba10c2b55763223ec6153076537b0c7f6127", 552, (20, 12), 0x944CD0, 0x944CB0),
    OriginalLeagueTablesResource("your_champion_icon", "FM2001_Art/Generic/league_tables/your_champion_icon.444", "e41c68820396153631c0b965150f8987cf36726a56e26b5014070a5af9b64917", 576, (20, 12), 0x944C90, 0x944C70),
    OriginalLeagueTablesResource("your_promotion_icon", "FM2001_Art/Generic/league_tables/your_promotion_icon.444", "6e4412a1528ef162ff52648218189422f0b1270841d663e656660d083e29935b", 488, (20, 12), 0x944C50, 0x944C30),
    OriginalLeagueTablesResource("your_relegation_icon", "FM2001_Art/Generic/league_tables/your_relegation_icon.444", "ee0f0982da9b009afab0cef319e7dd28de4fea1abda25b558416151c28a790f2", 492, (20, 12), 0x944C10, 0x944BF0),
    OriginalLeagueTablesResource("your_playoff_icon", "FM2001_Art/Generic/league_tables/your_playoff_icon.444", "acddcc458b76e92e2b5044cac509511f35b74b5dc0432cefdf790678216d23d8", 552, (20, 12), 0x944BD0, 0x944BB0),
    OriginalLeagueTablesResource("league_bar", "FM2001_Art/Generic/league_tables/league_bar.444", "818c42b75cecaac2ad310c2586f8539fc3d30411715d702c1f6056c9332cd4cd", 5552, (475, 19), 0x944B90, 0x944B70),
)
LEAGUE_TABLES_RESOURCE_BY_NAME = {resource.name: resource for resource in LEAGUE_TABLES_RESOURCES}


def validate_original_league_tables_resources(
    source_root: Path,
) -> tuple[OriginalLeagueTablesResource, ...]:
    """Require all 15 exact source-owned League Tables graphics."""
    root = Path(source_root)
    for resource in LEAGUE_TABLES_RESOURCES:
        path = root / resource.source_path
        try:
            data = path.read_bytes()
        except FileNotFoundError as exc:
            raise OriginalLeagueTablesError(
                f"Missing original League Tables resource: {resource.source_path}"
            ) from exc
        if len(data) != resource.byte_size:
            raise OriginalLeagueTablesError(
                f"League Tables byte-size mismatch: {resource.source_path}"
            )
        if sha256(data).hexdigest() != resource.sha256:
            raise OriginalLeagueTablesError(
                f"League Tables checksum mismatch: {resource.source_path}"
            )
        header = parse_ea444_header(data)
        if (header.width, header.height) != resource.size:
            raise OriginalLeagueTablesError(
                f"League Tables geometry mismatch: {resource.source_path}"
            )
    return LEAGUE_TABLES_RESOURCES
LEAGUE_TABLES_RESOURCE_PATH_LITERAL_VAS = {
    "champion_grid": 0x836A08,
    "promotion_grid": 0x836A3C,
    "relegation_grid": 0x836A70,
    "standard_grid": 0x836AA8,
    "your_team_grid": 0x836ADC,
    "playoff_grid": 0x836B10,
    "champion_icon": 0x836B44,
    "promotion_icon": 0x836B78,
    "relegation_icon": 0x836BAC,
    "playoff_icon": 0x836BE4,
    "your_champion_icon": 0x836C18,
    "your_promotion_icon": 0x836C50,
    "your_relegation_icon": 0x836C8C,
    "your_playoff_icon": 0x836CC8,
    "league_bar": 0x836D00,
}
LEAGUE_TABLES_RESOURCE_LOADER_START_VA = 0x5F7870
LEAGUE_TABLES_RESOURCE_LOADER_END_VA = 0x5F80C0


LEAGUE_TABLES_GRID_WRAPPERS = {
    "champion": 0x944EF0,
    "promotion": 0x944EB0,
    "relegation": 0x944E70,
    "standard": 0x944E30,
    "your_team": 0x944DF0,
    "playoff": 0x944DB0,
}
LEAGUE_TABLES_ICON_WRAPPERS = {
    "champion": (0x944D70, 0x944C70),
    "promotion": (0x944D30, 0x944C30),
    "relegation": (0x944CF0, 0x944BF0),
    "playoff": (0x944CB0, 0x944BB0),
}
LEAGUE_TABLES_BAR_CONTROL_OFFSET = 0x788
LEAGUE_TABLES_BAR_WRAPPER_VA = 0x944B70
LEAGUE_TABLES_BAR_RECT = (270, 152, 475, 19)


@dataclass(frozen=True)
class OriginalLeagueTablesHeaderText:
    label: str | None
    english_global_va: int | None
    english_index: int | None
    setup_call_va: int
    x: int
    y: int
    width: int
    height: int

    @property
    def rect(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.width, self.height)


LEAGUE_TABLES_HEADER_TEXTS = (
    OriginalLeagueTablesHeaderText(
        None, None, None, 0x447594, 316, 152, 214, 19
    ),
    OriginalLeagueTablesHeaderText(
        "P", 0x9830F4, 1473, 0x4475D7, 532, 152, 27, 19
    ),
    OriginalLeagueTablesHeaderText(
        "W", 0x9830F0, 1474, 0x44761A, 561, 152, 27, 19
    ),
    OriginalLeagueTablesHeaderText(
        "D", 0x9830EC, 1475, 0x44765D, 590, 152, 27, 19
    ),
    OriginalLeagueTablesHeaderText(
        "L", 0x9830E8, 1476, 0x4476A0, 619, 152, 27, 19
    ),
    OriginalLeagueTablesHeaderText(
        "F", 0x9830E4, 1477, 0x4476E3, 648, 152, 27, 19
    ),
    OriginalLeagueTablesHeaderText(
        "A", 0x9830E0, 1478, 0x447726, 677, 152, 27, 19
    ),
    OriginalLeagueTablesHeaderText(
        "Pts", 0x9830DC, 1479, 0x447769, 706, 152, 27, 19
    ),
)


def league_tables_country_event_index(event_id: int) -> int:
    """Map only source-proven country events 1..8 to selector indices."""
    if type(event_id) is not int:
        raise OriginalLeagueTablesError("League Tables event ID must be an integer")
    index = event_id - LEAGUE_TABLES_COUNTRY_EVENT_FIRST
    if not 0 <= index < LEAGUE_TABLES_COUNTRY_SELECTOR_COUNT:
        raise OriginalLeagueTablesError(
            f"League Tables event {event_id} is not a recovered country selector"
        )
    return index


def league_tables_country_identity(event_id: int) -> tuple[int, str]:
    index = league_tables_country_event_index(event_id)
    return LEAGUE_TABLES_COUNTRY_IDS[index], LEAGUE_TABLES_COUNTRY_NAMES[index]


def assert_league_tables_identity_contract() -> None:
    if (
        LEAGUE_TABLES_PANEL.panel_class != LEAGUE_TABLES_CLASS
        or LEAGUE_TABLES_PANEL.constructor_va != LEAGUE_TABLES_CONSTRUCTOR_VA
        or LEAGUE_TABLES_PANEL.type_descriptor_va != LEAGUE_TABLES_TYPE_DESCRIPTOR_VA
        or LEAGUE_TABLES_PANEL.vftable_va != LEAGUE_TABLES_VFTABLE_VA
    ):
        raise OriginalLeagueTablesError(
            "League Tables shell requires the source-proven PLeagueTables identity"
        )


def league_tables_division_event_index(event_id: int) -> int:
    """Map exact source events 9..13 to the five dynamic division slots."""
    if type(event_id) is not int:
        raise OriginalLeagueTablesError("League Tables event ID must be an integer")
    index = event_id - LEAGUE_TABLES_DIVISION_EVENT_FIRST
    if not 0 <= index < LEAGUE_TABLES_DIVISION_SELECTOR_COUNT:
        raise OriginalLeagueTablesError(
            f"League Tables event {event_id} is not a recovered division selector"
        )
    return index


def league_tables_sort_state(event_id: int) -> int:
    """Map exact source events 14/15 to the binary sort state."""
    if type(event_id) is not int:
        raise OriginalLeagueTablesError("League Tables event ID must be an integer")
    index = event_id - LEAGUE_TABLES_SORT_EVENT_FIRST
    if not 0 <= index < LEAGUE_TABLES_SORT_SELECTOR_COUNT:
        raise OriginalLeagueTablesError(
            f"League Tables event {event_id} is not a recovered sort selector"
        )
    return LEAGUE_TABLES_SORT_OPTIONS[index][4]
