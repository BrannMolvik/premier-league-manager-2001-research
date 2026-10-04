"""Source-closed partial FastView cross-component draw order.

Canonical executable tracing closes a partial relative paint order across the
currently rasterized FastView component families. Direct FastViewPanel controls
use the generic append-order child array; the score and team subtrees enter that
same parent array through SubPanelControl wrappers whose render slot delegates
synchronously into the owned panel's generic forward traversal.

The phase-split LeagueScores raster now has a source-closed order around the
LeagueTable block: early score rows -> LeagueTable -> late grid -> runtime
phase-icon tail. The older aggregate league_scores_static plane is retained only
for compatibility and still has no single relation to LeagueTable or the split
score phases because it spans more than one native position.

The contract remains partial and does not claim a global FastView z-order
across omitted or unbound layers, a cross-component pixel blend rule,
background ownership, audio, or 3D choreography.
"""
from __future__ import annotations

from dataclasses import dataclass


class FastViewDrawOrderError(ValueError):
    pass


# Generic parent draw-array contract.
PARENT_DRAW_ARRAY_POINTER_OFFSET = 0x1C
PARENT_DRAW_ARRAY_COUNT_OFFSET = 0x38
PARENT_DRAW_ARRAY_REGISTER_VA = 0x5274C0
PARENT_DRAW_ARRAY_APPEND_HELPER_VA = 0x5275C0
PARENT_DRAW_TRAVERSAL_VA = 0x6533A0
CHILD_RENDER_VIRTUAL_OFFSET = 0x64

# Constructors that register generic controls through 0x5274C0.
PICTURE_CONTROL_CONSTRUCTOR_VA = 0x527730
TEXT_CONTROL_CONSTRUCTOR_VA = 0x527960
PICTURE_CONTROL_REGISTER_CALL_VA = 0x52782A
TEXT_CONTROL_REGISTER_CALL_VA = 0x527A15

# Direct FastViewPanel construction order retained from the earlier source pass.
TOP_BAR_PICTURE_CALL_VA = 0x51FDA3
TICKER_PICTURE_CALL_VA = 0x51FE31
POSSESSION_DIAGRAM_OWNER_CALL_VA = 0x5206CD
POSSESSION_FIGURES_OWNER_CALL_VA = 0x520802
POSSESSION_DIAGRAM_CONSTRUCTOR_VA = 0x5227D0
POSSESSION_FIGURES_CONSTRUCTOR_VA = 0x51E7E0

# Slot +0x64 in the generic PictureControl/TextControl vtables reaches this
# visible-child forwarding seam.
PICTURE_CONTROL_VTABLE_VA = 0x7CAA5C
TEXT_CONTROL_VTABLE_VA = 0x7CAAF8
GENERIC_CHILD_RENDER_TARGET_VA = 0x64F6D0

# Recovery 275: nested score/team panels are represented in the parent draw
# array by SubPanelControl@FastViewPanel wrappers. 0x650B20 stores the target
# panel at +0x2C. The wrapper's +0x64 render slot is 0x650BB0 and its call at
# 0x650BFF synchronously invokes generic traversal 0x6533A0 on that target.
SUBPANEL_CONTROL_VTABLE_VA = 0x7CA5E4
SUBPANEL_CONTROL_TARGET_PANEL_OFFSET = 0x2C
SUBPANEL_CONTROL_RENDER_VA = 0x650BB0
SUBPANEL_CONTROL_TRAVERSAL_CALL_VA = 0x650BFF

FASTVIEW_SCORES_OBJECT_OFFSET = 0x90
FASTVIEW_SCORES_SUBPANEL_REGISTER_CALL_VA = 0x520DEF
FASTVIEW_SCORES_SUBPANEL_OFFSET = 0x98
FASTVIEW_TEAM_OBJECT_OFFSET = 0x94
FASTVIEW_TEAM_OWNER_CALL_VA = 0x520E67
FASTVIEW_TEAM_CONSTRUCTOR_VA = 0x524920
FASTVIEW_TEAM_SUBPANEL_REGISTER_CALL_VA = 0x520EEF
FASTVIEW_TEAM_SUBPANEL_OFFSET = 0x9C

# FastViewLeagueScores setup at 0x523370 first calls the generic entry builder
# 0x522CD0. Its vtable slot +0x5C is 0x523CC0, so one ScoreCompositeNormal
# (five static controls) is registered per source entry before LeagueTable.
# LeagueTable follows at 0x523472. Later controls include title_bar_22 at
# 0x523554 and current_fix_grid_1 at 0x5239F3. The aggregate
# league_scores_static raster therefore spans native positions both before and
# after league_table_static and cannot receive one pairwise relation.
FASTVIEW_LEAGUE_SCORES_SETUP_VA = 0x523370
FASTVIEW_SCORE_ENTRY_BUILD_CALLSITE_VA = 0x5233C2
FASTVIEW_SCORE_ENTRY_BUILDER_VA = 0x522CD0
FASTVIEW_SCORE_FACTORY_VTABLE_SLOT = 0x5C
FASTVIEW_SCORE_FACTORY_VA = 0x523CC0
LEAGUE_TABLE_COMPOSITE_FASTVIEW_CALLSITE_VA = 0x523472
LEAGUE_TABLE_COMPOSITE_CONSTRUCTOR_VA = 0x51E000
LEAGUE_TABLE_HEADING_CONSTRUCTOR_VA = 0x51DCB0
LEAGUE_TABLE_ROW_CONSTRUCTOR_VA = 0x51D730
LEAGUE_SCORES_TITLE_BAR_22_PICTURE_CALLSITE_VA = 0x523554
LEAGUE_SCORES_CURRENT_FIX_GRID_1_PICTURE_CALLSITE_VA = 0x5239F3

# Each tuple is one native paint position among the currently rasterized
# families. team_table_static and team_table_energy are alternative
# reconstruction views of the same native TeamTable position, not two native
# siblings, so no relation is exposed between those aliases.
SOURCE_CLOSED_RASTER_COMPONENT_ORDER_LEVELS = (
    ("direct_chrome",),
    ("possession_diagram",),
    ("possession_figures_text",),
    ("league_scores_early_rows_static",),
    ("league_table_static",),
    ("league_scores_late_grid_static",),
    ("league_scores_runtime_phase_icons",),
    ("team_table_static", "team_table_energy"),
)

_COMPONENT_PARENT_GROUP = {
    "direct_chrome": "fastview_panel",
    "possession_diagram": "fastview_panel",
    "possession_figures_text": "fastview_panel",
    "league_table_static": "fastview_scores",
    "league_scores_static": "fastview_scores",
    "league_scores_early_rows_static": "fastview_scores",
    "league_scores_late_grid_static": "fastview_scores",
    "league_scores_runtime_phase_icons": "fastview_scores",
    "team_table_static": "fastview_team",
    "team_table_energy": "fastview_team",
}


@dataclass(frozen=True)
class FastViewPairwiseDrawOrder:
    earlier_component: str
    later_component: str
    same_parent_draw_array: bool
    registration_is_append_order: bool
    traversal_is_forward: bool
    nested_subpanel_bridge_recovered: bool = False
    pixel_blend_rule_recovered: bool = False
    global_z_order_recovered: bool = False

    def __post_init__(self) -> None:
        if (
            not isinstance(self.earlier_component, str)
            or not self.earlier_component
            or not isinstance(self.later_component, str)
            or not self.later_component
            or self.earlier_component == self.later_component
        ):
            raise FastViewDrawOrderError(
                "pairwise draw-order components must be distinct non-empty names"
            )
        if not (
            self.registration_is_append_order
            and self.traversal_is_forward
            and (self.same_parent_draw_array or self.nested_subpanel_bridge_recovered)
        ):
            raise FastViewDrawOrderError(
                "source-closed pairwise order requires the complete registration/traversal chain"
            )
        if self.same_parent_draw_array and self.nested_subpanel_bridge_recovered:
            raise FastViewDrawOrderError(
                "pairwise order must identify either one shared parent array or a nested subpanel bridge"
            )
        if self.pixel_blend_rule_recovered or self.global_z_order_recovered:
            raise FastViewDrawOrderError(
                "pairwise FastView order cannot promote blend or global z-order"
            )


def _relation(earlier_component: str, later_component: str) -> FastViewPairwiseDrawOrder:
    same_parent = (
        _COMPONENT_PARENT_GROUP[earlier_component]
        == _COMPONENT_PARENT_GROUP[later_component]
    )
    return FastViewPairwiseDrawOrder(
        earlier_component=earlier_component,
        later_component=later_component,
        same_parent_draw_array=same_parent,
        registration_is_append_order=True,
        traversal_is_forward=True,
        nested_subpanel_bridge_recovered=not same_parent,
    )


def _source_closed_relations() -> dict[frozenset[str], FastViewPairwiseDrawOrder]:
    relations: dict[frozenset[str], FastViewPairwiseDrawOrder] = {}
    for earlier_index, earlier_level in enumerate(
        SOURCE_CLOSED_RASTER_COMPONENT_ORDER_LEVELS
    ):
        for later_level in SOURCE_CLOSED_RASTER_COMPONENT_ORDER_LEVELS[
            earlier_index + 1 :
        ]:
            for earlier_component in earlier_level:
                for later_component in later_level:
                    relation = _relation(earlier_component, later_component)
                    relations[
                        frozenset((earlier_component, later_component))
                    ] = relation
    return relations


_SOURCE_CLOSED_PAIRWISE_RELATIONS = _source_closed_relations()

# The historical aggregate score plane spans the three split score phases, so
# it cannot be ordered against LeagueTable or any split score phase. Its outer
# wrapper relations remain valid: all direct FastViewPanel controls precede the
# score wrapper, and the score wrapper precedes the team wrapper.
for earlier in ("direct_chrome", "possession_diagram", "possession_figures_text"):
    relation = _relation(earlier, "league_scores_static")
    _SOURCE_CLOSED_PAIRWISE_RELATIONS[
        frozenset((earlier, "league_scores_static"))
    ] = relation
for later in ("team_table_static", "team_table_energy"):
    relation = _relation("league_scores_static", later)
    _SOURCE_CLOSED_PAIRWISE_RELATIONS[
        frozenset(("league_scores_static", later))
    ] = relation

POSSESSION_DIAGRAM_BEFORE_FIGURES = _SOURCE_CLOSED_PAIRWISE_RELATIONS[
    frozenset(("possession_diagram", "possession_figures_text"))
]


def source_closed_pairwise_order(
    first_component: str,
    second_component: str,
) -> FastViewPairwiseDrawOrder:
    """Return a source-closed relation among current raster component families.

    Either argument order is accepted for lookup. The returned record always
    retains native earlier->later paint order. Alternative TeamTable raster
    aliases intentionally have no relation to each other.
    """
    if not isinstance(first_component, str) or not isinstance(second_component, str):
        raise FastViewDrawOrderError("component names must be strings")
    requested = frozenset((first_component, second_component))
    if len(requested) != 2:
        raise FastViewDrawOrderError(
            "cross-component order remains unresolved for this pair"
        )
    try:
        return _SOURCE_CLOSED_PAIRWISE_RELATIONS[requested]
    except KeyError as exc:
        raise FastViewDrawOrderError(
            "cross-component order remains unresolved for this pair"
        ) from exc


def later_component(first_component: str, second_component: str) -> str:
    """Return the source-proven later-drawn component for a known pair."""
    return source_closed_pairwise_order(first_component, second_component).later_component
