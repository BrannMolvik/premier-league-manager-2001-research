"""Confirmed original FM2001 first-screen background composition.

Coordinates here are not screenshot estimates. PStartMenu is constructed by the
canonical executable at 0x5312A8..0x5312C2 with a 532x532 child rectangle at
(134, 34); TeamSelect is registered as an 800x600 root at 0x4C39BB..0x4C39D6,
and its original 800x558 background resource is attached at (0, 0) through
0x4D7D4F..0x4D7D58 -> 0x651BA0.

The global 800x600 Generic/bground.444 remains beneath those screen-specific
layers, matching the legacy front-end startup/background ownership. Controls
and text are deliberately separate until their exact source-backed placement
is recovered.
"""
from __future__ import annotations

from dataclasses import dataclass

from ea444_decoder import EA444DecodedImage


SCREEN_SIZE = (800, 600)

GLOBAL_BACKGROUND_PATH = "FM2001_Art/Generic/bground.444"
PSTARTMENU_BACKGROUND_PATH = (
    "FM2001_Art/Generic/main_menu/main_menu_bground.444"
)
TEAMSELECT_BACKGROUND_PATH = (
    "FM2001_Art/Generic/team_choice/background.444"
)


@dataclass(frozen=True)
class OriginalRect:
    x: int
    y: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height


PSTARTMENU_BACKGROUND_RECT = OriginalRect(134, 34, 532, 532)
TEAMSELECT_ROOT_RECT = OriginalRect(0, 0, 800, 600)
TEAMSELECT_BACKGROUND_RECT = OriginalRect(0, 0, 800, 558)

# PStartMenu 0x4C1BA0 constructs four primary Button@ease_2001 controls.
# 0x946590 is initialized at 0x5F4500 from the exact original
# GenericButtonsAndBars/button_type_1.444 (169x575) with 169x25 frames.
# The label globals are filled sequentially from English.idx by 0x635F30:
# 0x9847F8=IDX 0 Continue, 0x9847F4=IDX 1 Start New Game,
# 0x9847F0=IDX 2 Load Game, 0x9847E0=IDX 6 Quit to Windows.
PSTARTMENU_ACTION_ATLAS_PATH = (
    "FM2001_Art/Generic/GenericButtonsAndBars/button_type_1.444"
)
PSTARTMENU_ACTION_FRAME_SIZE = (169, 25)


@dataclass(frozen=True)
class OriginalMenuAction:
    event: int
    language_index: int
    rect: OriginalRect


PSTARTMENU_ACTIONS = (
    OriginalMenuAction(1, 0, OriginalRect(181, 478, 169, 25)),
    OriginalMenuAction(2, 1, OriginalRect(7, 478, 169, 25)),
    OriginalMenuAction(3, 2, OriginalRect(355, 478, 169, 25)),
    OriginalMenuAction(4, 6, OriginalRect(181, 508, 169, 25)),
)

# 0x4D7D82..0x4D80BF constructs sixteen hierarchy rows by repeatedly
# calling 0x4D8C60 with x=20 and y=78+30*i. 0x4D8C60 in turn binds the
# original choice_league animation/bar resources.
TEAMSELECT_HIERARCHY_ROW_ORIGINS = tuple(
    (20, 78 + 30 * index) for index in range(16)
)
# 0x4D7D82..0x4D80BF constructs these native child controls. These are
# executable setup facts, not screenshot measurements; source-frame states
# remain open.
TEAMSELECT_HIERARCHY_CONTROL_IDS = tuple(range(1, 17))
TEAMSELECT_HIERARCHY_OBJECT_OFFSETS = tuple(
    0x2A24 + 0x4C * index for index in range(16)
)
TEAMSELECT_CLUB_ROW_ORIGINS = tuple(
    (581, 78 + 20 * index) for index in range(24)
)
TEAMSELECT_CLUB_CONTROL_IDS = tuple(range(0x11, 0x29))
TEAMSELECT_CLUB_OBJECT_OFFSETS = tuple(
    0x2EE4 + 0x40 * index for index in range(24)
)

# Constructor 0x4D9290 fills the country globals in this order for the
# default/English locale. Names are resolved from the canonical database.
TEAMSELECT_ENGLISH_COUNTRY_ORDER = (
    (26, "England"), (66, "Scotland"), (33, "Germany"), (40, "Italy"),
    (73, "Spain"), (31, "France"), (24, "Holland"), (9, "Belgium"),
)
TEAMSELECT_HIERARCHY_ANIM_PATH = (
    "FM2001_Art/Generic/GenericButtonsAndBars/choice_league_but_anim.444"
)
TEAMSELECT_HIERARCHY_BARS_PATH = (
    "FM2001_Art/Generic/GenericButtonsAndBars/choice_league_but_bars.444"
)
TEAMSELECT_HIERARCHY_FRAME_SIZE = (30, 29)
TEAMSELECT_HIERARCHY_BARS_FRAME_SIZE = (168, 29)

# TeamSelect action controls at 0x4D885F..0x4D8921. The final two arguments
# passed into Button@ease_2001 setup 0x652FD0 are x then y: event 0x29 is
# (225,301), event 0x2A is (426,301). Both bind 0x941630, the recovered
# choice_start_anim.444 family, whose atlas is 150x736 with 150x32 frames.
TEAMSELECT_ACTION_ATLAS_PATH = (
    "FM2001_Art/Generic/GenericButtonsAndBars/choice_start_anim.444"
)
TEAMSELECT_ACTION_FRAME_SIZE = (150, 32)
TEAMSELECT_BACK_RECT = OriginalRect(225, 301, 150, 32)
TEAMSELECT_START_RECT = OriginalRect(426, 301, 150, 32)
TEAMSELECT_BACK_EVENT = 0x29
TEAMSELECT_START_EVENT = 0x2A


class OriginalFrontEndLayoutError(ValueError):
    pass


def _require_image(
    image: EA444DecodedImage, expected: OriginalRect | tuple[int, int], name: str
) -> None:
    size = (expected.width, expected.height) if isinstance(expected, OriginalRect) else expected
    if (image.width, image.height) != size:
        raise OriginalFrontEndLayoutError(
            f"{name} is {image.width}x{image.height}, expected {size[0]}x{size[1]}"
        )


def _overlay(
    canvas: bytearray,
    layer: EA444DecodedImage,
    rect: OriginalRect,
) -> None:
    width, height = SCREEN_SIZE
    if rect.x < 0 or rect.y < 0 or rect.right > width or rect.bottom > height:
        raise OriginalFrontEndLayoutError("Original layer exceeds the 800x600 surface")
    for y in range(layer.height):
        for x in range(layer.width):
            src = (y * layer.width + x) * 4
            alpha = layer.rgba[src + 3]
            if alpha == 0:
                continue
            dst = ((rect.y + y) * width + rect.x + x) * 4
            if alpha == 255:
                canvas[dst:dst + 4] = layer.rgba[src:src + 4]
                continue
            # Generic alpha path for future source assets; current backgrounds
            # are opaque. Integer rounding is explicit and deterministic.
            inv = 255 - alpha
            for channel in range(3):
                canvas[dst + channel] = (
                    layer.rgba[src + channel] * alpha
                    + canvas[dst + channel] * inv
                    + 127
                ) // 255
            canvas[dst + 3] = 255


def compose_pstartmenu_background(
    global_background: EA444DecodedImage,
    menu_background: EA444DecodedImage,
) -> bytes:
    _require_image(global_background, SCREEN_SIZE, "global background")
    _require_image(menu_background, PSTARTMENU_BACKGROUND_RECT, "PStartMenu background")
    canvas = bytearray(global_background.rgba)
    _overlay(canvas, menu_background, PSTARTMENU_BACKGROUND_RECT)
    return bytes(canvas)


def compose_teamselect_background(
    global_background: EA444DecodedImage,
    team_background: EA444DecodedImage,
) -> bytes:
    _require_image(global_background, SCREEN_SIZE, "global background")
    _require_image(team_background, TEAMSELECT_BACKGROUND_RECT, "TeamSelect background")
    canvas = bytearray(global_background.rgba)
    _overlay(canvas, team_background, TEAMSELECT_BACKGROUND_RECT)
    return bytes(canvas)
