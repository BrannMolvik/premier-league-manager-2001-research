"""Source-closed static text-control inventory for nested FastView scores/table.

The canonical score and LeagueTable geometry already proves visible generic
TextControls even though their user-facing semantics, final text values,
style/font/color and pixels are not yet source-closed. This module enumerates
only those controls and exact 800x600 rectangles.

Runtime ScoreComposite phase labels are intentionally excluded because they
have a separate source/raster contract. Later LeagueScores title/button
controls are also excluded until their own geometry/resource contract is
recovered.
"""
from __future__ import annotations

from dataclasses import dataclass

from gate14_fastview_league_table import (
    league_table_heading_rects,
    league_table_row_rects,
    league_table_visible_row_count,
)
from gate14_fastview_scores import (
    FASTVIEW_LEAGUE_SCORES_PAGE_CAPACITY,
    score_composite_normal_page_slot_rects,
)


class FastViewStaticTextInventoryError(ValueError):
    pass


@dataclass(frozen=True)
class FastViewStaticTextControl:
    identity: str
    owner: str
    source_index: int | None
    control_index: int
    rect: tuple[int, int, int, int]

    def __post_init__(self) -> None:
        if not isinstance(self.identity, str) or not self.identity:
            raise FastViewStaticTextInventoryError("identity must be non-empty")
        if self.owner not in {
            "score_composite_normal",
            "league_table_heading",
            "league_table_row",
        }:
            raise FastViewStaticTextInventoryError("unknown static text owner")
        if self.source_index is not None and (
            type(self.source_index) is not int or self.source_index < 0
        ):
            raise FastViewStaticTextInventoryError(
                "source_index must be non-negative integer or None"
            )
        if type(self.control_index) is not int or self.control_index < 0:
            raise FastViewStaticTextInventoryError(
                "control_index must be non-negative integer"
            )
        if (
            type(self.rect) is not tuple
            or len(self.rect) != 4
            or any(type(value) is not int for value in self.rect)
        ):
            raise FastViewStaticTextInventoryError(
                "static text rect must contain four integers"
            )
        left, top, right, bottom = self.rect
        if not (0 <= left < right <= 800 and 0 <= top < bottom <= 600):
            raise FastViewStaticTextInventoryError(
                "static text rect must remain inside the 800x600 FastView surface"
            )


def league_scores_static_text_inventory(
    source_count: int,
) -> tuple[FastViewStaticTextControl, ...]:
    """Return four source-ordered static TextControls per visible score row."""
    if (
        type(source_count) is not int
        or not 1 <= source_count <= FASTVIEW_LEAGUE_SCORES_PAGE_CAPACITY
    ):
        raise FastViewStaticTextInventoryError(
            "LeagueScores static text requires one verified 1..12 visible page"
        )

    controls = []
    for source_index in range(source_count):
        _grid, text_rects = score_composite_normal_page_slot_rects(
            source_count,
            0,
            source_index,
        )
        if len(text_rects) != 4:
            raise FastViewStaticTextInventoryError(
                "ScoreCompositeNormal must retain four static TextControls"
            )
        for control_index, rect in enumerate(text_rects):
            controls.append(
                FastViewStaticTextControl(
                    identity=f"score_row_{source_index}_text_{control_index}",
                    owner="score_composite_normal",
                    source_index=source_index,
                    control_index=control_index,
                    rect=rect,
                )
            )
    return tuple(controls)


def league_table_static_text_inventory(
    source_count: int,
) -> tuple[FastViewStaticTextControl, ...]:
    """Return the heading and visible-row TextControls in source order."""
    try:
        visible_rows = league_table_visible_row_count(source_count)
    except Exception as exc:
        raise FastViewStaticTextInventoryError(str(exc)) from exc

    _heading_grid, heading_text = league_table_heading_rects()
    if len(heading_text) != 7:
        raise FastViewStaticTextInventoryError(
            "LeagueTable heading must retain seven TextControls"
        )

    controls = [
        FastViewStaticTextControl(
            identity=f"league_table_heading_text_{control_index}",
            owner="league_table_heading",
            source_index=None,
            control_index=control_index,
            rect=rect,
        )
        for control_index, rect in enumerate(heading_text)
    ]
    for source_index in range(visible_rows):
        _row_grid, row_text = league_table_row_rects(source_index)
        if len(row_text) != 9:
            raise FastViewStaticTextInventoryError(
                "LeagueTable row must retain nine TextControls"
            )
        for control_index, rect in enumerate(row_text):
            controls.append(
                FastViewStaticTextControl(
                    identity=(
                        f"league_table_row_{source_index}_text_{control_index}"
                    ),
                    owner="league_table_row",
                    source_index=source_index,
                    control_index=control_index,
                    rect=rect,
                )
            )
    return tuple(controls)


def static_text_inventory_contract(
    *,
    league_scores_source_count: int,
    league_table_source_count: int,
) -> dict:
    scores = league_scores_static_text_inventory(league_scores_source_count)
    table = league_table_static_text_inventory(league_table_source_count)
    return {
        "league_scores_static_text_control_count": len(scores),
        "league_table_static_text_control_count": len(table),
        "score_row_text_controls_per_row": 4,
        "league_table_heading_text_controls": 7,
        "league_table_row_text_controls_per_row": 9,
        "geometry_recovered": True,
        "source_control_order_recovered": True,
        "user_facing_semantics_recovered": False,
        "final_text_values_recovered": False,
        "font_style_color_recovered": False,
        "pixels_rasterized": False,
        "later_league_scores_title_button_controls_included": False,
        "score_subpanel_complete_pixels_recovered": False,
        "global_fastview_z_order_recovered": False,
        "complete_fastview_frame_recovered": False,
        "gate14_complete": False,
    }
