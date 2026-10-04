"""Source-closed outer FastViewPanel draw-array registration order.

The original generic parent appends visible controls to its +0x1C/+0x38 draw
array and traverses that array forward. Recovery 283 exhaustively accounts for
the outer FastViewPanel registrations reached during the source-qualified setup
path.

This is an outer-array contract only. FastViewScores and FastViewTeam each
delegate to their own nested child arrays at their wrapper positions. Their
complete internal child inventories remain separate work, so this module does
not promote global_fastview_z_order_recovered or complete-frame fidelity.
"""
from __future__ import annotations

from dataclasses import dataclass


class FastViewOuterDrawOrderError(ValueError):
    pass


FASTVIEW_PANEL_SETUP_VA = 0x51FA70
PARENT_DRAW_REGISTER_VA = 0x5274C0
PICTURE_CONTROL_CONSTRUCTOR_VA = 0x527730
TEXT_CONTROL_CONSTRUCTOR_VA = 0x527960

TOP_BAR_OWNER_CALL_VA = 0x51FDA3
TICKER_OWNER_CALL_VA = 0x51FE31

CLOCK_OWNER_CALL_VA = 0x51FE7B
CLOCK_CONSTRUCTOR_VA = 0x51EB90
CLOCK_TEXT_REGISTER_CALL_VA = 0x51EC30

EMBEDDED_BUTTON0_PARENT_OFFSET = 0x388
EMBEDDED_BUTTON0_REGISTER_CALL_VA = 0x51FFE5
EMBEDDED_BUTTON0_CONSTRUCTOR_CALL_VA = 0x520061
EMBEDDED_BUTTON1_PARENT_OFFSET = 0x3D4
EMBEDDED_BUTTON1_REGISTER_CALL_VA = 0x52000B
EMBEDDED_BUTTON1_CONSTRUCTOR_CALL_VA = 0x52009F
EMBEDDED_BUTTON_CONSTRUCTOR_VA = 0x652FD0

POSSESSION_DIAGRAM_OWNER_CALL_VA = 0x5206CD
POSSESSION_DIAGRAM_REGISTER_CALLS = (
    0x522894,
    0x52291D,
    0x5229AA,
    0x522A33,
)

POSSESSION_FIGURES_OWNER_CALL_VA = 0x520802
POSSESSION_FIGURES_REGISTER_CALLS = (
    0x51E876,
    0x51E900,
    0x51E990,
)

DIRECT_TEXT0_REGISTER_CALL_VA = 0x520A16
DIRECT_TEXT0_RECT = (250, 45, 550, 75)
DIRECT_TEXT1_REGISTER_CALL_VA = 0x520A69
DIRECT_TEXT1_RECT = (250, 70, 550, 86)

SCORES_SUBPANEL_REGISTER_CALL_VA = 0x520DEF
SCORES_SUBPANEL_PARENT_OFFSET = 0x98
TEAM_SUBPANEL_REGISTER_CALL_VA = 0x520EEF
TEAM_SUBPANEL_PARENT_OFFSET = 0x9C

POST_TEAM_CONTROL_ARRAY_PARENT_OFFSET = 0x424
POST_TEAM_CONTROL_STRIDE = 0x54
POST_TEAM_CONTROL_COUNT = 2
POST_TEAM_REGISTER_LOOP_CALL_VA = 0x520F8B
POST_TEAM_CONTROL_CONSTRUCTOR_VA = 0x652C50


@dataclass(frozen=True)
class FastViewOuterDrawEntry:
    rank: int
    identity: str
    registration_kind: str
    registration_call_va: int
    owner_call_va: int | None = None
    parent_object_offset: int | None = None
    nested_subpanel: bool = False

    def __post_init__(self) -> None:
        if type(self.rank) is not int or self.rank < 0:
            raise FastViewOuterDrawOrderError("outer draw rank must be non-negative")
        if not isinstance(self.identity, str) or not self.identity:
            raise FastViewOuterDrawOrderError("outer draw identity must be non-empty")
        if self.registration_kind not in {
            "picture_control_constructor",
            "text_control_constructor",
            "manual_parent_append",
            "subpanel_wrapper_append",
        }:
            raise FastViewOuterDrawOrderError("unknown outer registration kind")
        if type(self.registration_call_va) is not int:
            raise FastViewOuterDrawOrderError("registration call VA must be integer")
        if self.owner_call_va is not None and type(self.owner_call_va) is not int:
            raise FastViewOuterDrawOrderError("owner call VA must be integer or None")
        if self.parent_object_offset is not None and (
            type(self.parent_object_offset) is not int or self.parent_object_offset < 0
        ):
            raise FastViewOuterDrawOrderError(
                "parent object offset must be non-negative integer or None"
            )
        if type(self.nested_subpanel) is not bool:
            raise FastViewOuterDrawOrderError("nested_subpanel must be boolean")


def _build_outer_draw_entries() -> tuple[FastViewOuterDrawEntry, ...]:
    rows: list[FastViewOuterDrawEntry] = []

    def add(
        identity: str,
        kind: str,
        call_va: int,
        *,
        owner_call_va: int | None = None,
        parent_offset: int | None = None,
        nested_subpanel: bool = False,
    ) -> None:
        rows.append(
            FastViewOuterDrawEntry(
                rank=len(rows),
                identity=identity,
                registration_kind=kind,
                registration_call_va=call_va,
                owner_call_va=owner_call_va,
                parent_object_offset=parent_offset,
                nested_subpanel=nested_subpanel,
            )
        )

    add(
        "top_bar_picture",
        "picture_control_constructor",
        TOP_BAR_OWNER_CALL_VA,
    )
    add(
        "ticker_picture",
        "picture_control_constructor",
        TICKER_OWNER_CALL_VA,
    )
    add(
        "clock_text",
        "text_control_constructor",
        CLOCK_TEXT_REGISTER_CALL_VA,
        owner_call_va=CLOCK_OWNER_CALL_VA,
    )
    add(
        "embedded_button_0",
        "manual_parent_append",
        EMBEDDED_BUTTON0_REGISTER_CALL_VA,
        parent_offset=EMBEDDED_BUTTON0_PARENT_OFFSET,
    )
    add(
        "embedded_button_1",
        "manual_parent_append",
        EMBEDDED_BUTTON1_REGISTER_CALL_VA,
        parent_offset=EMBEDDED_BUTTON1_PARENT_OFFSET,
    )

    for index, call_va in enumerate(POSSESSION_DIAGRAM_REGISTER_CALLS):
        add(
            f"possession_diagram_picture_{index}",
            "picture_control_constructor",
            call_va,
            owner_call_va=POSSESSION_DIAGRAM_OWNER_CALL_VA,
        )

    for index, call_va in enumerate(POSSESSION_FIGURES_REGISTER_CALLS):
        add(
            f"possession_figures_text_{index}",
            "text_control_constructor",
            call_va,
            owner_call_va=POSSESSION_FIGURES_OWNER_CALL_VA,
        )

    add(
        "direct_text_0",
        "text_control_constructor",
        DIRECT_TEXT0_REGISTER_CALL_VA,
    )
    add(
        "direct_text_1",
        "text_control_constructor",
        DIRECT_TEXT1_REGISTER_CALL_VA,
    )
    add(
        "scores_subpanel",
        "subpanel_wrapper_append",
        SCORES_SUBPANEL_REGISTER_CALL_VA,
        parent_offset=SCORES_SUBPANEL_PARENT_OFFSET,
        nested_subpanel=True,
    )
    add(
        "team_subpanel",
        "subpanel_wrapper_append",
        TEAM_SUBPANEL_REGISTER_CALL_VA,
        parent_offset=TEAM_SUBPANEL_PARENT_OFFSET,
        nested_subpanel=True,
    )

    for index in range(POST_TEAM_CONTROL_COUNT):
        add(
            f"post_team_control_{index}",
            "manual_parent_append",
            POST_TEAM_REGISTER_LOOP_CALL_VA,
            parent_offset=(
                POST_TEAM_CONTROL_ARRAY_PARENT_OFFSET
                + index * POST_TEAM_CONTROL_STRIDE
            ),
        )

    return tuple(rows)


FASTVIEW_OUTER_DRAW_ENTRIES = _build_outer_draw_entries()
FASTVIEW_OUTER_DRAW_COUNT = 18


@dataclass(frozen=True)
class FastViewOuterDrawBoundary:
    outer_draw_array_exhaustively_recovered: bool = True
    outer_forward_order_recovered: bool = True
    score_subpanel_internal_inventory_complete: bool = False
    team_subpanel_internal_inventory_complete: bool = False
    global_fastview_z_order_recovered: bool = False
    complete_fastview_frame_recovered: bool = False

    def __post_init__(self) -> None:
        if not (
            self.outer_draw_array_exhaustively_recovered
            and self.outer_forward_order_recovered
        ):
            raise FastViewOuterDrawOrderError(
                "outer draw boundary cannot weaken recovered parent-array evidence"
            )
        if (
            self.score_subpanel_internal_inventory_complete
            or self.team_subpanel_internal_inventory_complete
            or self.global_fastview_z_order_recovered
            or self.complete_fastview_frame_recovered
        ):
            raise FastViewOuterDrawOrderError(
                "outer-array recovery cannot promote nested/global/frame completion"
            )


SOURCE_BOUNDARY = FastViewOuterDrawBoundary()


def outer_draw_rank(identity: str) -> int:
    if not isinstance(identity, str) or not identity:
        raise FastViewOuterDrawOrderError("identity must be non-empty string")
    for row in FASTVIEW_OUTER_DRAW_ENTRIES:
        if row.identity == identity:
            return row.rank
    raise FastViewOuterDrawOrderError("unknown outer FastView draw identity")


def outer_draw_before(first: str, second: str) -> bool:
    first_rank = outer_draw_rank(first)
    second_rank = outer_draw_rank(second)
    if first_rank == second_rank:
        raise FastViewOuterDrawOrderError(
            "outer draw comparison requires distinct identities"
        )
    return first_rank < second_rank
