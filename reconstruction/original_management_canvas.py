"""Fixed 800x600 source-backed FM2001 management composition boundary.

The surrounding application-owned management background is still unresolved,
but the PMenu row presentation is now source-complete enough to render. This
module therefore composes only the exact imported row arrow/background assets
and recovered Zurich label masks while leaving every other management pixel
fail-closed.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ea444_decoder import EA444DecodedImage, decode_ea444
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from ea_font import EAFont, EATextMask
from front_end_state import FrontEndScreen
from gate13_original_pixel_preview import encode_rgba_png
from original_front_end_layout import SCREEN_SIZE
from original_management_presenter import (
    OriginalManagementPanelSnapshot,
    OriginalManagementPresenter,
)
from original_pmenu_chrome import (
    PMENU_CHILD_ARROW_RESOURCE,
    PMENU_CHILD_BOX_RESOURCE,
    PMENU_CHILD_TEXT_LAYOUT,
    PMENU_LIST_SCREEN_ORIGIN,
    PMENU_LIST_SIZE,
    PMENU_ROW_ARROW_RECT,
    PMENU_ROW_BOX_RECT,
    PMENU_TITLE_ARROW_RESOURCE,
    PMENU_TITLE_BOX_RESOURCE,
    PMENU_TITLE_TEXT_LAYOUT,
    OriginalPMenuResource,
    pmenu_arrow_state_from_bits,
    pmenu_background_row_index,
    pmenu_child_arrow_source_row,
    pmenu_title_arrow_source_row,
    validate_original_pmenu_resources,
    validate_original_pmenu_row_fonts,
)
from original_pmenu_presenter import OriginalPMenuSnapshot, OriginalPMenuVisibleRow
from original_squad_resources import SQUAD_PANEL_RECT


class OriginalManagementCanvasError(ValueError):
    """The management host cannot be built from the recovered source boundary."""


@dataclass(frozen=True)
class OriginalManagementCanvasFrame:
    screen_size: tuple[int, int]
    menu_rect: tuple[int, int, int, int]
    panel_rect: tuple[int, int, int, int] | None
    presentation: OriginalManagementPanelSnapshot
    surrounding_background_recovered: bool
    pmenu_text_placement_recovered: bool

    @property
    def complete_source_pixel_frame_available(self) -> bool:
        return (
            self.surrounding_background_recovered
            and self.pmenu_text_placement_recovered
            and self.panel_rect is not None
        )


@dataclass(frozen=True)
class OriginalPMenuRenderResources:
    """Decoded exact source art plus the two recovered concrete row fonts."""

    title_arrow: EA444DecodedImage
    title_box: EA444DecodedImage
    child_arrow: EA444DecodedImage
    child_box: EA444DecodedImage
    title_font: EAFont
    child_font: EAFont

    def __post_init__(self) -> None:
        expected_images = (
            (self.title_arrow, PMENU_TITLE_ARROW_RESOURCE),
            (self.title_box, PMENU_TITLE_BOX_RESOURCE),
            (self.child_arrow, PMENU_CHILD_ARROW_RESOURCE),
            (self.child_box, PMENU_CHILD_BOX_RESOURCE),
        )
        for decoded, resource in expected_images:
            if (decoded.width, decoded.height) != resource.size:
                raise OriginalManagementCanvasError(
                    f"Decoded PMenu resource geometry mismatch: {resource.source_path}"
                )
        for font, layout in (
            (self.title_font, PMENU_TITLE_TEXT_LAYOUT),
            (self.child_font, PMENU_CHILD_TEXT_LAYOUT),
        ):
            if (font.atlas_width, font.atlas_height) != layout.font_atlas_size:
                raise OriginalManagementCanvasError(
                    f"Decoded PMenu {layout.row_kind} font geometry mismatch"
                )
            if font.native_line_height() != layout.native_line_height:
                raise OriginalManagementCanvasError(
                    f"Decoded PMenu {layout.row_kind} font metrics mismatch"
                )


@dataclass(frozen=True)
class OriginalPMenuCanvasOverlay:
    role: str
    row_kind: str
    menu_id: int
    x: int
    y: int
    width: int
    height: int
    png: bytes
    source_path: str
    source_index: int | None
    native_color_16: int | None = None


@dataclass(frozen=True)
class OriginalPMenuCanvasRender:
    list_screen_origin: tuple[int, int]
    list_size: tuple[int, int]
    row_count: int
    overlays: tuple[OriginalPMenuCanvasOverlay, ...]

    @property
    def photo_dimensions(self) -> tuple[tuple[int, int], ...]:
        return tuple((item.width, item.height) for item in self.overlays)


def build_management_canvas_frame(
    presenter: OriginalManagementPresenter,
) -> OriginalManagementCanvasFrame:
    """Bind a live management presenter to the fixed original screen surface."""
    if not isinstance(presenter, OriginalManagementPresenter):
        raise OriginalManagementCanvasError(
            "Management canvas requires OriginalManagementPresenter"
        )
    session = presenter.session
    if session.navigation.screen is not FrontEndScreen.MANAGEMENT:
        raise OriginalManagementCanvasError(
            "Management canvas requires the recovered PMenu management state"
        )
    if not session.started:
        raise OriginalManagementCanvasError(
            "Management canvas requires a completed TeamSelect Start"
        )

    snapshot = presenter.snapshot()
    panel_rect = (
        SQUAD_PANEL_RECT
        if snapshot.panel_class == "PSquadScreen"
        else None
    )
    x, y = PMENU_LIST_SCREEN_ORIGIN
    width, height = PMENU_LIST_SIZE
    return OriginalManagementCanvasFrame(
        screen_size=SCREEN_SIZE,
        menu_rect=(x, y, width, height),
        panel_rect=panel_rect,
        presentation=snapshot,
        surrounding_background_recovered=False,
        # Recovery 177 closes both concrete row fonts, line origins and the
        # half-open (30,0)-(198,29) glyph clip. Pixel composition is handled
        # separately below and does not imply the surrounding shell is known.
        pmenu_text_placement_recovered=True,
    )


def load_verified_management_pmenu_resources(
    source_root: str | Path,
    original_executable: str | Path,
) -> OriginalPMenuRenderResources:
    """Decode only checksum-gated imported PMenu assets with the real EA tables."""
    root = Path(source_root)
    validate_original_pmenu_resources(root)
    validated_fonts = {
        layout.row_kind: font
        for layout, font in validate_original_pmenu_row_fonts(root)
    }

    executable = Path(original_executable).read_bytes()
    tables = tables_from_original_executable(executable)
    quant = quantization_from_verified_executable(executable)

    def decoded(resource: OriginalPMenuResource) -> EA444DecodedImage:
        image = decode_ea444(
            (root / resource.source_path).read_bytes(),
            tables=tables,
            quant=quant,
        )
        if (image.width, image.height) != resource.size:
            raise OriginalManagementCanvasError(
                f"Decoded PMenu resource geometry mismatch: {resource.source_path}"
            )
        return image

    return OriginalPMenuRenderResources(
        title_arrow=decoded(PMENU_TITLE_ARROW_RESOURCE),
        title_box=decoded(PMENU_TITLE_BOX_RESOURCE),
        child_arrow=decoded(PMENU_CHILD_ARROW_RESOURCE),
        child_box=decoded(PMENU_CHILD_BOX_RESOURCE),
        title_font=validated_fonts["title"],
        child_font=validated_fonts["child"],
    )


def _crop_rgba(
    source: EA444DecodedImage,
    *,
    x: int,
    y: int,
    width: int,
    height: int,
) -> bytes:
    if (
        min(x, y, width, height) < 0
        or width == 0
        or height == 0
        or x + width > source.width
        or y + height > source.height
    ):
        raise OriginalManagementCanvasError("PMenu source crop exceeds recovered atlas")
    stride = source.width * 4
    row_bytes = width * 4
    return b"".join(
        source.rgba[(y + row) * stride + x * 4:
                    (y + row) * stride + x * 4 + row_bytes]
        for row in range(height)
    )


def _clip_text_mask(
    mask: EATextMask,
    *,
    line_origin: tuple[int, int],
    clip_rect: tuple[int, int, int, int],
) -> tuple[int, int, int, int, bytes] | None:
    if mask.width <= 0 or mask.height <= 0:
        return None
    line_x, line_y = line_origin
    left, top, right, bottom = clip_rect
    out_left = max(line_x, left)
    out_top = max(line_y, top)
    out_right = min(line_x + mask.width, right)
    out_bottom = min(line_y + mask.height, bottom)
    if out_left >= out_right or out_top >= out_bottom:
        return None

    width = out_right - out_left
    height = out_bottom - out_top
    src_x = out_left - line_x
    src_y = out_top - line_y
    clipped = bytearray(width * height)
    for row in range(height):
        src = (src_y + row) * mask.width + src_x
        dst = row * width
        clipped[dst:dst + width] = mask.alpha[src:src + width]
    return out_left, out_top, width, height, bytes(clipped)


def _endpoint_text_rgba(alpha: bytes, native_color_16: int) -> bytes:
    if native_color_16 == 0x0000:
        channel = 0
    elif native_color_16 == 0xFFFF:
        channel = 255
    else:
        raise OriginalManagementCanvasError(
            "Only recovered native black/white PMenu text endpoints are renderable"
        )
    rgba = bytearray(len(alpha) * 4)
    for index, value in enumerate(alpha):
        pos = index * 4
        rgba[pos:pos + 4] = bytes((channel, channel, channel, value))
    return bytes(rgba)


def _row_art(
    row: OriginalPMenuVisibleRow,
    resources: OriginalPMenuRenderResources,
) -> tuple[OriginalPMenuCanvasOverlay, ...]:
    title = row.row_kind == "title"
    if not title and row.row_kind != "child":
        raise OriginalManagementCanvasError("PMenu row kind is not source-proven")

    arrow_resource = PMENU_TITLE_ARROW_RESOURCE if title else PMENU_CHILD_ARROW_RESOURCE
    box_resource = PMENU_TITLE_BOX_RESOURCE if title else PMENU_CHILD_BOX_RESOURCE
    arrow_image = resources.title_arrow if title else resources.child_arrow
    box_image = resources.title_box if title else resources.child_box
    font = resources.title_font if title else resources.child_font

    arrow_state = pmenu_arrow_state_from_bits(row.arrow_state_bits)
    if title:
        arrow_index = pmenu_title_arrow_source_row(arrow_state, 0)
    else:
        arrow_index = pmenu_child_arrow_source_row(arrow_state, 0)
    arrow_x, arrow_y, arrow_w, arrow_h = PMENU_ROW_ARROW_RECT
    arrow_rgba = _crop_rgba(
        arrow_image,
        x=0,
        y=arrow_index * arrow_resource.frame_height,
        width=arrow_w,
        # MenuTitleArrow advances source frames in 58px blocks, while the
        # concrete row control remains the recovered 30x29 destination.
        height=arrow_h,
    )

    background_index = pmenu_background_row_index(row.background_state_bits)
    box_x, box_y, box_w, box_h = PMENU_ROW_BOX_RECT
    box_rgba = _crop_rgba(
        box_image,
        x=0,
        y=background_index * box_resource.frame_height,
        width=box_w,
        height=box_h,
    )

    overlays = [
        OriginalPMenuCanvasOverlay(
            role="arrow",
            row_kind=row.row_kind,
            menu_id=row.menu_id,
            x=arrow_x,
            y=row.y + arrow_y,
            width=arrow_w,
            height=arrow_h,
            png=encode_rgba_png(arrow_w, arrow_h, arrow_rgba),
            source_path=arrow_resource.source_path,
            source_index=arrow_index,
        ),
        OriginalPMenuCanvasOverlay(
            role="background",
            row_kind=row.row_kind,
            menu_id=row.menu_id,
            x=box_x,
            y=row.y + box_y,
            width=box_w,
            height=box_h,
            png=encode_rgba_png(box_w, box_h, box_rgba),
            source_path=box_resource.source_path,
            source_index=background_index,
        ),
    ]

    mask = font.render_text_alpha(row.caption)
    clipped = _clip_text_mask(
        mask,
        line_origin=row.text_line_origin,
        clip_rect=row.text_clip_rect,
    )
    if clipped is None:
        raise OriginalManagementCanvasError(
            f"Recovered PMenu label clipped to nothing: {row.caption!r}"
        )
    text_x, text_y, text_w, text_h, alpha = clipped
    overlays.append(
        OriginalPMenuCanvasOverlay(
            role="text",
            row_kind=row.row_kind,
            menu_id=row.menu_id,
            x=text_x,
            y=text_y,
            width=text_w,
            height=text_h,
            png=encode_rgba_png(
                text_w,
                text_h,
                _endpoint_text_rgba(alpha, row.text_color_16),
            ),
            source_path=row.font_source_path,
            source_index=None,
            native_color_16=row.text_color_16,
        )
    )
    return tuple(overlays)


def build_management_pmenu_render(
    frame: OriginalManagementCanvasFrame,
    resources: OriginalPMenuRenderResources,
) -> OriginalPMenuCanvasRender:
    """Compose only the recovered live PMenu rows, never substitute shell pixels."""
    if not isinstance(frame, OriginalManagementCanvasFrame):
        raise OriginalManagementCanvasError(
            "PMenu rendering requires an OriginalManagementCanvasFrame"
        )
    if not isinstance(resources, OriginalPMenuRenderResources):
        raise OriginalManagementCanvasError(
            "PMenu rendering requires verified decoded original resources"
        )
    if not frame.pmenu_text_placement_recovered:
        raise OriginalManagementCanvasError(
            "PMenu renderer requires recovered native text placement"
        )

    menu: OriginalPMenuSnapshot = frame.presentation.menu
    if menu.list_screen_origin != PMENU_LIST_SCREEN_ORIGIN or menu.list_size != PMENU_LIST_SIZE:
        raise OriginalManagementCanvasError("PMenu presenter geometry drifted from source")

    overlays: list[OriginalPMenuCanvasOverlay] = []
    for row in menu.rows:
        overlays.extend(_row_art(row, resources))
    return OriginalPMenuCanvasRender(
        list_screen_origin=menu.list_screen_origin,
        list_size=menu.list_size,
        row_count=len(menu.rows),
        overlays=tuple(overlays),
    )
