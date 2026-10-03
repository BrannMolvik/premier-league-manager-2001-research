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

# Base layout helper 0x522CD0 stores these six source fields on the owning
# FastViewLeagueScores object. 0x5230B0 later uses them to reposition every
# ScoreComposite on the visible page.
FASTVIEW_LEAGUE_SCORES_ROW_COUNT = 12
FASTVIEW_LEAGUE_SCORES_ROW_STEP = 19
FASTVIEW_LEAGUE_SCORES_SINGLE_COLUMN_ORIGIN = (246, 55)
FASTVIEW_LEAGUE_SCORES_TWO_COLUMN_ORIGIN = (38, 55)
FASTVIEW_LEAGUE_SCORES_TWO_COLUMN_STEP = 416
FASTVIEW_LEAGUE_SCORES_PAGE_CAPACITY = 24

# ScoreComposite::0x51A730 adds the owning composite origin to these fixed local
# rectangles from the table at 0x828E98.
SCORE_COMPOSITE_NORMAL_GRID_LOCAL_RECT = (0, 0, 309, 16)
SCORE_COMPOSITE_NORMAL_TEXT_LOCAL_RECTS = (
    (2, 0, 132, 16),
    (177, 0, 307, 16),
    (139, 0, 152, 16),
    (158, 0, 171, 16),
)

SCORE_COMPOSITE_EVENT_RECEIVERS = (
    ("EventHalfTime", 0x7CA160, 0x7CA354, 0x51B9A0),
    ("EventExtraTime", 0x7CA16C, 0x7CA348, 0x51B9C0),
    ("EventPenalties", 0x7CA148, 0x7CA33C, 0x51B9E0),
    ("EventFullTime", 0x7CA154, 0x7CA330, 0x51BA00),
    ("EventGlobalSecondHalf", 0x7CA240, 0x7CA324, 0x51BA20),
)

SCORE_COMPOSITE_PHASE_DISPLAY_HELPER_VA = 0x51BA30
SCORE_COMPOSITE_PHASE_DISPLAY_CLEAR_VA = 0x51BBE0
SCORE_COMPOSITE_PHASE_ICON_LOCAL_RECT = (316, 0, 334, 16)
SCORE_COMPOSITE_PHASE_TEXT_LOCAL_RECT = (311, 0, 339, 16)
SCORE_COMPOSITE_PHASE_TEXT_RAW_FLAGS = 0x24
SCORE_COMPOSITE_PHASE_TEXT_STYLE_INDEX = 1
SCORE_COMPOSITE_PHASE_PICTURE_VARIANT = 0
SCORE_COMPOSITE_PHASE_ACTIVE_FLAG_OFFSET = 0xAC
SCORE_COMPOSITE_PHASE_PICTURE_PTR_OFFSET = 0xD8
SCORE_COMPOSITE_PHASE_TEXT_PTR_OFFSET = 0xDC


@dataclass(frozen=True)
class FastViewScorePhaseResource:
    event_name: str
    name: str
    source_path: str
    sha256: str
    byte_size: int
    size: tuple[int, int]
    path_literal_va: int
    static_string_initializer_va: int
    static_string_object_va: int
    callback_va: int
    callback_icon_pointer_va: int
    callback_label_global_va: int
    imported: bool = False


HALF_TIME_ICON = FastViewScorePhaseResource(
    event_name="EventHalfTime",
    name="half_time_icon",
    source_path="FM2001_Art/FastView/half_time_icon.444",
    sha256="351589aa787ef62dae4013c67e231c90c7b6f2e82acd635fb67adb13e1c994c8",
    byte_size=568,
    size=(18, 16),
    path_literal_va=0x828DD0,
    static_string_initializer_va=0x51B650,
    static_string_object_va=0x877628,
    callback_va=0x51B9A0,
    callback_icon_pointer_va=0x877630,
    callback_label_global_va=0x982380,
)

FULL_TIME_ICON = FastViewScorePhaseResource(
    event_name="EventFullTime",
    name="full_time_icon",
    source_path="FM2001_Art/FastView/full_time_icon.444",
    sha256="9a24ab846620d6460afe265c6c98488870a08e2802d55476b9735a8641ae81b8",
    byte_size=616,
    size=(18, 16),
    path_literal_va=0x828DF8,
    static_string_initializer_va=0x51B690,
    static_string_object_va=0x877610,
    callback_va=0x51BA00,
    callback_icon_pointer_va=0x877618,
    callback_label_global_va=0x98237C,
)

EXTRA_TIME_ICON = FastViewScorePhaseResource(
    event_name="EventExtraTime",
    name="extra_time_icon",
    source_path="FM2001_Art/FastView/extra_time_icon.444",
    sha256="cf8af734450ab3069e0b32d82a770909d962ade9545533e7715d36d53e0eea2e",
    byte_size=400,
    size=(18, 16),
    path_literal_va=0x828E20,
    static_string_initializer_va=0x51B6D0,
    static_string_object_va=0x8775F8,
    callback_va=0x51B9C0,
    callback_icon_pointer_va=0x877600,
    callback_label_global_va=0x982378,
)

PENALTIES_ICON = FastViewScorePhaseResource(
    event_name="EventPenalties",
    name="penalties_icon",
    source_path="FM2001_Art/FastView/penalties_icon.444",
    sha256="0fc5b157ecfadfa437f65ef5a4b940b5de6886e8c1e81e1f4ccba8d97af23545",
    byte_size=280,
    size=(18, 16),
    path_literal_va=0x828E48,
    static_string_initializer_va=0x51B710,
    static_string_object_va=0x8775E0,
    callback_va=0x51B9E0,
    callback_icon_pointer_va=0x8775E8,
    callback_label_global_va=0x982374,
)

SCORE_COMPOSITE_PHASE_RESOURCES = (
    HALF_TIME_ICON,
    EXTRA_TIME_ICON,
    PENALTIES_ICON,
    FULL_TIME_ICON,
)
SCORE_COMPOSITE_PHASE_RESOURCE_BY_EVENT = {
    item.event_name: item for item in SCORE_COMPOSITE_PHASE_RESOURCES
}


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
    """Return the source table's grid-2 width/height pair."""
    return (
        SCORE_COMPOSITE_NORMAL_LAYOUT_DWORDS[0],
        SCORE_COMPOSITE_NORMAL_LAYOUT_DWORDS[1],
    )


@dataclass(frozen=True)
class FastViewLeagueScoresPageLayout:
    columns: int
    rows_per_column: int
    origin: tuple[int, int]
    column_step: int
    row_step: int

    def slot_origin(self, column: int, row: int) -> tuple[int, int]:
        if type(column) is not int or type(row) is not int:
            raise FastViewScoresError("column and row must be integers")
        if not 0 <= column < self.columns:
            raise FastViewScoresError("column is outside the source page layout")
        if not 0 <= row < self.rows_per_column:
            raise FastViewScoresError("row is outside the source page layout")
        return (
            self.origin[0] + column * self.column_step,
            self.origin[1] + row * self.row_step,
        )


def fastview_league_scores_page_layout(
    source_count: int,
) -> FastViewLeagueScoresPageLayout:
    """Return the exact 0x522CD0/0x5230B0 row-layout contract.

    Counts through 12 use one centered column. Larger source sets use two
    12-row columns separated by 416 pixels. The source has separate paging
    behavior above 24 entries, so this function describes one visible page and
    does not map off-page source entries.
    """
    if type(source_count) is not int or source_count <= 0:
        raise FastViewScoresError("FastViewLeagueScores source_count must be positive")
    if source_count <= FASTVIEW_LEAGUE_SCORES_ROW_COUNT:
        return FastViewLeagueScoresPageLayout(
            columns=1,
            rows_per_column=FASTVIEW_LEAGUE_SCORES_ROW_COUNT,
            origin=FASTVIEW_LEAGUE_SCORES_SINGLE_COLUMN_ORIGIN,
            column_step=0,
            row_step=FASTVIEW_LEAGUE_SCORES_ROW_STEP,
        )
    return FastViewLeagueScoresPageLayout(
        columns=2,
        rows_per_column=FASTVIEW_LEAGUE_SCORES_ROW_COUNT,
        origin=FASTVIEW_LEAGUE_SCORES_TWO_COLUMN_ORIGIN,
        column_step=FASTVIEW_LEAGUE_SCORES_TWO_COLUMN_STEP,
        row_step=FASTVIEW_LEAGUE_SCORES_ROW_STEP,
    )


def _translate_rect(
    rect: tuple[int, int, int, int],
    origin: tuple[int, int],
) -> tuple[int, int, int, int]:
    left, top, right, bottom = rect
    x, y = origin
    return (x + left, y + top, x + right, y + bottom)


def score_composite_normal_rects(
    origin: tuple[int, int],
) -> tuple[tuple[int, int, int, int], tuple[tuple[int, int, int, int], ...]]:
    """Return the exact grid-2 and four generic text-control rectangles."""
    if (
        type(origin) is not tuple
        or len(origin) != 2
        or any(type(value) is not int for value in origin)
    ):
        raise FastViewScoresError("ScoreCompositeNormal origin must be an integer pair")
    return (
        _translate_rect(SCORE_COMPOSITE_NORMAL_GRID_LOCAL_RECT, origin),
        tuple(
            _translate_rect(rect, origin)
            for rect in SCORE_COMPOSITE_NORMAL_TEXT_LOCAL_RECTS
        ),
    )


def score_composite_normal_page_slot_rects(
    source_count: int,
    column: int,
    row: int,
) -> tuple[tuple[int, int, int, int], tuple[tuple[int, int, int, int], ...]]:
    """Resolve one visible page slot to exact final grid/text rectangles."""
    layout = fastview_league_scores_page_layout(source_count)
    return score_composite_normal_rects(layout.slot_origin(column, row))


def score_composite_phase_local_rects() -> tuple[
    tuple[int, int, int, int],
    tuple[int, int, int, int],
]:
    """Return exact local PictureControl/text rectangles from 0x51BA30."""
    return (
        SCORE_COMPOSITE_PHASE_ICON_LOCAL_RECT,
        SCORE_COMPOSITE_PHASE_TEXT_LOCAL_RECT,
    )


def score_composite_phase_rects(
    origin: tuple[int, int],
) -> tuple[tuple[int, int, int, int], tuple[int, int, int, int]]:
    """Translate the exact phase icon/text pair to one composite origin."""
    if (
        type(origin) is not tuple
        or len(origin) != 2
        or any(type(value) is not int for value in origin)
    ):
        raise FastViewScoresError("ScoreComposite phase origin must be an integer pair")
    return (
        _translate_rect(SCORE_COMPOSITE_PHASE_ICON_LOCAL_RECT, origin),
        _translate_rect(SCORE_COMPOSITE_PHASE_TEXT_LOCAL_RECT, origin),
    )


def score_composite_phase_resource(event_name: str) -> FastViewScorePhaseResource:
    """Return only the exact typed callback-to-icon mapping proved in source."""
    if type(event_name) is not str:
        raise FastViewScoresError("ScoreComposite phase event name must be a string")
    try:
        return SCORE_COMPOSITE_PHASE_RESOURCE_BY_EVENT[event_name]
    except KeyError as exc:
        raise FastViewScoresError(
            "No source-proven phase icon for this ScoreComposite event"
        ) from exc
