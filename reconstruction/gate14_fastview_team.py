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

PLAYER_ROW_FORM_RECEIVER_BASE_VFTABLE = 0x7CA938
PLAYER_ROW_ENERGY_RECEIVER_BASE_VFTABLE = 0x7CA92C
PLAYER_ROW_GOAL_RECEIVER_BASE_VFTABLE = 0x7CA920
PLAYER_ROW_OWN_GOAL_RECEIVER_BASE_VFTABLE = 0x7CA95C
PLAYER_ROW_FORM_RECEIVER_VFTABLE = 0x7CA90C
PLAYER_ROW_ENERGY_RECEIVER_VFTABLE = 0x7CA900
PLAYER_ROW_GOAL_RECEIVER_VFTABLE = 0x7CA8F4
PLAYER_ROW_OWN_GOAL_RECEIVER_VFTABLE = 0x7CA8E8

PLAYER_ROW_ENERGY_RECEIVER_OFFSET = 0x58
PLAYER_ROW_ENERGY_CALLBACK_VA = 0x5267D0
PLAYER_ROW_ENERGY_UPDATE_VA = 0x526680
PLAYER_ROW_ENERGY_EVENT_VALUE_OFFSET = 0x04
PLAYER_ROW_DYNAMIC_BAR_CONTROL_OFFSET = 0x38
PLAYER_ROW_SIDE_FLAG_OFFSET = 0x40
PLAYER_ROW_BAR_RECT_LEFT_OFFSET = 0x44
PLAYER_ROW_BAR_RECT_TOP_OFFSET = 0x48
PLAYER_ROW_BAR_RECT_RIGHT_OFFSET = 0x4C
PLAYER_ROW_BAR_RECT_BOTTOM_OFFSET = 0x50

PLAYER_ROW_ENERGY_MIN = 58
PLAYER_ROW_ENERGY_MAX = 99
PLAYER_ROW_ENERGY_SPAN = PLAYER_ROW_ENERGY_MAX - PLAYER_ROW_ENERGY_MIN
PLAYER_ROW_ENERGY_SPAN_GLOBAL_VA = 0x877754
PLAYER_ROW_ENERGY_SPAN_INIT_VA = 0x51F330
PLAYER_ROW_ENERGY_BAR_WIDTH = 82
PLAYER_ROW_ENERGY_BAR_WIDTH_FLOAT_VA = 0x7CA96C
PLAYER_ROW_FLOAT_TO_INT_VA = 0x668350

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
    dynamic_energy_bar: FastViewTeamResource
    static_energy_bar: FastViewTeamResource
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


@dataclass(frozen=True)
class FastViewEnergyBarState:
    side_index: int
    row_index: int
    energy_value: int
    source_scaled_width: int
    dynamic_resource: FastViewTeamResource
    static_resource: FastViewTeamResource
    full_rect: tuple[int, int, int, int]
    dynamic_rect: tuple[int, int, int, int]


def _source_energy_scaled_width(energy_value: int) -> int:
    """Mirror 0x526680's exact integer-equivalent x87 width transform.

    The source computes (energy - 58) / (99 - 58), clamps only values above
    1.0, multiplies by 82.0, then truncates toward zero via 0x668350.
    For integer EventPlayerUpdateEnergy values this is exactly
    2 * (energy - 58), with only the source upper clamp applied.
    """
    if type(energy_value) is not int:
        raise FastViewTeamError("EventPlayerUpdateEnergy value must be an integer")
    if energy_value > PLAYER_ROW_ENERGY_MAX:
        return PLAYER_ROW_ENERGY_BAR_WIDTH
    return 2 * (energy_value - PLAYER_ROW_ENERGY_MIN)


def team_row_energy_bar_state(
    side_index: int,
    row_index: int,
    energy_value: int,
) -> FastViewEnergyBarState:
    """Return the source rectangle rewritten by EventPlayerUpdateEnergy.

    PlayerRow's +0x58 receiver is RTTI-bound to EventPlayerUpdateEnergy.
    Callback 0x5267D0 forwards event+0x04 to 0x526680. The latter rewrites
    only the +0x38 PictureControl rectangle and mirrors the visual treatment:
    side 0 grows team_bar_1 over blank_bar, while side 1 shrinks blank_bar to
    reveal team_bar_2. Values below 58 are left mathematically unclamped because
    the executable itself does not clamp the lower side in this routine.
    """
    contract = side_contract(side_index)
    origin = team_row_origin(side_index, row_index)
    full_rect = _translate(contract.bar_local_rect, origin)
    left, top, right, bottom = full_rect
    width = _source_energy_scaled_width(energy_value)

    if side_index == 0:
        dynamic_right = left + width
    else:
        dynamic_right = left + PLAYER_ROW_ENERGY_BAR_WIDTH - width

    return FastViewEnergyBarState(
        side_index=side_index,
        row_index=row_index,
        energy_value=energy_value,
        source_scaled_width=width,
        dynamic_resource=contract.dynamic_energy_bar,
        static_resource=contract.static_energy_bar,
        full_rect=full_rect,
        dynamic_rect=(left, top, dynamic_right, bottom),
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
