"""Source-bounded FastViewTeam::TeamTable row-bar geometry.

Recovery 197 corrects the earlier assumption that the three 82x16 FastView bar
images belonged to PossessionFigures. Canonical RTTI plus the
0x524A20 -> 0x524EC0 -> 0x525DB0 constructor chain proves they belong to the
two FastViewTeam TeamTable row families.

This module preserves only exact geometry/resource pairing. The higher-level
meaning of the dynamic width update at 0x526680 remains deliberately neutral.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import struct


FASTVIEW_TEAM_CONSTRUCTOR_VA = 0x524A20
FASTVIEW_TEAM_VFTABLE_VA = 0x7CA888
FASTVIEW_TEAM_TYPE_DESCRIPTOR_VA = 0x8299D8

TEAMTABLE_CONSTRUCTOR_VA = 0x524EC0
TEAMTABLE_VFTABLE_VA = 0x7CA950
TEAMTABLE_TYPE_DESCRIPTOR_VA = 0x829B50

TEAMTABLE_ROW_CONSTRUCTOR_VA = 0x525DB0
TEAMTABLE_ROW_VFTABLE_VA = 0x7CA968
TEAMTABLE_ROW_TYPE_DESCRIPTOR_VA = 0x829A78
TEAMTABLE_ROW_DYNAMIC_BAR_UPDATE_VA = 0x526680

TEAM_BAR_1_PATH = "FM2001_Art/FastView/team_bar_1.444"
BLANK_BAR_PATH = "FM2001_Art/FastView/blank_bar.444"
TEAM_BAR_2_PATH = "FM2001_Art/FastView/team_bar_2.444"
TEAMTABLE_BAR_IMPORT_ROOT = Path("original_assets/source")


@dataclass(frozen=True)
class TeamTableBarResource:
    source_path: str
    byte_size: int
    sha256: str


TEAMTABLE_BAR_RESOURCES = (
    TeamTableBarResource(
        TEAM_BAR_1_PATH,
        2344,
        "edd35c18a53598b3cfd3e93adc2b27153742582d7888a0923fdd672d36e2681d",
    ),
    TeamTableBarResource(
        BLANK_BAR_PATH,
        2776,
        "961eb49ae0810a522130f4b6e7401c7d16250d0de65bc7e51bc8341c6b8a7e3a",
    ),
    TeamTableBarResource(
        TEAM_BAR_2_PATH,
        2312,
        "4514b621f8d6a7b41c82c5215c4a1af571f60d773f0a3d1ea095c87d62e8a751",
    ),
)

TEAMTABLE_ROW_COUNT = 11
TEAMTABLE_ROW_STEP = 17
TEAMTABLE_BAR_WIDTH = 82
TEAMTABLE_BAR_HEIGHT = 16
TEAMTABLE_FIRST_ROW_Y = 27
TEAMTABLE_SIDE0_BAR_X = 309
TEAMTABLE_SIDE1_BAR_X = 409

TEAMTABLE_ROW_DYNAMIC_CONTROL_OFFSET = 0x38
TEAMTABLE_ROW_PAIRED_CONTROL_OFFSET = 0x3C
TEAMTABLE_ROW_SIDE_FLAG_OFFSET = 0x40


class FastViewTeamTableError(ValueError):
    pass


@dataclass(frozen=True)
class TeamTableBarPair:
    side_index: int
    row_index: int
    rect: tuple[int, int, int, int]
    dynamic_resource_path: str
    paired_resource_path: str
    dynamic_control_offset: int = TEAMTABLE_ROW_DYNAMIC_CONTROL_OFFSET
    paired_control_offset: int = TEAMTABLE_ROW_PAIRED_CONTROL_OFFSET


def teamtable_bar_pair(side_index: int, row_index: int) -> TeamTableBarPair:
    """Return the exact overlaid bar pair for one source TeamTable row."""
    if type(side_index) is not int or side_index not in (0, 1):
        raise FastViewTeamTableError("TeamTable side index must be 0 or 1")
    if type(row_index) is not int or not 0 <= row_index < TEAMTABLE_ROW_COUNT:
        raise FastViewTeamTableError(
            f"TeamTable row index must be in 0..{TEAMTABLE_ROW_COUNT - 1}"
        )

    x0 = TEAMTABLE_SIDE0_BAR_X if side_index == 0 else TEAMTABLE_SIDE1_BAR_X
    y0 = TEAMTABLE_FIRST_ROW_Y + TEAMTABLE_ROW_STEP * row_index
    rect = (x0, y0, x0 + TEAMTABLE_BAR_WIDTH, y0 + TEAMTABLE_BAR_HEIGHT)

    # Row constructor 0x525DB0 creates the original fourth string at object+0x3c
    # and the original third string at object+0x38.  FastViewTeam 0x524A20
    # supplies [team_bar_1, blank_bar] for side 0 and
    # [blank_bar, team_bar_2] for side 1.
    if side_index == 0:
        dynamic_path = TEAM_BAR_1_PATH
        paired_path = BLANK_BAR_PATH
    else:
        dynamic_path = BLANK_BAR_PATH
        paired_path = TEAM_BAR_2_PATH

    return TeamTableBarPair(
        side_index=side_index,
        row_index=row_index,
        rect=rect,
        dynamic_resource_path=dynamic_path,
        paired_resource_path=paired_path,
    )


def validate_imported_teamtable_bar_resources(
    repo_root: Path,
) -> tuple[TeamTableBarResource, ...]:
    """Require all three byte-identical 82x16 TeamTable bar originals."""
    for resource in TEAMTABLE_BAR_RESOURCES:
        path = Path(repo_root) / TEAMTABLE_BAR_IMPORT_ROOT / resource.source_path
        try:
            data = path.read_bytes()
        except FileNotFoundError as exc:
            raise FastViewTeamTableError(
                f"Missing staged FastView TeamTable bar: {resource.source_path}"
            ) from exc
        if len(data) != resource.byte_size:
            raise FastViewTeamTableError(
                f"FastView TeamTable bar byte-size mismatch: {resource.source_path}"
            )
        if sha256(data).hexdigest() != resource.sha256:
            raise FastViewTeamTableError(
                f"FastView TeamTable bar checksum mismatch: {resource.source_path}"
            )
        if len(data) < 4 or struct.unpack_from("<HH", data, 0) != (
            TEAMTABLE_BAR_WIDTH,
            TEAMTABLE_BAR_HEIGHT,
        ):
            raise FastViewTeamTableError(
                f"FastView TeamTable bar geometry mismatch: {resource.source_path}"
            )
    return TEAMTABLE_BAR_RESOURCES
