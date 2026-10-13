"""Native FastView tactics control placement, from authenticated FM2001 PE source.

These are original constructor coordinates and resource identities, NOT a live
mouse event bridge, screenshot reconstruction, composited output, or evidence
that the 800x600 modal can already be played. No original assets are included.
"""
from __future__ import annotations

from dataclasses import dataclass

NATIVE_TACTICS_PANEL_RECT = (20, 139, 760, 400)
NATIVE_FASTVIEW_MODAL_SIZE = (800, 600)
NATIVE_ARROW_IMAGE_SIZE = (11, 48)
NATIVE_ARROW_FRAME_SIZE = (11, 16)
NATIVE_ARROW_RESOURCE_PATHS = (
    "FM2001_Art/FastView/tactics_arrow_left.444",
    "FM2001_Art/FastView/tactics_arrow_right.444",
    "FM2001_Art/FastView/tactics_arrow_left_2.444",
    "FM2001_Art/FastView/tactics_arrow_right_2.444",
)
NATIVE_HUMAN_POPUP = "FM2001_Art/FastView/tactics_popup_1.444"
NATIVE_CPU_POPUP = "FM2001_Art/FastView/tactics_popup_2.444"
NATIVE_TACTICS_FIRST_PLAYER_Y = 278
NATIVE_TACTICS_PLAYER_ROW_STEP = 17
NATIVE_TACTICS_PLAYER_ROWS = 11
# The fourth arrow x is source-calculated from [0x947304]+0x1A4, not
# a hardcoded number or necessarily equal to the third arrow's right edge.
NATIVE_RIGHT_VARIANT2_BASE_GLOBAL_VA = 0x947304
NATIVE_RIGHT_VARIANT2_X_ADDEND = 0x1A4
NATIVE_RIGHT_VARIANT2_BOX_RESOURCE_PATH = "FM2001_Art/Generic/GenericButtonsAndBars/name_input_box_7.444"
NATIVE_RIGHT_VARIANT2_SOURCE_INITIAL_WIDTH = 124
NATIVE_RIGHT_VARIANT2_SOURCE_INITIAL_X = 124 + 0x1A4


@dataclass(frozen=True)
class OriginalFastViewTacticsArrowPosition:
    source_row: int | None
    arrow_variant_index: int
    native_x: int | None
    native_y: int
    dynamic_x_global_va: int | None = None
    dynamic_x_addend: int = 0

    def __post_init__(self) -> None:
        if self.arrow_variant_index not in (0, 1, 2, 3):
            raise ValueError("unknown native FastView arrow")
        if self.native_x is None and self.dynamic_x_global_va is None:
            raise ValueError("unresolved x must preserve its native source owner")
        if self.native_x is not None and self.dynamic_x_global_va is not None:
            raise ValueError("native position cannot be both static and dynamic")

    def resolved_native_x(self, *, original_box_width: int | None = None) -> int:
        """Use caller-provided live width for dynamic original x, never invent it."""
        if self.dynamic_x_global_va is None:
            assert self.native_x is not None
            return self.native_x
        if type(original_box_width) is not int or original_box_width < 0:
            raise ValueError("original source dynamic box width required")
        return original_box_width + self.dynamic_x_addend


def original_fastview_player_arrow_positions() -> tuple[OriginalFastViewTacticsArrowPosition, ...]:
    """Eleven originally registered player-row control quartets.

    Geometry alone does not prove their user-facing label or accepted click.
    """
    arrows = []
    for index in range(NATIVE_TACTICS_PLAYER_ROWS):
        y = NATIVE_TACTICS_FIRST_PLAYER_Y + NATIVE_TACTICS_PLAYER_ROW_STEP * index
        arrows.extend((
            OriginalFastViewTacticsArrowPosition(index, 0, 69, y),
            OriginalFastViewTacticsArrowPosition(index, 1, 120, y),
            OriginalFastViewTacticsArrowPosition(index, 2, 407, y),
            OriginalFastViewTacticsArrowPosition(
                index, 3, None, y,
                NATIVE_RIGHT_VARIANT2_BASE_GLOBAL_VA,
                NATIVE_RIGHT_VARIANT2_X_ADDEND,
            ),
        ))
    return tuple(arrows)


def original_fastview_bottom_arrow_positions() -> tuple[OriginalFastViewTacticsArrowPosition, ...]:
    """Two separate original 0x946e90/0x946e50 controls, not player rows."""
    return (
        OriginalFastViewTacticsArrowPosition(None, 0, 303, 481),
        OriginalFastViewTacticsArrowPosition(None, 1, 379, 481),
    )
