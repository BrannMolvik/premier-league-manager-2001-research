"""Source-closed FastView current-fixture score-grid contracts.

Recovery 205 separates two similarly named original EA444 resources by their
actual owning classes and constructor paths. This module records only exact
source identity, geometry and typed receiver behavior proved from the canonical
FM2001 executable and authorized disc.

No grid pixels are rendered here because these two original resources are not
yet provenance-staged in the repository.
"""
from __future__ import annotations

from dataclasses import dataclass


class FastViewScoresError(ValueError):
    pass


SOURCE_PICTURE_CONTROL_CONSTRUCTOR_VA = 0x527730
SOURCE_PICTURE_CONTROL_VFTABLE = 0x7CAA5C
SOURCE_PICTURE_CONTROL_RTTI = ".?AVPictureControl@@"

FASTVIEW_LEAGUE_SCORES_PRIMARY_VFTABLE = 0x7CA750
FASTVIEW_LEAGUE_SCORES_RECEIVER_VFTABLE = 0x7CA744
FASTVIEW_LEAGUE_SCORES_RTTI = ".?AVFastViewLeagueScores@FastViewPanel@@"
FASTVIEW_LEAGUE_SCORES_LAYOUT_METHOD_VA = 0x523DF0
FASTVIEW_LEAGUE_SCORES_SCORE_FACTORY_VA = 0x523CC0
FASTVIEW_LEAGUE_SCORES_EVENT_UPDATE_CALLBACK_VA = 0x523DB0
EVENT_LEAGUE_TABLE_UPDATE_BASE_VFTABLE = 0x7CA7B4
EVENT_LEAGUE_TABLE_UPDATE_RTTI = ".?AV?$Receiver@VEventLeagueTableUpdate@@@@"

SCORE_COMPOSITE_NORMAL_CONSTRUCTOR_VA = 0x51B740
SCORE_COMPOSITE_NORMAL_PRIMARY_VFTABLE = 0x7CA36C
SCORE_COMPOSITE_NORMAL_RTTI = ".?AVScoreCompositeNormal@@"
SCORE_COMPOSITE_NORMAL_LAYOUT_TABLE_VA = 0x828E98
SCORE_COMPOSITE_NORMAL_LAYOUT_DWORDS = (
    309, 16, 0, 0, 0, 0, 2, 139, 177, 158, 130, 16, 13, 16
)

SCORE_COMPOSITE_EVENT_RECEIVERS = (
    ("EventHalfTime", 0x7CA160, 0x7CA354, 0x51B9A0),
    ("EventExtraTime", 0x7CA16C, 0x7CA348, 0x51B9C0),
    ("EventPenalties", 0x7CA148, 0x7CA33C, 0x51B9E0),
    ("EventFullTime", 0x7CA154, 0x7CA330, 0x51BA00),
    ("EventGlobalSecondHalf", 0x7CA240, 0x7CA324, 0x51BA20),
)


@dataclass(frozen=True)
class FastViewScoreGridResource:
    name: str
    owner: str
    source_path: str
    sha256: str
    byte_size: int
    size: tuple[int, int]
    path_literal_va: int
    imported: bool = False


CURRENT_FIX_GRID_1 = FastViewScoreGridResource(
    name="current_fix_grid_1",
    owner="FastViewPanel::FastViewLeagueScores",
    source_path="FM2001_Art/FastView/current_fix_grid_1.444",
    sha256="bdd2fe25884e8ce72e21bd7b9296c65827ce90ea058c6f43e2f727f2bae19057",
    byte_size=3704,
    size=(309, 19),
    path_literal_va=0x829920,
)

CURRENT_FIX_GRID_2 = FastViewScoreGridResource(
    name="current_fix_grid_2",
    owner="ScoreCompositeNormal",
    source_path="FM2001_Art/FastView/current_fix_grid_2.444",
    sha256="ffc53c7b5fc9aa8c11053d704c4232505528577bfb9675fa7a4a2985e8e4ec2e",
    byte_size=4060,
    size=(309, 16),
    path_literal_va=0x828ED0,
)

FASTVIEW_CURRENT_FIXTURE_GRID_RESOURCES = (
    CURRENT_FIX_GRID_1,
    CURRENT_FIX_GRID_2,
)


def fastview_league_scores_grid_rects(
    source_count: int,
) -> tuple[tuple[int, int, int, int], ...]:
    """Return exact grid-1 PictureControl rectangles from 0x523DF0.

    The source method switches at count 12. One through twelve entries use one
    centered 309x19 strip. Counts above twelve use one left and one right strip.
    Zero is rejected here because downstream source indexing uses count-1 and a
    zero-entry live state is not proved by this path.
    """
    if type(source_count) is not int or source_count <= 0:
        raise FastViewScoresError("FastViewLeagueScores source_count must be positive")
    if source_count <= 12:
        return ((246, 32, 555, 51),)
    return (
        (38, 32, 347, 51),
        (454, 32, 763, 51),
    )


def score_composite_normal_local_grid_size() -> tuple[int, int]:
    """Return the source table's grid-2 width/height pair.

    The final screen origin remains caller-supplied by the owning composite and
    is deliberately not invented here.
    """
    return (
        SCORE_COMPOSITE_NORMAL_LAYOUT_DWORDS[0],
        SCORE_COMPOSITE_NORMAL_LAYOUT_DWORDS[1],
    )
