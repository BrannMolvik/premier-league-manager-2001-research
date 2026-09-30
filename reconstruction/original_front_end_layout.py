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

# 0x4D7D82..0x4D80BF constructs sixteen hierarchy rows by repeatedly
# calling 0x4D8C60 with x=20 and y=78+30*i. 0x4D8C60 in turn binds the
# original choice_league animation/bar resources.
TEAMSELECT_HIERARCHY_ROW_ORIGINS = tuple(
    (20, 78 + 30 * index) for index in range(16)
)
TEAMSELECT_HIERARCHY_ANIM_PATH = (
    "FM2001_Art/Generic/GenericButtonsAndBars/choice_league_but_anim.444"
)
TEAMSELECT_HIERARCHY_BARS_PATH = (
    "FM2001_Art/Generic/GenericButtonsAndBars/choice_league_but_bars.444"
)
TEAMSELECT_HIERARCHY_FRAME_SIZE = (30, 29)
TEAMSELECT_HIERARCHY_BARS_FRAME_SIZE = (168, 29)


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
