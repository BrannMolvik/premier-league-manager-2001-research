"""Source-closed FastView LeagueTableComposite geometry.

This is a distinct family from FastViewLeagueScores current-fixture score rows.
Recovery 205 binds the two current_table_grid EA444 files to the nested
LeagueTableComposite::Heading and ::Row classes, and closes their FastView
screen placement plus generic text-control rectangles.

The text columns are intentionally unnamed until their data producers are
traced. Neither original bitmap is provenance-staged yet.
"""
from __future__ import annotations

from dataclasses import dataclass


class FastViewLeagueTableError(ValueError):
    pass


SOURCE_PICTURE_CONTROL_CONSTRUCTOR_VA = 0x527730

LEAGUE_TABLE_COMPOSITE_CONSTRUCTOR_VA = 0x51E000
LEAGUE_TABLE_COMPOSITE_PRIMARY_VFTABLE = 0x7CA400
LEAGUE_TABLE_COMPOSITE_SECONDARY_VFTABLE = 0x7CA3F8
LEAGUE_TABLE_COMPOSITE_RTTI = ".?AVLeagueTableComposite@@"
LEAGUE_TABLE_COMPOSITE_SENDER_VFTABLE = 0x7CA40C
LEAGUE_TABLE_COMPOSITE_SENDER_RTTI = ".?AV?$Sender@VEventLeagueTableUpdate@@@@"

LEAGUE_TABLE_FASTVIEW_CALL_VA = 0x523472
LEAGUE_TABLE_SCREEN_ORIGIN = (382, 32)
LEAGUE_TABLE_ROW_FIRST_Y_OFFSET = 23
LEAGUE_TABLE_ROW_STEP = 19

HEADING_CONSTRUCTOR_VA = 0x51DCB0
HEADING_VFTABLE = 0x7CA3F0
HEADING_RTTI = ".?AVHeading@LeagueTableComposite@@"

ROW_CONSTRUCTOR_VA = 0x51D730
ROW_VFTABLE = 0x7CA3E8
ROW_RTTI = ".?AVRow@LeagueTableComposite@@"
ROW_MOVE_VA = 0x51DC10

CURRENT_TABLE_GRID_1_PATH = "FM2001_Art/FastView/current_table_grid_1.444"
CURRENT_TABLE_GRID_1_PATH_LITERAL_VA = 0x829114
CURRENT_TABLE_GRID_1_SHA256 = "db8114130becce71ba84f890ccd157606d04bf68501484df308564da28957a5f"
CURRENT_TABLE_GRID_1_BYTES = 4496
CURRENT_TABLE_GRID_1_SIZE = (381, 19)

CURRENT_TABLE_GRID_2_PATH = "FM2001_Art/FastView/current_table_grid_2.444"
CURRENT_TABLE_GRID_2_PATH_LITERAL_VA = 0x8290B4
CURRENT_TABLE_GRID_2_SHA256 = "e5a1b5688115cc8a63d47c738cf5af7f66f20eee9433292e47ee4e7c152ed70b"
CURRENT_TABLE_GRID_2_BYTES = 4276
CURRENT_TABLE_GRID_2_SIZE = (381, 16)

# Static initializer 0x51D650, consumed by Heading::0x51DCB0.
HEADING_TEXT_LOCAL_RECTS = (
    (168, 0, 198, 19),
    (198, 0, 228, 19),
    (228, 0, 258, 19),
    (258, 0, 288, 19),
    (288, 0, 318, 19),
    (318, 0, 348, 19),
    (348, 0, 378, 19),
)

# Static initializer 0x51D4F0, consumed by Row::0x51D730.
ROW_TEXT_LOCAL_RECTS = (
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
class LeagueTableCompositeFrame:
    heading_grid_rect: tuple[int, int, int, int]
    heading_text_rects: tuple[tuple[int, int, int, int], ...]
    row_grid_rects: tuple[tuple[int, int, int, int], ...]
    row_text_rects: tuple[tuple[tuple[int, int, int, int], ...], ...]
    text_semantics_recovered: bool = False
    bitmap_resources_imported: bool = False


def _translate(
    rect: tuple[int, int, int, int],
    origin: tuple[int, int],
) -> tuple[int, int, int, int]:
    x, y = origin
    left, top, right, bottom = rect
    return (x + left, y + top, x + right, y + bottom)


def league_table_visible_row_count(source_count: int) -> int:
    """Mirror 0x51E0F0..0x51E101.

    Counts through twelve keep one row object per source record. Larger source
    sets create ceil(count / 2) visible row objects for the two-side table
    presentation.
    """
    if type(source_count) is not int or source_count <= 0:
        raise FastViewLeagueTableError("LeagueTableComposite source_count must be positive")
    return source_count if source_count <= 12 else (source_count + 1) // 2


def league_table_heading_rect() -> tuple[int, int, int, int]:
    x, y = LEAGUE_TABLE_SCREEN_ORIGIN
    width, height = CURRENT_TABLE_GRID_1_SIZE
    return (x, y, x + width, y + height)


def league_table_heading_text_rects() -> tuple[tuple[int, int, int, int], ...]:
    return tuple(_translate(rect, LEAGUE_TABLE_SCREEN_ORIGIN) for rect in HEADING_TEXT_LOCAL_RECTS)


def league_table_row_origin(row_index: int) -> tuple[int, int]:
    if type(row_index) is not int or row_index < 0:
        raise FastViewLeagueTableError("row_index must be a non-negative integer")
    x, y = LEAGUE_TABLE_SCREEN_ORIGIN
    return (x, y + LEAGUE_TABLE_ROW_FIRST_Y_OFFSET + row_index * LEAGUE_TABLE_ROW_STEP)


def league_table_row_rect(row_index: int) -> tuple[int, int, int, int]:
    x, y = league_table_row_origin(row_index)
    width, height = CURRENT_TABLE_GRID_2_SIZE
    return (x, y, x + width, y + height)


def league_table_row_text_rects(
    row_index: int,
) -> tuple[tuple[int, int, int, int], ...]:
    origin = league_table_row_origin(row_index)
    return tuple(_translate(rect, origin) for rect in ROW_TEXT_LOCAL_RECTS)


def league_table_composite_frame(source_count: int) -> LeagueTableCompositeFrame:
    row_count = league_table_visible_row_count(source_count)
    return LeagueTableCompositeFrame(
        heading_grid_rect=league_table_heading_rect(),
        heading_text_rects=league_table_heading_text_rects(),
        row_grid_rects=tuple(league_table_row_rect(i) for i in range(row_count)),
        row_text_rects=tuple(league_table_row_text_rects(i) for i in range(row_count)),
    )
