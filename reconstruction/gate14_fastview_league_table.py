"""Source-closed FastView LeagueTableComposite geometry and assets.

Recovery 206 separates the current-table grid family from the already-closed
FastViewLeagueScores / ScoreCompositeNormal current-fixture grids.

Only exact executable/disc evidence is represented here. User-facing meanings
for the heading and row text controls remain deliberately unnamed.
"""
from __future__ import annotations

from dataclasses import dataclass


class FastViewLeagueTableError(ValueError):
    pass


SOURCE_PICTURE_CONTROL_CONSTRUCTOR_VA = 0x527730
SOURCE_TEXT_CONTROL_CONSTRUCTOR_VA = 0x527960

LEAGUE_TABLE_COMPOSITE_CONSTRUCTOR_VA = 0x51E000
LEAGUE_TABLE_COMPOSITE_FASTVIEW_CALLSITE_VA = 0x523472
LEAGUE_TABLE_COMPOSITE_PRIMARY_VFTABLE = 0x7CA400
LEAGUE_TABLE_COMPOSITE_SECONDARY_VFTABLE = 0x7CA3F8
LEAGUE_TABLE_COMPOSITE_RTTI = ".?AVLeagueTableComposite@@"

LEAGUE_TABLE_EVENT_SCORE_BASE_VFTABLE = 0x7CA3B0
LEAGUE_TABLE_EVENT_SCORE_RTTI = ".?AV?$Receiver@VEventScore@@@@"
LEAGUE_TABLE_EVENT_UPDATE_BASE_VFTABLE = 0x7CA40C
LEAGUE_TABLE_EVENT_UPDATE_RTTI = ".?AV?$Sender@VEventLeagueTableUpdate@@@@"

LEAGUE_TABLE_ROW_CONSTRUCTOR_VA = 0x51D730
LEAGUE_TABLE_ROW_VFTABLE = 0x7CA3E8
LEAGUE_TABLE_ROW_RTTI = ".?AVRow@LeagueTableComposite@@"

LEAGUE_TABLE_HEADING_CONSTRUCTOR_VA = 0x51DCB0
LEAGUE_TABLE_HEADING_VFTABLE = 0x7CA3F0
LEAGUE_TABLE_HEADING_RTTI = ".?AVHeading@LeagueTableComposite@@"

LEAGUE_TABLE_ORIGIN = (382, 32)
LEAGUE_TABLE_HEADING_LOCAL_GRID_RECT = (0, 0, 381, 19)
LEAGUE_TABLE_ROW_LOCAL_GRID_RECT = (0, 0, 381, 16)
LEAGUE_TABLE_ROW_FIRST_ORIGIN = (382, 55)
LEAGUE_TABLE_ROW_STEP = 19
LEAGUE_TABLE_COUNT_SWITCH = 12

LEAGUE_TABLE_HEADING_TEXT_LOCAL_RECTS = tuple(
    (168 + 30 * index, 0, 198 + 30 * index, 19)
    for index in range(7)
)

# Exact source order from the nine-entry table at 0x8776B8. The first seven
# are fixed 30x16 statistic cells. The final two are separate left-side cells.
LEAGUE_TABLE_ROW_TEXT_LOCAL_RECTS = (
    (168, 0, 198, 16),
    (198, 0, 228, 16),
    (228, 0, 258, 16),
    (258, 0, 288, 16),
    (288, 0, 318, 16),
    (318, 0, 348, 16),
    (348, 0, 378, 16),
    (0, 0, 26, 16),
    (30, 0, 160, 16),
)


@dataclass(frozen=True)
class FastViewLeagueTableGridResource:
    name: str
    owner: str
    source_path: str
    sha256: str
    byte_size: int
    size: tuple[int, int]
    path_literal_va: int
    imported: bool = False


CURRENT_TABLE_GRID_1 = FastViewLeagueTableGridResource(
    name="current_table_grid_1",
    owner="LeagueTableComposite::Heading",
    source_path="FM2001_Art/FastView/current_table_grid_1.444",
    sha256="db8114130becce71ba84f890ccd157606d04bf68501484df308564da28957a5f",
    byte_size=4496,
    size=(381, 19),
    path_literal_va=0x829114,
)

CURRENT_TABLE_GRID_2 = FastViewLeagueTableGridResource(
    name="current_table_grid_2",
    owner="LeagueTableComposite::Row",
    source_path="FM2001_Art/FastView/current_table_grid_2.444",
    sha256="e5a1b5688115cc8a63d47c738cf5af7f66f20eee9433292e47ee4e7c152ed70b",
    byte_size=4276,
    size=(381, 16),
    path_literal_va=0x8290B4,
)

FASTVIEW_CURRENT_TABLE_GRID_RESOURCES = (
    CURRENT_TABLE_GRID_1,
    CURRENT_TABLE_GRID_2,
)


def _translate_rect(
    rect: tuple[int, int, int, int],
    origin: tuple[int, int],
) -> tuple[int, int, int, int]:
    left, top, right, bottom = rect
    x, y = origin
    return (x + left, y + top, x + right, y + bottom)


def league_table_visible_row_count(source_count: int) -> int:
    """Mirror 0x51E0F0..0x51E101 without assigning page semantics.

    Counts through twelve are preserved. Larger counts are transformed with
    floor((count - 1) / 2) + 1, i.e. ceil(count / 2), exactly as compiled.
    """
    if type(source_count) is not int or source_count <= 0:
        raise FastViewLeagueTableError("LeagueTableComposite source_count must be positive")
    if source_count <= LEAGUE_TABLE_COUNT_SWITCH:
        return source_count
    return ((source_count - 1) // 2) + 1


def league_table_heading_rects() -> tuple[
    tuple[int, int, int, int],
    tuple[tuple[int, int, int, int], ...],
]:
    """Return exact final heading grid/text rectangles."""
    return (
        _translate_rect(LEAGUE_TABLE_HEADING_LOCAL_GRID_RECT, LEAGUE_TABLE_ORIGIN),
        tuple(
            _translate_rect(rect, LEAGUE_TABLE_ORIGIN)
            for rect in LEAGUE_TABLE_HEADING_TEXT_LOCAL_RECTS
        ),
    )


def league_table_row_origin(row_index: int) -> tuple[int, int]:
    if type(row_index) is not int or row_index < 0:
        raise FastViewLeagueTableError("LeagueTableComposite row_index must be non-negative")
    return (
        LEAGUE_TABLE_ROW_FIRST_ORIGIN[0],
        LEAGUE_TABLE_ROW_FIRST_ORIGIN[1] + row_index * LEAGUE_TABLE_ROW_STEP,
    )


def league_table_row_rects(
    row_index: int,
) -> tuple[
    tuple[int, int, int, int],
    tuple[tuple[int, int, int, int], ...],
]:
    """Return exact final row grid/text rectangles for one source-created row."""
    origin = league_table_row_origin(row_index)
    return (
        _translate_rect(LEAGUE_TABLE_ROW_LOCAL_GRID_RECT, origin),
        tuple(
            _translate_rect(rect, origin)
            for rect in LEAGUE_TABLE_ROW_TEXT_LOCAL_RECTS
        ),
    )
