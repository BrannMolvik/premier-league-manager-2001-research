"""Source-closed partial FastView cross-component draw order.

Private canonical-executable tracing closes one specific ordering relation:
PossessionDiagram PictureControls are registered before PossessionFigures text
controls in the same parent draw array, and the generic renderer traverses that
array forward. Therefore possession percentage text is drawn after the diagram.

This module records only that pairwise relation. It does not claim a global
FastView z-order, background ownership, blend rule, dynamic PictureControl
resize semantics, audio, or 3D choreography.
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

# Constructors that both register their control object through 0x5274C0.
PICTURE_CONTROL_CONSTRUCTOR_VA = 0x527730
TEXT_CONTROL_CONSTRUCTOR_VA = 0x527960
PICTURE_CONTROL_REGISTER_CALL_VA = 0x52782A
TEXT_CONTROL_REGISTER_CALL_VA = 0x527A15

# FastViewPanel owner construction order.
POSSESSION_DIAGRAM_OWNER_CALL_VA = 0x5206CD
POSSESSION_FIGURES_OWNER_CALL_VA = 0x520802
POSSESSION_DIAGRAM_CONSTRUCTOR_VA = 0x5227D0
POSSESSION_FIGURES_CONSTRUCTOR_VA = 0x51E7E0

# Slot +0x64 in both relevant generic control vtables dispatches the visible
# child through the generic render seam. This supports traversal ownership, not
# a cross-component alpha/blend rule.
PICTURE_CONTROL_VTABLE_VA = 0x7CAA5C
TEXT_CONTROL_VTABLE_VA = 0x7CAAF8
GENERIC_CHILD_RENDER_TARGET_VA = 0x64F6D0


@dataclass(frozen=True)
class FastViewPairwiseDrawOrder:
    earlier_component: str
    later_component: str
    same_parent_draw_array: bool
    registration_is_append_order: bool
    traversal_is_forward: bool
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
            self.same_parent_draw_array
            and self.registration_is_append_order
            and self.traversal_is_forward
        ):
            raise FastViewDrawOrderError(
                "source-closed pairwise order requires the complete registration/traversal chain"
            )
        if self.pixel_blend_rule_recovered or self.global_z_order_recovered:
            raise FastViewDrawOrderError(
                "pairwise possession order cannot promote blend or global z-order"
            )


POSSESSION_DIAGRAM_BEFORE_FIGURES = FastViewPairwiseDrawOrder(
    earlier_component="possession_diagram",
    later_component="possession_figures_text",
    same_parent_draw_array=True,
    registration_is_append_order=True,
    traversal_is_forward=True,
)


def source_closed_pairwise_order(
    first_component: str,
    second_component: str,
) -> FastViewPairwiseDrawOrder:
    """Return the one currently source-closed cross-component relation.

    Either argument order is accepted for lookup. The returned record always
    retains native earlier->later paint order.
    """
    if not isinstance(first_component, str) or not isinstance(second_component, str):
        raise FastViewDrawOrderError("component names must be strings")
    requested = frozenset((first_component, second_component))
    known = frozenset(
        (
            POSSESSION_DIAGRAM_BEFORE_FIGURES.earlier_component,
            POSSESSION_DIAGRAM_BEFORE_FIGURES.later_component,
        )
    )
    if requested != known or len(requested) != 2:
        raise FastViewDrawOrderError(
            "cross-component order remains unresolved for this pair"
        )
    return POSSESSION_DIAGRAM_BEFORE_FIGURES


def later_component(first_component: str, second_component: str) -> str:
    """Return the source-proven later-drawn component for the known pair."""
    return source_closed_pairwise_order(first_component, second_component).later_component
