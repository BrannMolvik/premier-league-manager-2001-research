"""Source-backed fresh PSquadScreen top-control composition."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_decoder import EA444DecodedImage, decode_ea444
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from ea_font import EAFont
from gate13_original_pixel_preview import encode_rgba_png
from original_live_debug_view import endpoint_text_rgba
from original_pmenu_chrome import (
    PMENU_FONT_ATLAS_SIZE,
    PMENU_FONT_BYTE_SIZE,
    PMENU_FONT_NATIVE_LINE_HEIGHT,
    PMENU_FONT_SHA256,
    PMENU_FONT_SOURCE_PATH,
)
from original_squad_resources import (
    SQUAD_BUTTONS,
    SQUAD_PANEL_RECT,
    SQUAD_RESOURCES,
    validate_imported_original_squad_resources,
)


class OriginalSquadTopControlsError(ValueError):
    pass


SQUAD_BUTTON_ATLAS_PATH = "FM2001_Art/Generic/GenericButtonsAndBars/squad_but_anim.444"
SQUAD_BUTTON_FRAME_SIZE = (73, 25)
SQUAD_BUTTON_FRAME_COUNT = 23
SQUAD_BUTTON_VFTABLE_VA = 0x7BE814
SQUAD_BUTTON_STATE_TOGGLE_VA = 0x652D80
SQUAD_BUTTON_STATE_MASK = 0x8000
SQUAD_BUTTON_GROUP_SELECTOR_VA = 0x652AE0
SQUAD_BUTTON_GROUP_LENGTH_VA = 0x652BC0
SQUAD_BUTTON_SOURCE_OFFSET_VA = 0x5D4D70
SQUAD_BUTTON_TEXT_STYLE = 0
SQUAD_BUTTON_NORMAL_COLOR_16 = 0xFFFF
SQUAD_BUTTON_SELECTED_COLOR_16 = 0x0000
SQUAD_BUTTON_INITIAL_GROUPS = (1, 0, 0)
SQUAD_BUTTON_INITIAL_SOURCE_FRAMES = (11, 0, 0)


@dataclass(frozen=True)
class OriginalSquadTopResources:
    atlas: EA444DecodedImage
    font: EAFont

    def __post_init__(self) -> None:
        if (self.atlas.width, self.atlas.height) != (
            SQUAD_BUTTON_FRAME_SIZE[0],
            SQUAD_BUTTON_FRAME_SIZE[1] * SQUAD_BUTTON_FRAME_COUNT,
        ):
            raise OriginalSquadTopControlsError("Squad button atlas geometry mismatch")
        if (self.font.atlas_width, self.font.atlas_height) != PMENU_FONT_ATLAS_SIZE:
            raise OriginalSquadTopControlsError("Squad button font geometry mismatch")
        if self.font.native_line_height() != PMENU_FONT_NATIVE_LINE_HEIGHT:
            raise OriginalSquadTopControlsError("Squad button font metrics mismatch")


@dataclass(frozen=True)
class OriginalSquadTopOverlay:
    role: str
    control_id: int
    original_text: str
    x: int
    y: int
    width: int
    height: int
    png: bytes
    source_path: str
    source_index: int | None
    native_color_16: int | None = None


@dataclass(frozen=True)
class OriginalSquadTopRender:
    panel_rect: tuple[int, int, int, int]
    overlays: tuple[OriginalSquadTopOverlay, ...]

    @property
    def photo_dimensions(self) -> tuple[tuple[int, int], ...]:
        return tuple((item.width, item.height) for item in self.overlays)


def _button_resource():
    matches = [
        resource for resource in SQUAD_RESOURCES
        if resource.source_path == SQUAD_BUTTON_ATLAS_PATH
    ]
    if len(matches) != 1:
        raise OriginalSquadTopControlsError("Squad button atlas ownership is ambiguous")
    return matches[0]


def _validate_font(source_root: Path) -> EAFont:
    data = (source_root / PMENU_FONT_SOURCE_PATH).read_bytes()
    if len(data) != PMENU_FONT_BYTE_SIZE or sha256(data).hexdigest() != PMENU_FONT_SHA256:
        raise OriginalSquadTopControlsError("Squad button font source mismatch")
    font = EAFont.from_bytes(data)
    if (font.atlas_width, font.atlas_height) != PMENU_FONT_ATLAS_SIZE:
        raise OriginalSquadTopControlsError("Squad button font atlas mismatch")
    if font.native_line_height() != PMENU_FONT_NATIVE_LINE_HEIGHT:
        raise OriginalSquadTopControlsError("Squad button font line-height mismatch")
    return font


def load_verified_squad_top_resources(
    source_root: str | Path,
    original_executable: str | Path,
) -> OriginalSquadTopResources:
    root = Path(source_root)
    validate_imported_original_squad_resources(root)
    resource = _button_resource()
    executable = Path(original_executable).read_bytes()
    atlas = decode_ea444(
        (root / resource.source_path).read_bytes(),
        tables=tables_from_original_executable(executable),
        quant=quantization_from_verified_executable(executable),
    )
    return OriginalSquadTopResources(atlas=atlas, font=_validate_font(root))


def _crop_frame(atlas: EA444DecodedImage, source_index: int) -> bytes:
    width, height = SQUAD_BUTTON_FRAME_SIZE
    if not 0 <= source_index < SQUAD_BUTTON_FRAME_COUNT:
        raise OriginalSquadTopControlsError("Squad source-frame index is invalid")
    y0 = source_index * height
    stride = atlas.width * 4
    return b"".join(
        atlas.rgba[(y0 + row) * stride:(y0 + row) * stride + width * 4]
        for row in range(height)
    )


def build_fresh_squad_top_render(
    resources: OriginalSquadTopResources,
) -> OriginalSquadTopRender:
    """Compose the native initial state: control 3 selected, controls 4/5 normal."""
    if not isinstance(resources, OriginalSquadTopResources):
        raise OriginalSquadTopControlsError(
            "Squad top rendering requires verified original resources"
        )
    panel_x, panel_y, _panel_w, _panel_h = SQUAD_PANEL_RECT
    width, height = SQUAD_BUTTON_FRAME_SIZE
    line_height = resources.font.native_line_height()
    overlays: list[OriginalSquadTopOverlay] = []

    for button, group, source_index in zip(
        SQUAD_BUTTONS,
        SQUAD_BUTTON_INITIAL_GROUPS,
        SQUAD_BUTTON_INITIAL_SOURCE_FRAMES,
    ):
        x = panel_x + button.origin[0]
        y = panel_y + button.origin[1]
        rgba = _crop_frame(resources.atlas, source_index)
        overlays.append(
            OriginalSquadTopOverlay(
                "button", button.control_id, button.original_text,
                x, y, width, height,
                encode_rgba_png(width, height, rgba),
                SQUAD_BUTTON_ATLAS_PATH, source_index,
            )
        )

        mask = resources.font.render_text_alpha(button.original_text)
        text_x = x + (width - resources.font.measure_text(button.original_text)) // 2
        text_y = y + (height - line_height) // 2
        color = SQUAD_BUTTON_SELECTED_COLOR_16 if group == 1 else SQUAD_BUTTON_NORMAL_COLOR_16
        overlays.append(
            OriginalSquadTopOverlay(
                "text", button.control_id, button.original_text,
                text_x, text_y, mask.width, mask.height,
                encode_rgba_png(
                    mask.width, mask.height,
                    endpoint_text_rgba(mask.alpha, color),
                ),
                PMENU_FONT_SOURCE_PATH, None, color,
            )
        )
    return OriginalSquadTopRender(SQUAD_PANEL_RECT, tuple(overlays))
