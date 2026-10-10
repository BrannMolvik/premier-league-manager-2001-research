"""Source-backed fresh PSquadScreen top-control composition."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_decoder import EA444DecodedImage
from gate13_ea444_staged_rasters import decode_staged_or_original as decode_ea444
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from ea_font import EAFont
from ea_language_strings import parse_language_pair
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
    SQUAD_VISIBLE_ROW_Y_ORIGINS,
    SQUAD_FIRST_ROSTER_RECT, SQUAD_RESERVE_ROSTER_RECT,
)
from original_squad_row_style import (
    load_verified_squad_row_text_resources, _clip_mask, SQUAD_ROW_FONT_ATLAS_SIZE,
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

SQUAD_FIRST_TITLE_PATH = 'FM2001_Art/Generic/GenericButtonsAndBars/title_bar_7.444'
SQUAD_FIRST_TITLE_SHA256 = '2b08a35ab9eed1093a95a7db96fade138fc2bef9212c106463ef755d4201cecf'
SQUAD_FIRST_GRID_PATH = 'FM2001_Art/Coaching/stats/stats_grid_disabled.444'
SQUAD_FIRST_GRID_SHA256 = '4fe16ef35b5ee5da748c9de81a14897e162d2d15e73cd143190dfb97a23822a7'


@dataclass(frozen=True)
class OriginalSquadTopResources:
    atlas: EA444DecodedImage
    font: EAFont
    first_roster_title: EA444DecodedImage | None = None
    first_roster_grid: EA444DecodedImage | None = None
    first_roster_title_font: EAFont | None = None

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
        chrome = (self.first_roster_title, self.first_roster_grid, self.first_roster_title_font)
        if any(item is not None for item in chrome):
            if any(item is None for item in chrome):
                raise OriginalSquadTopControlsError('Incomplete first-roster chrome resources')
            if (self.first_roster_title.width, self.first_roster_title.height) != (226, 20):
                raise OriginalSquadTopControlsError('First-roster title geometry mismatch')
            if (self.first_roster_grid.width, self.first_roster_grid.height) != (729, 16):
                raise OriginalSquadTopControlsError('First-roster grid geometry mismatch')
            font = self.first_roster_title_font
            if (font.atlas_width, font.atlas_height) != SQUAD_ROW_FONT_ATLAS_SIZE:
                raise OriginalSquadTopControlsError('First-roster title font mismatch')


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
    strings, indices = parse_language_pair((root / 'English.str').read_bytes(),
                                           (root / 'English.idx').read_bytes())
    if (indices.resolve(strings, 166) != 'First Team'
            or indices.resolve(strings, 168) != 'Reserves'):
        raise OriginalSquadTopControlsError('First-roster original language binding mismatch')
    executable = Path(original_executable).read_bytes()
    atlas = decode_ea444(
        (root / resource.source_path).read_bytes(),
        tables=tables_from_original_executable(executable),
        quant=quantization_from_verified_executable(executable),
    )
    def chrome(path, expected_hash, expected_size):
        raw = (root / path).read_bytes()
        if len(raw) != expected_size or sha256(raw).hexdigest() != expected_hash:
            raise OriginalSquadTopControlsError('Original Squad chrome identity mismatch')
        return decode_ea444(raw, tables=tables_from_original_executable(executable),
                           quant=quantization_from_verified_executable(executable))
    return OriginalSquadTopResources(atlas=atlas, font=_validate_font(root),
        first_roster_title=chrome(SQUAD_FIRST_TITLE_PATH, SQUAD_FIRST_TITLE_SHA256, 2872),
        first_roster_grid=chrome(SQUAD_FIRST_GRID_PATH, SQUAD_FIRST_GRID_SHA256, 12324),
        first_roster_title_font=load_verified_squad_row_text_resources(root).font)


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


def squad_button_frame_png(resources: OriginalSquadTopResources, source_index: int) -> bytes:
    """Crop only one source bitmap; do not rerasterize roster/text on each tick."""
    if not isinstance(resources, OriginalSquadTopResources) or type(source_index) is not int:
        raise OriginalSquadTopControlsError('Verified Squad resources/source frame required')
    return encode_rgba_png(*SQUAD_BUTTON_FRAME_SIZE, _crop_frame(resources.atlas, source_index))


def build_fresh_squad_top_render(
    resources: OriginalSquadTopResources,
    *, include_reserve: bool = False,
    source_frames: tuple[int, int, int] = SQUAD_BUTTON_INITIAL_SOURCE_FRAMES,
) -> OriginalSquadTopRender:
    """Compose the combined view, including its live ordinary hover subframes."""
    if not isinstance(resources, OriginalSquadTopResources):
        raise OriginalSquadTopControlsError(
            "Squad top rendering requires verified original resources"
        )
    if type(include_reserve) is not bool:
        raise OriginalSquadTopControlsError('Explicit native paired-list visibility is required')
    if (not isinstance(source_frames, tuple) or len(source_frames) != 3
            or any(type(value) is not int for value in source_frames)
            or source_frames[0] != 11
            or any(not 0 <= value <= 10 for value in source_frames[1:])):
        raise OriginalSquadTopControlsError('Unqualified combined-view Squad tab frames')
    panel_x, panel_y, _panel_w, _panel_h = SQUAD_PANEL_RECT
    width, height = SQUAD_BUTTON_FRAME_SIZE
    line_height = resources.font.native_line_height()
    overlays: list[OriginalSquadTopOverlay] = []

    if resources.first_roster_title is not None:
        # PSquadList 4B506D -> 5D6050 -> 5D5EB0: title_bar_7 at local
        # (0,126), wrapper 946B70 (226x20), First Team / English.idx[166].
        title = resources.first_roster_title
        font = resources.first_roster_title_font
        # 4B520F..4B5670 installs 20 pictures at y=154+17*i, with
        # wrapper 942FD0 cropping the first 328x16 of the 729x16 original.
        grid = resources.first_roster_grid
        cropped_grid = b''.join(grid.rgba[y * 729 * 4:y * 729 * 4 + 328 * 4]
                                for y in range(16))
        png = encode_rgba_png(328, 16, cropped_grid)
        owners = [(0, SQUAD_FIRST_ROSTER_RECT, 'First Team')]
        if include_reserve:
            # Both owners execute the SAME 4B4FE0 setup. The constructor's
            # discriminator +98C selects 984560/984558 at 4B5052..4B506D;
            # source language loader 637574/6375B6 binds idx166/idx168.
            owners.append((1, SQUAD_RESERVE_ROSTER_RECT, 'Reserves'))
        for control_id, owner, caption in owners:
            rect = (panel_x + owner.x, panel_y + owner.y + 126, 226, 20)
            overlays.append(OriginalSquadTopOverlay('roster_title', control_id, caption,
                *rect, encode_rgba_png(226, 20, title.rgba), SQUAD_FIRST_TITLE_PATH, 0))
            mask = font.render_text_alpha(caption)
            # 5D5EB0: font 9197E0, flags 2001, white, inset (6,0).
            clipped = _clip_mask(mask, line_x=rect[0] + 6,
                line_y=rect[1] + 10 - font.native_line_height() // 2, rect=rect)
            if clipped is not None:
                x, y, w, h, alpha = clipped
                overlays.append(OriginalSquadTopOverlay('roster_title_text', control_id, caption,
                    x, y, w, h, encode_rgba_png(w, h, endpoint_text_rgba(alpha, 0xffff)),
                    'Fonts/Zurich_BdXCn_BT_18pixel.fnt', None, 0xffff))
            for y in SQUAD_VISIBLE_ROW_Y_ORIGINS:
                overlays.append(OriginalSquadTopOverlay('roster_grid', control_id, '',
                    rect[0], panel_y + owner.y + y, 328, 16, png, SQUAD_FIRST_GRID_PATH, 0))

    for button, group, source_index in zip(
        SQUAD_BUTTONS,
        SQUAD_BUTTON_INITIAL_GROUPS,
        source_frames,
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
