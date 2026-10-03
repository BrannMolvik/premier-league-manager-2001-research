"""Source-closed FastViewTeam / TeamTable row presentation.

Recovery 208 records only canonical executable/disc evidence for the two
side-indexed TeamTable instances and their nested Row controls. Asset pairing,
row geometry, text-control rectangles and the first-11/remaining name-grid
transition are exact. Higher-level row meanings remain deliberately unnamed.
"""
from __future__ import annotations

from dataclasses import dataclass


class FastViewTeamError(ValueError):
    pass


FASTVIEW_TEAM_CONSTRUCTOR_VA = 0x524920
FASTVIEW_TEAM_SETUP_VA = 0x524A20
FASTVIEW_TEAM_VFTABLE = 0x7CA888
TEAM_TABLE_CONSTRUCTOR_VA = 0x524EC0
TEAM_TABLE_VFTABLE = 0x7CA950
TEAM_ROW_CONSTRUCTOR_VA = 0x525DB0
TEAM_ROW_PRIMARY_VFTABLE = 0x7CA918

TEAM_ROW_EVENT_FORM_BASE_VFTABLE = 0x7CA938
TEAM_ROW_EVENT_FORM_FINAL_VFTABLE = 0x7CA90C
TEAM_ROW_EVENT_FORM_CALLBACK_VA = 0x526740
TEAM_ROW_EVENT_ENERGY_BASE_VFTABLE = 0x7CA92C
TEAM_ROW_EVENT_ENERGY_FINAL_VFTABLE = 0x7CA900
TEAM_ROW_EVENT_ENERGY_CALLBACK_VA = 0x5267D0
TEAM_ROW_EVENT_GOAL_BASE_VFTABLE = 0x7CA920
TEAM_ROW_EVENT_GOAL_FINAL_VFTABLE = 0x7CA8F4
TEAM_ROW_EVENT_GOAL_CALLBACK_VA = 0x526800
TEAM_ROW_EVENT_OWN_GOAL_BASE_VFTABLE = 0x7CA95C
TEAM_ROW_EVENT_OWN_GOAL_FINAL_VFTABLE = 0x7CA8E8
TEAM_ROW_EVENT_OWN_GOAL_CALLBACK_VA = 0x526880

TEAM_ROW_ENERGY_UPDATE_VA = 0x526680
TEAM_ROW_ENERGY_MIN = 58
TEAM_ROW_ENERGY_MAX = 99
TEAM_ROW_ENERGY_RANGE_INIT_VA = 0x51F330
TEAM_ROW_ENERGY_RANGE_GLOBAL_VA = 0x877754
TEAM_ROW_ENERGY_BAR_WIDTH = 82
TEAM_ROW_ENERGY_TRUNCATE_VA = 0x668350
TEAM_ROW_DYNAMIC_BAR_CONTROL_OFFSET = 0x38
TEAM_ROW_STATIC_BAR_CONTROL_OFFSET = 0x3C
TEAM_ROW_SIDE_INDEX_OFFSET = 0x40

TEAM_ROW_FORM_CONTROL_OFFSET = 0x34
TEAM_ROW_FORM_TEXT_INDEX = 5
TEAM_ROW_FORM_FORMAT = "%u"
TEAM_ROW_FORM_FORMAT_VA = 0x828D3C

TEAM_ROW_GOAL_COUNTER_OFFSET = 0x18
TEAM_ROW_GOAL_CONTROL_OFFSET = 0x2C
TEAM_ROW_GOAL_TEXT_INDEX = 3
TEAM_ROW_GOAL_FORMAT = "(%u)"
TEAM_ROW_GOAL_FORMAT_VA = 0x829B94
TEAM_ROW_OWN_GOAL_CHANGES_GOAL_CONTROL_NATIVE_COLOR = True

TEAM_ROW_PRIMARY_NAME_COUNT = 11
TEAM_ROW_STEP = 17

# Row constructor creates six generic text controls in this exact source order.
TEAM_ROW_TEXT_RAW_FLAGS = (0x24, 0x24, 0x21, 0x21, 0x21, 0x24)

# Side-indexed final rectangles at row index 0.
TEAM_SIDE_0_ROW_ORIGIN = (37, 27)
TEAM_SIDE_1_ROW_ORIGIN = (409, 27)
TEAM_SIDE_0_NAME_LOCAL_RECT = (0, 0, 259, 16)
TEAM_SIDE_1_NAME_LOCAL_RECT = (95, 0, 354, 16)
TEAM_SIDE_0_BAR_LOCAL_RECT = (272, 0, 354, 16)
TEAM_SIDE_1_BAR_LOCAL_RECT = (0, 0, 82, 16)

TEAM_SIDE_0_TEXT_LOCAL_RECTS = (
    (0, 0, 24, 16),
    (27, 0, 67, 16),
    (70, 0, 206, 16),
    (206, 0, 226, 16),
    (186, 0, 206, 16),
    (239, 0, 259, 16),
)
TEAM_SIDE_1_TEXT_LOCAL_RECTS = (
    (128, 0, 152, 16),
    (155, 0, 195, 16),
    (198, 0, 334, 16),
    (334, 0, 354, 16),
    (314, 0, 334, 16),
    (95, 0, 115, 16),
)


@dataclass(frozen=True)
class FastViewTeamResource:
    name: str
    source_path: str
    sha256: str
    byte_size: int
    size: tuple[int, int]
    path_literal_va: int
    imported: bool = False


TEAM_NAME_GRID_1 = FastViewTeamResource(
    "team_name_grid",
    "FM2001_Art/FastView/team_name_grid.444",
    "368f7c86ef07d9447af886b0a4d8857fa4a732d65f17913f72b2a9155e9a4d93",
    3496,
    (259, 16),
    0x829424,
)
TEAM_NAME_GRID_2 = FastViewTeamResource(
    "team_name_grid_2",
    "FM2001_Art/FastView/team_name_grid_2.444",
    "0cce4d1646afa3dd11da5f0db6b3a887ded8a6d647f39d998eaef8ffe5f71602",
    3512,
    (259, 16),
    0x8293F8,
)
TEAM_NAME_GRID_3 = FastViewTeamResource(
    "team_name_grid_3",
    "FM2001_Art/FastView/team_name_grid_3.444",
    "8deb413437234504cbb6c3a076b172304469d873f4e2df5fbedd314e5f22b095",
    3512,
    (259, 16),
    0x829384,
)
TEAM_NAME_GRID_4 = FastViewTeamResource(
    "team_name_grid_4",
    "FM2001_Art/FastView/team_name_grid_4.444",
    "6fc1446b5d65a07a5165fa0947282dfeb6b783d142ae9edc76f60dbd5cecd3e8",
    3496,
    (259, 16),
    0x829358,
)
TEAM_BAR_1 = FastViewTeamResource(
    "team_bar_1",
    "FM2001_Art/FastView/team_bar_1.444",
    "edd35c18a53598b3cfd3e93adc2b27153742582d7888a0923fdd672d36e2681d",
    2344,
    (82, 16),
    0x8293D4,
)
BLANK_BAR = FastViewTeamResource(
    "blank_bar",
    "FM2001_Art/FastView/blank_bar.444",
    "961eb49ae0810a522130f4b6e7401c7d16250d0de65bc7e51bc8341c6b8a7e3a",
    2776,
    (82, 16),
    0x8293B0,
)
TEAM_BAR_2 = FastViewTeamResource(
    "team_bar_2",
    "FM2001_Art/FastView/team_bar_2.444",
    "4514b621f8d6a7b41c82c5215c4a1af571f60d773f0a3d1ea095c87d62e8a751",
    2312,
    (82, 16),
    0x829334,
)


@dataclass(frozen=True)
class FastViewTeamSideContract:
    side_index: int
    row_origin: tuple[int, int]
    primary_name_grid: FastViewTeamResource
    alternate_name_grid: FastViewTeamResource
    bar_a: FastViewTeamResource
    bar_b: FastViewTeamResource
    name_local_rect: tuple[int, int, int, int]
    bar_local_rect: tuple[int, int, int, int]
    text_local_rects: tuple[tuple[int, int, int, int], ...]


SIDE_0_CONTRACT = FastViewTeamSideContract(
    0,
    TEAM_SIDE_0_ROW_ORIGIN,
    TEAM_NAME_GRID_1,
    TEAM_NAME_GRID_2,
    TEAM_BAR_1,
    BLANK_BAR,
    TEAM_SIDE_0_NAME_LOCAL_RECT,
    TEAM_SIDE_0_BAR_LOCAL_RECT,
    TEAM_SIDE_0_TEXT_LOCAL_RECTS,
)
SIDE_1_CONTRACT = FastViewTeamSideContract(
    1,
    TEAM_SIDE_1_ROW_ORIGIN,
    TEAM_NAME_GRID_3,
    TEAM_NAME_GRID_4,
    BLANK_BAR,
    TEAM_BAR_2,
    TEAM_SIDE_1_NAME_LOCAL_RECT,
    TEAM_SIDE_1_BAR_LOCAL_RECT,
    TEAM_SIDE_1_TEXT_LOCAL_RECTS,
)
TEAM_SIDE_CONTRACTS = (SIDE_0_CONTRACT, SIDE_1_CONTRACT)


def side_contract(side_index: int) -> FastViewTeamSideContract:
    if type(side_index) is not int or side_index not in (0, 1):
        raise FastViewTeamError("FastViewTeam side_index must be 0 or 1")
    return TEAM_SIDE_CONTRACTS[side_index]


def _translate(
    rect: tuple[int, int, int, int],
    origin: tuple[int, int],
) -> tuple[int, int, int, int]:
    left, top, right, bottom = rect
    x, y = origin
    return (x + left, y + top, x + right, y + bottom)


def team_row_origin(side_index: int, row_index: int) -> tuple[int, int]:
    contract = side_contract(side_index)
    if type(row_index) is not int or row_index < 0:
        raise FastViewTeamError("FastViewTeam row_index must be non-negative")
    return (
        contract.row_origin[0],
        contract.row_origin[1] + row_index * TEAM_ROW_STEP,
    )


def team_row_name_resource(side_index: int, row_index: int) -> FastViewTeamResource:
    contract = side_contract(side_index)
    if type(row_index) is not int or row_index < 0:
        raise FastViewTeamError("FastViewTeam row_index must be non-negative")
    return (
        contract.primary_name_grid
        if row_index < TEAM_ROW_PRIMARY_NAME_COUNT
        else contract.alternate_name_grid
    )


def team_row_rects(
    side_index: int,
    row_index: int,
) -> tuple[
    tuple[int, int, int, int],
    tuple[int, int, int, int],
    tuple[tuple[int, int, int, int], ...],
]:
    """Return exact final name-grid, shared bar, and generic text rectangles."""
    contract = side_contract(side_index)
    origin = team_row_origin(side_index, row_index)
    return (
        _translate(contract.name_local_rect, origin),
        _translate(contract.bar_local_rect, origin),
        tuple(_translate(rect, origin) for rect in contract.text_local_rects),
    )


@dataclass(frozen=True)
class FastViewEnergyBarState:
    side_index: int
    row_index: int
    energy: int
    normalized_extent_px: int
    static_resource: FastViewTeamResource
    dynamic_resource: FastViewTeamResource
    full_rect: tuple[int, int, int, int]
    dynamic_rect: tuple[int, int, int, int]


def team_row_energy_extent_px(energy: int) -> int:
    """Mirror 0x526680's clamped 58..99 -> 0..82 conversion.

    The source computes (energy - 58) / (99 - 58), clamps to [0,1],
    multiplies by 82 and truncates toward zero through 0x668350. Because the
    EventPlayerUpdateEnergy payload is integral, the bounded interior is
    exactly floor((energy - 58) * 82 / 41).
    """
    if type(energy) is not int or not 0 <= energy <= 0xFFFFFFFF:
        raise FastViewTeamError("EventPlayerUpdateEnergy value must fit uint32")
    if energy <= TEAM_ROW_ENERGY_MIN:
        return 0
    if energy >= TEAM_ROW_ENERGY_MAX:
        return TEAM_ROW_ENERGY_BAR_WIDTH
    return (
        (energy - TEAM_ROW_ENERGY_MIN) * TEAM_ROW_ENERGY_BAR_WIDTH
        // (TEAM_ROW_ENERGY_MAX - TEAM_ROW_ENERGY_MIN)
    )


def team_row_energy_bar_state(
    side_index: int,
    row_index: int,
    energy: int,
) -> FastViewEnergyBarState:
    """Return the exact two-layer energy-bar state for one PlayerRow.

    Row+0x3C is the full static bar-B picture. Row+0x38 is bar-A and is
    resized by EventPlayerUpdateEnergy. Side 0 grows bar-A from the left;
    side 1 uses blank_bar as bar-A and shrinks it from 82px to zero, revealing
    the full team_bar_2 layer from the right.
    """
    contract = side_contract(side_index)
    _, full_rect, _ = team_row_rects(side_index, row_index)
    extent = team_row_energy_extent_px(energy)
    left, top, right, bottom = full_rect
    dynamic_rect = (
        (left, top, left + extent, bottom)
        if side_index == 0
        else (left, top, right - extent, bottom)
    )
    return FastViewEnergyBarState(
        side_index=side_index,
        row_index=row_index,
        energy=energy,
        normalized_extent_px=extent,
        static_resource=contract.bar_b,
        dynamic_resource=contract.bar_a,
        full_rect=full_rect,
        dynamic_rect=dynamic_rect,
    )


def team_row_form_text(value: int) -> str:
    """Mirror EventPlayerUpdateForm's exact source %u text payload."""
    if type(value) is not int or not 0 <= value <= 0xFFFFFFFF:
        raise FastViewTeamError("EventPlayerUpdateForm value must fit uint32")
    return str(value)


def team_row_goal_count_after_event(previous_count: int) -> tuple[int, str]:
    """Mirror Goal/OwnGoal's shared increment then '(%u)' text update."""
    if type(previous_count) is not int or not 0 <= previous_count < 0xFFFFFFFF:
        raise FastViewTeamError("PlayerRow goal counter must fit incrementable uint32")
    count = previous_count + 1
    return count, f"({count})"


def team_row_named_event_text_rect(
    side_index: int,
    row_index: int,
    event_name: str,
) -> tuple[int, int, int, int]:
    """Return only text rectangles whose receiver semantics are source-named."""
    _, _, rects = team_row_rects(side_index, row_index)
    if event_name == "EventPlayerUpdateForm":
        return rects[TEAM_ROW_FORM_TEXT_INDEX]
    if event_name in {"EventPlayerGoal", "EventPlayerOwnGoal"}:
        return rects[TEAM_ROW_GOAL_TEXT_INDEX]
    raise FastViewTeamError("No source-named PlayerRow text rectangle for event")
