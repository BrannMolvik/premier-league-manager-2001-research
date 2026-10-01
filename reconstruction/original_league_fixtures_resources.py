"""Source-backed original PLeagueFixtures graphic resources and grid geometry.

All six paths are exact literals from the canonical executable and were
revalidated against the authorized original disc in Recovery 150.  The module
keeps box-resource state semantics neutral beyond the original filenames; the
grid placements are exact calls made by PLeagueFixtures::0x46AA70.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_header import parse_ea444_header
from original_management_navigation import LEAGUE_FIXTURES_PANEL


class OriginalLeagueFixturesResourceError(ValueError):
    pass


LEAGUE_FIXTURES_SETUP_VA = 0x46AA70
LEAGUE_FIXTURES_BITMAP_SETUP_VA = 0x5D5280


@dataclass(frozen=True)
class OriginalLeagueFixturesResource:
    name: str
    source_path: str
    sha256: str
    byte_size: int
    size: tuple[int, int]
    path_literal_va: int
    load_init_va: int
    raw_handle_va: int
    wrapper_init_va: int
    wrapper_va: int


DATE_FIXTURES_BOX = OriginalLeagueFixturesResource(
    "date_fixtures_box",
    "FM2001_Art/Generic/league_fixtures/date_fixtures_box.444",
    "b02036ae2d37c893e74a60a53eb1cdb514585654773916978e88f11ef66ab142",
    148,
    (24, 13),
    0x836D30,
    0x5F80E0,
    0x944B50,
    0x5F8130,
    0x944B30,
)
PLAYED_FIXTURES_BOX = OriginalLeagueFixturesResource(
    "played_fixtures_box",
    "FM2001_Art/Generic/league_fixtures/played_fixtures_box.444",
    "8c61143070c399477af735683b9e8a7effdfffee25b27d397f321cfe3a7d0db4",
    144,
    (24, 13),
    0x836D6C,
    0x5F8170,
    0x944B10,
    0x5F81C0,
    0x944AF0,
)
RED_FIXTURES_BOX = OriginalLeagueFixturesResource(
    "red_fixtures_box",
    "FM2001_Art/Generic/league_fixtures/red_fixtures_box.444",
    "0acd8300cd9bbb129924270f354e0a7017d3f78729be4ad5311895f9f5064c2e",
    112,
    (24, 13),
    0x836DA8,
    0x5F8200,
    0x944AD0,
    0x5F8250,
    0x944AB0,
)
TOGGLED_FIXTURES_BOX = OriginalLeagueFixturesResource(
    "toggled_fixtures_box",
    "FM2001_Art/Generic/league_fixtures/toggled_fixtures_box.444",
    "d99af52f7c4f20c88bc93f24ac2447febf2250da161a639070af840721c2539e",
    152,
    (24, 13),
    0x836DE0,
    0x5F8290,
    0x944A90,
    0x5F82E0,
    0x944A70,
)
FIXTURES_HORIZONTAL_GRID = OriginalLeagueFixturesResource(
    "fixtures_hori_grid",
    "FM2001_Art/Generic/league_fixtures/fixtures_hori_grid.444",
    "37e94e0eb2420aa498ca98d560ab180f80d1b8b7ffc6d4e8c664c398f7ebf8db",
    2652,
    (132, 52),
    0x836E1C,
    0x5F8320,
    0x944A50,
    0x5F8370,
    0x944A30,
)
FIXTURES_VERTICAL_GRID = OriginalLeagueFixturesResource(
    "fixtures_vert_grid",
    "FM2001_Art/Generic/league_fixtures/fixtures_vert_grid.444",
    "726bbb5df0fb632592a5e9f902fff7ca109b55e07ab433776e8f6973476f0ecb",
    924,
    (24, 528),
    0x836E58,
    0x5F83B0,
    0x944A10,
    0x5F8400,
    0x9449F0,
)

LEAGUE_FIXTURES_RESOURCES = (
    DATE_FIXTURES_BOX,
    PLAYED_FIXTURES_BOX,
    RED_FIXTURES_BOX,
    TOGGLED_FIXTURES_BOX,
    FIXTURES_HORIZONTAL_GRID,
    FIXTURES_VERTICAL_GRID,
)

# Exact first two positional arguments passed to 0x5D5280 by
# PLeagueFixtures::0x46AA70.  They are treated as source x/y coordinates
# because the helper's callers consistently pass screen-space origins.
LEAGUE_FIXTURES_VERTICAL_GRID_POSITIONS = tuple(
    (378 + 29 * index, 98) for index in range(12)
)
LEAGUE_FIXTURES_HORIZONTAL_GRID_POSITIONS = tuple(
    (241, 235 + 14 * index) for index in range(24)
)

LEAGUE_FIXTURE_STATUS_COMPLETE_BIT = 0x1
LEAGUE_FIXTURE_SCORE_LEFT_OFFSET = 0x3C
LEAGUE_FIXTURE_SCORE_RIGHT_OFFSET = 0x3E
LEAGUE_FIXTURE_STATUS_OFFSET = 0x44
LEAGUE_FIXTURE_DATE_ACCESSOR_VA = 0x510A20
LEAGUE_FIXTURE_SCORE_LEFT_ACCESSOR_VA = 0x513E70
LEAGUE_FIXTURE_SCORE_RIGHT_ACCESSOR_VA = 0x513E80
LEAGUE_FIXTURE_RESULT_COPY_VA = 0x5112A0
LEAGUE_FIXTURE_COMPLETION_VA = 0x511370
LEAGUE_FIXTURE_SCORE_FORMAT_VA = 0x81C504
LEAGUE_FIXTURE_SCORE_FORMAT = "%i:%i"
LEAGUE_FIXTURE_DATE_FORMAT_VA = 0x81C4F8
LEAGUE_FIXTURE_DATE_FORMAT = "%02i.%02i"
LEAGUE_FIXTURES_SELECTED_INDEX_OLD_OFFSET = 0x109B0
LEAGUE_FIXTURES_SELECTED_INDEX_CURRENT_OFFSET = 0x109B4

# Recovery 153: source-proven PLeagueFixtures matrix/header contract.
LEAGUE_FIXTURES_MATRIX_BUILD_VA = 0x46D950
LEAGUE_FIXTURES_MEMBER_PREPARE_VA = 0x4F4940
LEAGUE_FIXTURES_LAYER_HELPER_VA = 0x616F40
LEAGUE_FIXTURES_GRID_OBJECT_OFFSET = 0x1CF0
LEAGUE_FIXTURES_GRID_VFTABLE_VA = 0x7C23D0
LEAGUE_FIXTURES_GRID_OUTER_PANEL_OFFSET = 0x2C
LEAGUE_FIXTURES_CLUB_TEXT_VFTABLE_VA = 0x7C25C0
LEAGUE_FIXTURES_CLUB_TEXT_SETTER_VA = 0x5D5490
LEAGUE_FIXTURES_CLUB_TEXT_IDENTITY_OFFSET = 0x48
LEAGUE_FIXTURES_COLUMN_CLUB_TEXT_OFFSET = 0x9A0
LEAGUE_FIXTURES_ROW_CLUB_TEXT_OFFSET = 0x15D0
LEAGUE_FIXTURES_CLUB_TEXT_STRIDE = 0x4C
LEAGUE_FIXTURES_MATRIX_POINTER_OFFSET = 0xA0
LEAGUE_FIXTURES_COLUMN_WINDOW_OFFSET = 0xA4
LEAGUE_FIXTURES_MATRIX_MEMBER_INDEX_OFFSET = 0x2A0
LEAGUE_FIXTURES_GLOBAL_FIXTURE_BUCKETS_VA = 0x947AD8
LEAGUE_FIXTURES_GLOBAL_FIXTURE_BUCKET_BYTES = 0x5D4
LEAGUE_FIXTURES_GLOBAL_FIXTURE_BUCKET_COUNT = (
    LEAGUE_FIXTURES_GLOBAL_FIXTURE_BUCKET_BYTES // 4
)
LEAGUE_FIXTURE_MATRIX_KIND_CODE = 1
LEAGUE_FIXTURE_MATRIX_EXCLUDED_STATUS_BIT = 0x20
LEAGUE_FIXTURE_MATRIX_COMPETITION_OFFSET = 0x4C
LEAGUE_FIXTURE_MATRIX_LEFT_SIDE_OFFSET = 0x14
LEAGUE_FIXTURE_MATRIX_RIGHT_SIDE_OFFSET = 0x28
LEAGUE_FIXTURES_VISIBLE_COLUMNS = 12
LEAGUE_FIXTURES_VISIBLE_ROWS = 24
LEAGUE_FIXTURES_COLUMN_PAGE_STEP = 12
LEAGUE_FIXTURES_COLUMN_PIXEL_STEP = 29
LEAGUE_FIXTURES_ROW_PIXEL_STEP = 14
LEAGUE_FIXTURES_GRID_POINT_SELECT_VA = 0x46D300
LEAGUE_FIXTURES_GRID_POINT_FIXTURE_ACTION_VA = 0x46D390
LEAGUE_FIXTURES_GRID_POINT_COMPLETION_QUERY_VA = 0x46D400
LEAGUE_FIXTURES_CELL_FIXTURE_ACTION_TARGET_VA = 0x488C80
LEAGUE_FIXTURES_MATCH_INFO_CLASS = "PMatchInfo"
LEAGUE_FIXTURES_MATCH_INFO_TYPE_DESCRIPTOR_VA = 0x81D058
LEAGUE_FIXTURES_MATCH_INFO_VFTABLE_VA = 0x7C41D4
LEAGUE_FIXTURES_MATCH_INFO_CONSTRUCTOR_VA = 0x487580
LEAGUE_FIXTURES_MATCH_INFO_ALLOC_SIZE = 0x1828
LEAGUE_FIXTURES_MATCH_INFO_BASE_CLASS = "PExplodingDialog"
LEAGUE_FIXTURES_MATCH_INFO_BASE_TYPE_DESCRIPTOR_VA = 0x81BB38
LEAGUE_FIXTURES_MATCH_INFO_BASE_VFTABLE_VA = 0x7C0D54
LEAGUE_FIXTURES_MATCH_INFO_FIXTURE_CONTEXT_VCALL_SLOT = 0x18
LEAGUE_FIXTURES_MATCH_INFO_LINK_INDEX_OFFSET = 0x40
LEAGUE_FIXTURES_MATCH_INFO_LINK_ROOT_GLOBAL_VA = 0x8755F8
LEAGUE_FIXTURES_MATCH_INFO_PRIMARY_CONTEXT_OFFSET = 0x70
LEAGUE_FIXTURES_MATCH_INFO_SECONDARY_CONTEXT_OFFSET = 0x74
LEAGUE_FIXTURES_MATCH_INFO_LAYOUT_HELPER_VA = 0x653320
LEAGUE_FIXTURES_MATCH_INFO_SIZE = (760, 500)

LEAGUE_FIXTURES_SELECTOR_SETUP_VA = 0x46AA70
LEAGUE_FIXTURES_LEAGUE_REBUILD_VA = 0x46D840
LEAGUE_FIXTURES_EVENT_DISPATCH_VA = 0x46E040
LEAGUE_FIXTURES_ACTIVE_COUNTRY_INDEX_OFFSET = 0x64
LEAGUE_FIXTURES_SELECTED_LEAGUE_INDEX_BASE_OFFSET = 0x68
LEAGUE_FIXTURES_SELECTED_LEAGUE_INDEX_COUNT = 8
LEAGUE_FIXTURES_LEAGUE_POINTER_BASE_OFFSET = 0x88
LEAGUE_FIXTURES_COUNTRY_ID_BASE_OFFSET = 0xF0
LEAGUE_FIXTURES_COUNTRY_CONTROL_BASE_OFFSET = 0x110
LEAGUE_FIXTURES_LEAGUE_CONTROL_BASE_OFFSET = 0x3B8
LEAGUE_FIXTURES_SELECTOR_CONTROL_STRIDE = 0x4C
LEAGUE_FIXTURES_COUNTRY_SELECTOR_COUNT = 8
LEAGUE_FIXTURES_LEAGUE_SELECTOR_COUNT = 6
LEAGUE_FIXTURES_COUNTRY_EVENT_FIRST = 1
LEAGUE_FIXTURES_LEAGUE_EVENT_FIRST = 9
LEAGUE_FIXTURES_SELECTOR_CLASS = "fmRadioTextSm@fm2001_ctrls"
LEAGUE_FIXTURES_SELECTOR_VFTABLE_VA = 0x7D6AB8
LEAGUE_FIXTURES_SELECTOR_CONSTRUCTOR_VA = 0x5D4B50
LEAGUE_FIXTURES_SELECTOR_OWNER_BIND_VA = 0x5D48C0
LEAGUE_FIXTURES_SELECTOR_SETUP_CONTROL_VA = 0x5D4C70
LEAGUE_FIXTURES_SELECTOR_SET_TEXT_VA = 0x5D3F10
LEAGUE_FIXTURES_LEAGUE_BASE_TYPE_DESCRIPTOR_VA = 0x818AA0
LEAGUE_FIXTURES_LEAGUE_TYPE_DESCRIPTOR_VA = 0x818978
LEAGUE_FIXTURES_RTDYNAMICCAST_VA = 0x668995
LEAGUE_FIXTURES_COUNTRY_COMPETITION_COUNT_OFFSET = 0x4C
LEAGUE_FIXTURES_COUNTRY_COMPETITION_ARRAY_OFFSET = 0x48
LEAGUE_FIXTURES_LEAGUE_CAPTION_OFFSET = 0x14
LEAGUE_FIXTURES_CURRENT_CLUB_COMPETITION_ID_OFFSET = 0x10
LEAGUE_FIXTURES_CURRENT_CLUB_COUNTRY_ID_OFFSET = 0x14
LEAGUE_FIXTURES_COMPETITION_ID_RESOLVE_VA = 0x4056F0
LEAGUE_FIXTURES_COUNTRY_COMPETITION_INDEX_VA = 0x410FF0



@dataclass(frozen=True)
class LeagueFixturesMatchInfoAction:
    action_va: int
    panel_class: str
    constructor_va: int
    vftable_va: int
    allocation_size: int
    size: tuple[int, int]
    primary_context_offset: int
    secondary_context_offset: int


LEAGUE_FIXTURES_MATCH_INFO_ACTION = LeagueFixturesMatchInfoAction(
    action_va=LEAGUE_FIXTURES_CELL_FIXTURE_ACTION_TARGET_VA,
    panel_class=LEAGUE_FIXTURES_MATCH_INFO_CLASS,
    constructor_va=LEAGUE_FIXTURES_MATCH_INFO_CONSTRUCTOR_VA,
    vftable_va=LEAGUE_FIXTURES_MATCH_INFO_VFTABLE_VA,
    allocation_size=LEAGUE_FIXTURES_MATCH_INFO_ALLOC_SIZE,
    size=LEAGUE_FIXTURES_MATCH_INFO_SIZE,
    primary_context_offset=LEAGUE_FIXTURES_MATCH_INFO_PRIMARY_CONTEXT_OFFSET,
    secondary_context_offset=LEAGUE_FIXTURES_MATCH_INFO_SECONDARY_CONTEXT_OFFSET,
)


def league_fixtures_match_info_action(
    *,
    fixture_present: bool,
    linked_context_available: bool,
) -> LeagueFixturesMatchInfoAction | None:
    """Mirror the two fail-closed gates before PMatchInfo is opened.

    PLeagueGrid::0x46D390 never calls 0x488C80 for a null matrix fixture.
    0x488C80 then resolves a linked context from the fixture-derived object's
    +0x40 index and returns without constructing PMatchInfo when that resolution
    fails.
    """
    if type(fixture_present) is not bool:
        raise OriginalLeagueFixturesResourceError("fixture_present must be boolean")
    if type(linked_context_available) is not bool:
        raise OriginalLeagueFixturesResourceError(
            "linked_context_available must be boolean"
        )
    if not fixture_present or not linked_context_available:
        return None
    return LEAGUE_FIXTURES_MATCH_INFO_ACTION


@dataclass(frozen=True)
class LeagueFixturesCountrySelector:
    index: int
    country_id: int
    caption: str
    event_id: int
    control_offset: int
    country_id_offset: int
    selected_league_index_offset: int


@dataclass(frozen=True)
class LeagueFixturesLeagueSelector:
    index: int
    league_identity: int
    caption: str
    event_id: int
    control_offset: int
    selected: bool


LEAGUE_FIXTURES_COUNTRY_SELECTORS = (
    LeagueFixturesCountrySelector(0, 26, "England", 1, 0x110, 0xF0, 0x68),
    LeagueFixturesCountrySelector(1, 33, "Germany", 2, 0x15C, 0xF4, 0x6C),
    LeagueFixturesCountrySelector(2, 40, "Italy", 3, 0x1A8, 0xF8, 0x70),
    LeagueFixturesCountrySelector(3, 73, "Spain", 4, 0x1F4, 0xFC, 0x74),
    LeagueFixturesCountrySelector(4, 66, "Scotland", 5, 0x240, 0x100, 0x78),
    LeagueFixturesCountrySelector(5, 31, "France", 6, 0x28C, 0x104, 0x7C),
    LeagueFixturesCountrySelector(6, 24, "Holland", 7, 0x2D8, 0x108, 0x80),
    LeagueFixturesCountrySelector(7, 9, "Belgium", 8, 0x324, 0x10C, 0x84),
)


def league_fixtures_country_selector_for_club_country(
    country_id: int,
) -> LeagueFixturesCountrySelector:
    """Return the source country selector matching the current user's club."""
    if type(country_id) is not int or country_id < 0:
        raise OriginalLeagueFixturesResourceError(
            "current club country ID must be a non-negative integer"
        )
    for selector in LEAGUE_FIXTURES_COUNTRY_SELECTORS:
        if selector.country_id == country_id:
            return selector
    raise OriginalLeagueFixturesResourceError(
        "current club country is outside the eight source League Fixtures selectors"
    )


def league_fixtures_selected_league_index(
    current_league_identity: int,
    league_identities: tuple[int, ...] | list[int],
) -> int:
    """Mirror country competition-index lookup 0x410FF0, fail-closed on -1."""
    if type(current_league_identity) is not int or current_league_identity < 0:
        raise OriginalLeagueFixturesResourceError(
            "current league identity must be a non-negative integer"
        )
    normalized = tuple(league_identities)
    if not normalized or len(normalized) > LEAGUE_FIXTURES_LEAGUE_SELECTOR_COUNT:
        raise OriginalLeagueFixturesResourceError(
            "League Fixtures requires between one and six source League entries"
        )
    for value in normalized:
        if type(value) is not int or value < 0:
            raise OriginalLeagueFixturesResourceError(
                "source League identities must be non-negative integers"
            )
    try:
        return normalized.index(current_league_identity)
    except ValueError as exc:
        raise OriginalLeagueFixturesResourceError(
            "current league is absent from the selected country's source League list"
        ) from exc


def league_fixtures_league_selectors(
    leagues: tuple[tuple[int, str], ...] | list[tuple[int, str]],
    *,
    selected_index: int,
) -> tuple[LeagueFixturesLeagueSelector, ...]:
    """Build the exact visible League radio list used by 0x46D840.

    The original country competition array is LeagueBase*. 0x46D840
    dynamically casts entries to League and exposes at most the six source
    radio controls. The clean-room seam receives only those already-proven
    League identities/captions and fails closed outside that bound.
    """
    normalized = tuple(leagues)
    if not normalized or len(normalized) > LEAGUE_FIXTURES_LEAGUE_SELECTOR_COUNT:
        raise OriginalLeagueFixturesResourceError(
            "League Fixtures requires between one and six source League entries"
        )
    if type(selected_index) is not int or not 0 <= selected_index < len(normalized):
        raise OriginalLeagueFixturesResourceError(
            "selected League index is outside the visible source League list"
        )

    result = []
    seen: set[int] = set()
    for index, item in enumerate(normalized):
        if (
            not isinstance(item, tuple)
            or len(item) != 2
            or type(item[0]) is not int
            or item[0] < 0
            or not isinstance(item[1], str)
            or not item[1]
        ):
            raise OriginalLeagueFixturesResourceError(
                "each source League entry must be (non-negative identity, non-empty caption)"
            )
        identity, caption = item
        if identity in seen:
            raise OriginalLeagueFixturesResourceError(
                "source League identities must be unique"
            )
        seen.add(identity)
        result.append(
            LeagueFixturesLeagueSelector(
                index=index,
                league_identity=identity,
                caption=caption,
                event_id=LEAGUE_FIXTURES_LEAGUE_EVENT_FIRST + index,
                control_offset=(
                    LEAGUE_FIXTURES_LEAGUE_CONTROL_BASE_OFFSET
                    + LEAGUE_FIXTURES_SELECTOR_CONTROL_STRIDE * index
                ),
                selected=index == selected_index,
            )
        )
    return tuple(result)


def league_fixtures_selector_event(event_id: int) -> tuple[str, int]:
    """Map exact PLeagueFixtures radio events 1..14 to source selector indices."""
    if type(event_id) is not int:
        raise OriginalLeagueFixturesResourceError("selector event ID must be an integer")
    if LEAGUE_FIXTURES_COUNTRY_EVENT_FIRST <= event_id < (
        LEAGUE_FIXTURES_COUNTRY_EVENT_FIRST + LEAGUE_FIXTURES_COUNTRY_SELECTOR_COUNT
    ):
        return ("country", event_id - LEAGUE_FIXTURES_COUNTRY_EVENT_FIRST)
    if LEAGUE_FIXTURES_LEAGUE_EVENT_FIRST <= event_id < (
        LEAGUE_FIXTURES_LEAGUE_EVENT_FIRST + LEAGUE_FIXTURES_LEAGUE_SELECTOR_COUNT
    ):
        return ("league", event_id - LEAGUE_FIXTURES_LEAGUE_EVENT_FIRST)
    raise OriginalLeagueFixturesResourceError(
        "event ID is not a League Fixtures country/League selector"
    )


def league_fixture_empty_slot_is_self_match(
    row_club_identity: int,
    column_club_identity: int,
) -> bool:
    """Return the exact empty-slot red predicate from PLeagueGrid.

    Recovery 153 proves both compared values are ClubText+0x48 club identities
    populated by 0x5D5490 from the same selected competition member list.
    Pointer equality in the original therefore means the row and column refer
    to the same club: the impossible self-fixture diagonal.
    """
    for label, value in (
        ("row_club_identity", row_club_identity),
        ("column_club_identity", column_club_identity),
    ):
        if type(value) is not int or value < 0:
            raise OriginalLeagueFixturesResourceError(
                f"{label} must be a non-negative canonical club identity"
            )
    return row_club_identity == column_club_identity


def league_fixture_matrix_accepts_candidate(
    *,
    kind_code: int,
    fixture_competition_identity: int,
    selected_competition_identity: int,
    fixture_status_bits: int,
    left_club_identity: int | None,
    right_club_identity: int | None,
) -> bool:
    """Mirror the fail-closed fixture filters in PLeagueFixtures::0x46D950."""
    for label, value in (
        ("kind_code", kind_code),
        ("fixture_competition_identity", fixture_competition_identity),
        ("selected_competition_identity", selected_competition_identity),
        ("fixture_status_bits", fixture_status_bits),
    ):
        if type(value) is not int or value < 0:
            raise OriginalLeagueFixturesResourceError(
                f"{label} must be a non-negative integer"
            )
    for label, value in (
        ("left_club_identity", left_club_identity),
        ("right_club_identity", right_club_identity),
    ):
        if value is not None and (type(value) is not int or value < 0):
            raise OriginalLeagueFixturesResourceError(
                f"{label} must be None or a non-negative canonical club identity"
            )

    return (
        kind_code == LEAGUE_FIXTURE_MATRIX_KIND_CODE
        and fixture_competition_identity == selected_competition_identity
        and not fixture_status_bits & LEAGUE_FIXTURE_MATRIX_EXCLUDED_STATUS_BIT
        and left_club_identity is not None
        and right_club_identity is not None
    )


def league_fixture_matrix_layer_count_from_helper_result(helper_result: int) -> int:
    """Mirror 0x46D985..0x46D98F: signed helper result divided by two.

    The source-selected competitions observed by this path provide a
    non-negative helper result; invalid negative values are rejected rather
    than extrapolated.
    """
    if type(helper_result) is not int or helper_result < 0:
        raise OriginalLeagueFixturesResourceError(
            "matrix layer helper result must be a non-negative integer"
        )
    return helper_result // 2


def league_fixture_matrix_slot(
    *,
    club_count: int,
    left_member_index: int,
    right_member_index: int,
    repeat_layer: int = 0,
) -> int:
    """Return the exact N*N layer-major matrix slot used by 0x46D950."""
    for label, value in (
        ("club_count", club_count),
        ("left_member_index", left_member_index),
        ("right_member_index", right_member_index),
        ("repeat_layer", repeat_layer),
    ):
        if type(value) is not int:
            raise OriginalLeagueFixturesResourceError(f"{label} must be an integer")
    if club_count <= 0:
        raise OriginalLeagueFixturesResourceError("club_count must be positive")
    if not 0 <= left_member_index < club_count:
        raise OriginalLeagueFixturesResourceError("left_member_index is outside club_count")
    if not 0 <= right_member_index < club_count:
        raise OriginalLeagueFixturesResourceError("right_member_index is outside club_count")
    if repeat_layer < 0:
        raise OriginalLeagueFixturesResourceError("repeat_layer must be non-negative")
    return (
        repeat_layer * club_count * club_count
        + left_member_index * club_count
        + right_member_index
    )


def league_fixture_first_free_repeat_slot(
    occupied: tuple[bool, ...] | list[bool],
    *,
    club_count: int,
    left_member_index: int,
    right_member_index: int,
    layer_count: int,
) -> int:
    """Mirror the source's N*N stepping for repeated same-pair fixtures."""
    if type(layer_count) is not int or layer_count <= 0:
        raise OriginalLeagueFixturesResourceError("layer_count must be positive")
    required = club_count * club_count * layer_count
    if len(occupied) != required:
        raise OriginalLeagueFixturesResourceError(
            "occupied matrix length does not match club_count and layer_count"
        )
    for layer in range(layer_count):
        slot = league_fixture_matrix_slot(
            club_count=club_count,
            left_member_index=left_member_index,
            right_member_index=right_member_index,
            repeat_layer=layer,
        )
        if not occupied[slot]:
            return slot
    raise OriginalLeagueFixturesResourceError(
        "all source-allocated repeat layers are already occupied"
    )


def league_fixtures_column_page_offset(
    current_offset: int,
    club_count: int,
    direction: int,
) -> int:
    """Mirror the reachable +/-12 column paging behavior at 0x46E489/0x46E4AB."""
    for label, value in (("current_offset", current_offset), ("club_count", club_count)):
        if type(value) is not int:
            raise OriginalLeagueFixturesResourceError(f"{label} must be an integer")
    if club_count < 0:
        raise OriginalLeagueFixturesResourceError("club_count must be non-negative")
    max_offset = max(0, club_count - LEAGUE_FIXTURES_VISIBLE_COLUMNS)
    if not 0 <= current_offset <= max_offset:
        raise OriginalLeagueFixturesResourceError(
            "current_offset is outside the source-reachable column window"
        )
    if direction not in (-1, 1):
        raise OriginalLeagueFixturesResourceError("direction must be -1 or 1")
    if direction < 0:
        return max(0, current_offset - LEAGUE_FIXTURES_COLUMN_PAGE_STEP)
    return min(max_offset, current_offset + LEAGUE_FIXTURES_COLUMN_PAGE_STEP)


def league_fixtures_grid_indices_from_point(
    *,
    x: int,
    y: int,
    origin_x: int,
    origin_y: int,
) -> tuple[int, int]:
    """Mirror the valid in-grid coordinate reduction in 0x46D300/390/400."""
    for label, value in (
        ("x", x),
        ("y", y),
        ("origin_x", origin_x),
        ("origin_y", origin_y),
    ):
        if type(value) is not int:
            raise OriginalLeagueFixturesResourceError(f"{label} must be an integer")
    dx = x - origin_x
    dy = y - origin_y
    if dx < 0 or dy < 0:
        raise OriginalLeagueFixturesResourceError(
            "point precedes the source grid origin"
        )
    column = dx // LEAGUE_FIXTURES_COLUMN_PIXEL_STEP
    row = dy // LEAGUE_FIXTURES_ROW_PIXEL_STEP
    validate_league_fixtures_grid_selection_index(column, axis="column")
    validate_league_fixtures_grid_selection_index(row, axis="row")
    return column, row


def validate_league_fixtures_grid_selection_index(index: int, *, axis: str) -> int:
    """Validate the exact visible selector ranges routed by the panel dispatcher."""
    if type(index) is not int:
        raise OriginalLeagueFixturesResourceError("grid selection index must be an integer")
    if axis == "column":
        limit = LEAGUE_FIXTURES_VISIBLE_COLUMNS
    elif axis == "row":
        limit = LEAGUE_FIXTURES_VISIBLE_ROWS
    else:
        raise OriginalLeagueFixturesResourceError("axis must be 'column' or 'row'")
    if not 0 <= index < limit:
        raise OriginalLeagueFixturesResourceError(
            f"{axis} selection index must be in 0..{limit - 1}"
        )
    return index


def league_fixture_base_box(
    *,
    fixture_present: bool,
    fixture_status_bits: int = 0,
    empty_slot_same_club: bool = False,
) -> OriginalLeagueFixturesResource:
    """Mirror the base box-selection rules in the recovered row/update paths.

    For a populated fixture, status bit 0 selects the completed score-display
    path and its original played_fixtures_box; otherwise the date path uses
    date_fixtures_box. For an empty slot, Recovery 153 proves the source
    boolean is row-club == column-club, marking the impossible self-fixture
    diagonal red while other empty slots retain date_fixtures_box.
    """
    if type(fixture_present) is not bool:
        raise OriginalLeagueFixturesResourceError("fixture_present must be boolean")
    if type(fixture_status_bits) is not int or fixture_status_bits < 0:
        raise OriginalLeagueFixturesResourceError(
            "fixture_status_bits must be a non-negative integer"
        )
    if type(empty_slot_same_club) is not bool:
        raise OriginalLeagueFixturesResourceError(
            "empty_slot_same_club must be boolean"
        )
    if fixture_present:
        return (
            PLAYED_FIXTURES_BOX
            if fixture_status_bits & LEAGUE_FIXTURE_STATUS_COMPLETE_BIT
            else DATE_FIXTURES_BOX
        )
    return RED_FIXTURES_BOX if empty_slot_same_club else DATE_FIXTURES_BOX


def league_fixture_box_for_cell(
    *,
    fixture_present: bool,
    fixture_status_bits: int = 0,
    empty_slot_same_club: bool = False,
    selected: bool = False,
) -> OriginalLeagueFixturesResource:
    """Apply the source-proven selected-cell overlay after the base box rule."""
    if type(selected) is not bool:
        raise OriginalLeagueFixturesResourceError("selected must be boolean")
    if selected:
        return TOGGLED_FIXTURES_BOX
    return league_fixture_base_box(
        fixture_present=fixture_present,
        fixture_status_bits=fixture_status_bits,
        empty_slot_same_club=empty_slot_same_club,
    )


def league_fixture_visible_text(
    *,
    fixture_status_bits: int,
    score_left: int | None = None,
    score_right: int | None = None,
    date_day: int | None = None,
    date_month: int | None = None,
) -> str:
    """Mirror the two source format strings selected by fixture status bit 0."""
    if type(fixture_status_bits) is not int or fixture_status_bits < 0:
        raise OriginalLeagueFixturesResourceError(
            "fixture_status_bits must be a non-negative integer"
        )
    if fixture_status_bits & LEAGUE_FIXTURE_STATUS_COMPLETE_BIT:
        if type(score_left) is not int or type(score_right) is not int:
            raise OriginalLeagueFixturesResourceError(
                "completed fixture text requires integer score fields"
            )
        return f"{score_left}:{score_right}"
    if type(date_day) is not int or type(date_month) is not int:
        raise OriginalLeagueFixturesResourceError(
            "scheduled fixture text requires integer day/month fields"
        )
    return f"{date_day:02d}.{date_month:02d}"



def validate_original_league_fixtures_resources(
    source_root: Path,
) -> tuple[OriginalLeagueFixturesResource, ...]:
    """Require every exact source-correlated League Fixtures graphic."""
    root = Path(source_root)
    for resource in LEAGUE_FIXTURES_RESOURCES:
        path = root / resource.source_path
        try:
            data = path.read_bytes()
        except FileNotFoundError as exc:
            raise OriginalLeagueFixturesResourceError(
                f"Missing original League Fixtures resource: {resource.source_path}"
            ) from exc
        if len(data) != resource.byte_size:
            raise OriginalLeagueFixturesResourceError(
                f"League Fixtures byte-size mismatch: {resource.source_path}"
            )
        if sha256(data).hexdigest() != resource.sha256:
            raise OriginalLeagueFixturesResourceError(
                f"League Fixtures checksum mismatch: {resource.source_path}"
            )
        header = parse_ea444_header(data)
        if (header.width, header.height) != resource.size:
            raise OriginalLeagueFixturesResourceError(
                f"League Fixtures geometry mismatch: {resource.source_path}"
            )
    return LEAGUE_FIXTURES_RESOURCES


def assert_league_fixtures_panel_identity() -> None:
    if LEAGUE_FIXTURES_PANEL.panel_class != "PLeagueFixtures":
        raise OriginalLeagueFixturesResourceError(
            "League Fixtures resources require the source-proven PLeagueFixtures panel"
        )
