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
# Four original eleven-row arrow object arrays and their genuine high
# input event producers. Vtable +0x08 child constructors create the sprites,
# while reached FastViewTactics::0x52E280 assigns each child event+0x20.
NATIVE_HUMAN_PLAYER_ARROW_PARENT_OFFSETS = (0x1CF4, 0x2038, 0x34D8, 0x3CEC)
NATIVE_HUMAN_PLAYER_ARROW_EVENT_BASES = (0x246E8E, 0x247276, 0x2466BE, 0x246AA6)
NATIVE_HUMAN_PLAYER_ARROW_EVENT_FIELD_OFFSET = 0x20
# The fourth arrow x is source-calculated from [0x947304]+0x1A4, not
# a hardcoded number or necessarily equal to the third arrow's right edge.
NATIVE_RIGHT_VARIANT2_BASE_GLOBAL_VA = 0x947304
NATIVE_RIGHT_VARIANT2_X_ADDEND = 0x1A4
NATIVE_RIGHT_VARIANT2_BOX_RESOURCE_PATH = "FM2001_Art/Generic/GenericButtonsAndBars/name_input_box_7.444"
NATIVE_RIGHT_VARIANT2_SOURCE_INITIAL_WIDTH = 124
NATIVE_RIGHT_VARIANT2_SOURCE_INITIAL_X = 124 + 0x1A4


# These eight actual native input control positions are distinct from the
# player-row arrows. Native 0x52E3F0 dispatch IDs 61..68 edit four tactical
# numeric fields; their constructors register these exact IDs and 0x64F380
# stores the original source coordinates. The original hit-test and final
# artwork crop are not asserted by this contract.
# Event61..68 controls are NOT reused eleven-player tactics_arrow_* sprites.
# Their reached native owner is GenericButtonsAndBars/scroller_hori.444;
# the constructor crops one 25x18 region from its original 100x36 atlas.
NATIVE_HUMAN_TACTICS_SCROLLER_ART = "FM2001_Art/Generic/GenericButtonsAndBars/scroller_hori.444"
NATIVE_HUMAN_TACTICS_SCROLLER_ATLAS_SIZE = (100, 36)
NATIVE_HUMAN_TACTICS_SCROLLER_CROP_SIZE = (25, 18)
NATIVE_HUMAN_TACTICS_SCROLLER_LEFT_OWNER = 0x947050
NATIVE_HUMAN_TACTICS_SCROLLER_RIGHT_OWNER = 0x947030
NATIVE_HUMAN_TACTICS_SCROLLER_LEFT_SOURCE_Y = 0
NATIVE_HUMAN_TACTICS_SCROLLER_RIGHT_SOURCE_Y = 18

NATIVE_HUMAN_TACTICS_SELECTOR_CONTROL_POSITIONS = (
    (61, 576, 278), (62, 733, 278),
    (63, 576, 334), (64, 733, 334),
    (65, 576, 390), (66, 733, 390),
    (67, 576, 446), (68, 733, 446),
)


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

    @property
    def source_original_native_event_id(self) -> int | None:
        """Source-reached player-row child event; unrelated bottom pair = unknown."""
        if self.source_row is None:
            return None
        if type(self.source_row) is not int or not (0 <= self.source_row < NATIVE_TACTICS_PLAYER_ROWS):
            raise ValueError("unverified original native player-row index")
        return NATIVE_HUMAN_PLAYER_ARROW_EVENT_BASES[self.arrow_variant_index] + self.source_row

    @property
    def source_original_parent_offset(self) -> int | None:
        if self.source_row is None:
            return None
        if type(self.source_row) is not int or not (0 <= self.source_row < NATIVE_TACTICS_PLAYER_ROWS):
            raise ValueError("unverified original native player-row index")
        return (NATIVE_HUMAN_PLAYER_ARROW_PARENT_OFFSETS[self.arrow_variant_index]
                + self.source_row * 0x4C)

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

# Original PictureControl child 0x651F40 selects one of two WORD frames using
# native base-control flag bit2 (source getter 0x64F590). This is NOT a
# designation of mouse hover/press; that semantic requires a separate trace.
NATIVE_FASTVIEW_ARROW_FRAME_CONTROL_SOURCE_VA = 0x651F40
NATIVE_FASTVIEW_ARROW_FRAME_FLAG_SOURCE_VA = 0x64F590
NATIVE_FASTVIEW_ARROW_FRAME_REFRESH_SOURCE_VA = 0x64F600
NATIVE_FASTVIEW_ARROW_FRAME_FLAG_MASK = 0x04


def original_fastview_arrow_frame_word_for_native_flags(
    native_flags: int,
    frame_word_at_44: int,
    frame_word_at_46: int,
) -> int:
    """Source-exact frame WORD read, not synthetic pointer-state interpretation.

    Source 0x64F590 extracts (control+0x18 >> 2) & 1.
    Source 0x651F40 uses +0x46 when that bit is set, otherwise +0x44.
    This function does not touch the original control or draw any pixels.
    """
    if type(native_flags) is not int or not (0 <= native_flags <= 0xFFFFFFFF):
        raise ValueError("authentic unsigned source DWORD flags required")
    for value in (frame_word_at_44, frame_word_at_46):
        if type(value) is not int or not (0 <= value <= 0xFFFF):
            raise ValueError("authentic unsigned 16-bit native frame index required")
    return frame_word_at_46 if (native_flags & NATIVE_FASTVIEW_ARROW_FRAME_FLAG_MASK) else frame_word_at_44


# Two additional authentic 11-row native controls. These are *not* the
# tactics-arrow sprites. Source constructor calls 0x6503F0 and 0x5D71A0
# take x80 and x133 respectively, with y278+17*row. Their original IDs
# are registered through distinct control+0x20 ownership routes.
# Graphics, native hit widths/heights and complete event side effects remain
# unverified; never paint arrow art or wire actions from these coordinates.
NATIVE_AUXILIARY_PLAYER_ROW_FAMILIES = (
    # source event base, parent object row0 offset, row stride, x, constructor
    (0x23D65A, 0x1A34, 0x40, 80, 0x6503F0),
    (0x8877AE, 0x263C, 0x44, 133, 0x5D71A0),
)
NATIVE_AUXILIARY_EVENT_FIELD_OFFSET = 0x20

# The first (source 0x6503F0) family is explicitly created with x/y and
# a 40x16 rectangle, which its wrapper passes to base 0x64F380.
# The second is NOT 40x16: 0x5D71A0 forwards the original input arg
# 0x877820 into 0x651A50, which reads that resource's +0x14 (width)
# and +0x18 (height) before 0x64F380. Do not invent those runtime values.
NATIVE_FIRST_AUXILIARY_ROW_SIZE = (40, 16)
NATIVE_SECOND_AUXILIARY_DIMENSIONS_OWNER_VA = 0x877820
NATIVE_SECOND_AUXILIARY_DIMENSIONS_OFFSETS = (0x14, 0x18)
NATIVE_SECOND_AUXILIARY_RECT_WRAPPER = 0x651A50



@dataclass(frozen=True)
class OriginalFastViewTacticsAuxiliaryRowControl:
    source_event_id: int
    source_row: int
    parent_offset: int
    native_x: int
    native_y: int
    source_constructor_va: int
    artwork_identity_verified: bool = False

    def native_source_rect_from_original_dimensions(
        self, *, original_resource_dimensions: tuple[int, int] | None = None
    ) -> tuple[int, int, int, int]:
        """Retain the native rectangle writer's source geometry, not a click.

        0x23D65A source constructor 0x6503F0 passes 40x16 explicitly.
        0x8877AE source constructor 0x5D71A0 obtains width/height from the
        original 0x877820 image owner. If the live original owner values are
        unknown, fail closed rather than substitute 40x16 or 800x600.
        No result here proves native pointer hit or mutable player effects.
        """
        if self.source_constructor_va == 0x6503F0:
            if original_resource_dimensions is not None:
                raise ValueError("first family rectangle does not use caller resource dimensions")
            width, height = NATIVE_FIRST_AUXILIARY_ROW_SIZE
        elif self.source_constructor_va == 0x5D71A0:
            if type(original_resource_dimensions) is not tuple or len(original_resource_dimensions) != 2:
                raise ValueError("original live resource width and height are required")
            width, height = original_resource_dimensions
            if any(type(v) is not int or not (0 < v <= 0xFFFFFFFF) for v in (width, height)):
                raise ValueError("only original unsigned resource dimensions can be supplied")
        else:
            raise ValueError("unrecognized original auxiliary native constructor")
        return (self.native_x, self.native_y, width, height)

    def __post_init__(self) -> None:
        if type(self.source_row) is not int or not (0 <= self.source_row < NATIVE_TACTICS_PLAYER_ROWS):
            raise ValueError("original auxiliary player-row index required")
        if self.artwork_identity_verified:
            raise ValueError("auxiliary event artwork identity not yet source proven")


def original_fastview_auxiliary_player_row_controls(
) -> tuple[OriginalFastViewTacticsAuxiliaryRowControl, ...]:
    """Source coordinates/event owners for 22 additional native controls.

    Does not equate x/y with an independently proven click rectangle; native
    constructors and owner child pointers need deeper resource/hit tracing.
    """
    positions = []
    for row in range(NATIVE_TACTICS_PLAYER_ROWS):
        for event_base, first_offset, stride, x, constructor_va in NATIVE_AUXILIARY_PLAYER_ROW_FAMILIES:
            positions.append(OriginalFastViewTacticsAuxiliaryRowControl(
                source_event_id=event_base + row,
                source_row=row,
                parent_offset=first_offset + stride * row,
                native_x=x,
                native_y=NATIVE_TACTICS_FIRST_PLAYER_Y + NATIVE_TACTICS_PLAYER_ROW_STEP * row,
                source_constructor_va=constructor_va,
            ))
    return tuple(positions)
