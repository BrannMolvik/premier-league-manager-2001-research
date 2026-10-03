"""Source-closed FastViewLeagueScores current-fixture grid contract.

This module records the exact directly bound league-score grid whose ownership,
class method and owner-local rectangle are all recovered from the canonical
FM2001 executable. A second ScoreCompositeNormal grid is recorded as an
ownership-only lead until its layout descriptor is decoded.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import struct


class FastViewLeagueScoresError(ValueError):
    pass


SOURCE_FASTVIEW_LEAGUE_SCORES_PRIMARY_VFTABLE = 0x7CA750
SOURCE_FASTVIEW_LEAGUE_SCORES_SUBOBJECT_VFTABLE = 0x7CA744
SOURCE_FASTVIEW_LEAGUE_SCORES_RTTI = ".?AVFastViewLeagueScores@FastViewPanel@@"
SOURCE_FASTVIEW_LEAGUE_SCORES_SETUP_VA = 0x523370
SOURCE_FASTVIEW_LEAGUE_SCORES_CONSTRUCT_VFUNC_CALL_VA = 0x520D82

SOURCE_PICTURE_CONTROL_CONSTRUCTOR_VA = 0x527730

CURRENT_FIX_GRID_1_PATH = "FM2001_Art/FastView/current_fix_grid_1.444"
CURRENT_FIX_GRID_1_PATH_LITERAL_VA = 0x829920
CURRENT_FIX_GRID_1_STRING_INIT_VA = 0x5239AB
CURRENT_FIX_GRID_1_PICTURE_CONTROL_CALL_VA = 0x5239F3
CURRENT_FIX_GRID_1_BYTE_SIZE = 3704
CURRENT_FIX_GRID_1_SIZE = (309, 19)
CURRENT_FIX_GRID_1_OWNER_LOCAL_RECT = (38, 32, 347, 51)
CURRENT_FIX_GRID_1_SHA256 = (
    "bdd2fe25884e8ce72e21bd7b9296c65827ce90ea058c6f43e2f727f2bae19057"
)

# Ownership-only follow-on. Do not render until its layout descriptor is decoded.
CURRENT_FIX_GRID_2_PATH = "FM2001_Art/FastView/current_fix_grid_2.444"
CURRENT_FIX_GRID_2_PATH_LITERAL_VA = 0x828ED0
CURRENT_FIX_GRID_2_SCORE_COMPOSITE_NORMAL_CONSTRUCTOR_VA = 0x51B740
CURRENT_FIX_GRID_2_STRING_INIT_VA = 0x51B75D
CURRENT_FIX_GRID_2_SCORE_COMPOSITE_BASE_CALL_VA = 0x51B79A
CURRENT_FIX_GRID_2_BYTE_SIZE = 4060
CURRENT_FIX_GRID_2_SIZE = (309, 16)
CURRENT_FIX_GRID_2_SHA256 = (
    "ffc53c7b5fc9aa8c11053d704c4232505528577bfb9675fa7a4a2985e8e4ec2e"
)
CURRENT_FIX_GRID_2_OWNER_LOCAL_RECT = None

IMPORT_ROOT = Path("original_assets/source")


@dataclass(frozen=True)
class FastViewLeagueScoresResource:
    name: str
    source_path: str
    sha256: str
    byte_size: int
    size: tuple[int, int]
    owner_local_rect: tuple[int, int, int, int] | None
    direct_picture_control: bool


CURRENT_FIX_GRID_1 = FastViewLeagueScoresResource(
    name="current_fix_grid_1",
    source_path=CURRENT_FIX_GRID_1_PATH,
    sha256=CURRENT_FIX_GRID_1_SHA256,
    byte_size=CURRENT_FIX_GRID_1_BYTE_SIZE,
    size=CURRENT_FIX_GRID_1_SIZE,
    owner_local_rect=CURRENT_FIX_GRID_1_OWNER_LOCAL_RECT,
    direct_picture_control=True,
)

CURRENT_FIX_GRID_2 = FastViewLeagueScoresResource(
    name="current_fix_grid_2",
    source_path=CURRENT_FIX_GRID_2_PATH,
    sha256=CURRENT_FIX_GRID_2_SHA256,
    byte_size=CURRENT_FIX_GRID_2_BYTE_SIZE,
    size=CURRENT_FIX_GRID_2_SIZE,
    owner_local_rect=CURRENT_FIX_GRID_2_OWNER_LOCAL_RECT,
    direct_picture_control=False,
)


def current_fixture_grid1_rect() -> tuple[int, int, int, int]:
    """Return the exact FastViewLeagueScores owner-local PictureControl rect."""
    return CURRENT_FIX_GRID_1_OWNER_LOCAL_RECT


def imported_resource_path(
    repo_root: str | Path,
    resource: FastViewLeagueScoresResource,
) -> Path:
    return Path(repo_root) / IMPORT_ROOT / resource.source_path


def validate_staged_current_fixture_grid1(
    repo_root: str | Path,
) -> FastViewLeagueScoresResource:
    """Require the exact current_fix_grid_1 bytes when intentionally staged."""
    resource = CURRENT_FIX_GRID_1
    path = imported_resource_path(repo_root, resource)
    try:
        data = path.read_bytes()
    except FileNotFoundError as exc:
        raise FastViewLeagueScoresError(
            f"Missing staged FastView league-scores resource: {resource.source_path}"
        ) from exc
    if len(data) != resource.byte_size:
        raise FastViewLeagueScoresError("current_fix_grid_1 byte-size mismatch")
    if sha256(data).hexdigest() != resource.sha256:
        raise FastViewLeagueScoresError("current_fix_grid_1 checksum mismatch")
    if len(data) < 4:
        raise FastViewLeagueScoresError("current_fix_grid_1 has no EA444 header")
    if struct.unpack_from("<HH", data, 0) != resource.size:
        raise FastViewLeagueScoresError("current_fix_grid_1 geometry mismatch")
    return resource
