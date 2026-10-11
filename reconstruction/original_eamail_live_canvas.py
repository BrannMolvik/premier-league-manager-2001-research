"""Source original EAMail eight-row normal/selected bitmap compositing for live host.

Selection is original 0x471B80 -> 0x470B40, normal 0x470B90; text,
preview, status icons and detail/action dialog remain intentionally absent.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ea444_decoder import EA444DecodedImage
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from gate13_ea444_staged_rasters import decode_staged_or_original
from gate13_original_pixel_preview import encode_rgba_png
from original_eamail_control_art import validate_original_eamail_control_art
from original_eamail_source_contract import (
    ORIGINAL_EAMAIL_GRID_RESOURCES,
    ORIGINAL_EAMAIL_ROW_RECT,
    ORIGINAL_EAMAIL_VISIBLE_ROWS,
    validate_original_eamail_grid_resources,
)
from original_eamail_native_row_fields import OriginalEAMNativeVisibleRowsSource


class OriginalEAMailCanvasError(ValueError):
    """Cannot render source original EAMail row art safely."""


@dataclass(frozen=True)
class OriginalEAMailRowArt:
    normal: EA444DecodedImage
    selected: EA444DecodedImage | None = None

    def __post_init__(self) -> None:
        for image in (self.normal, self.selected):
            if image is not None and (image.width, image.height) != ORIGINAL_EAMAIL_ROW_RECT[2:]:
                raise OriginalEAMailCanvasError("Original native row grid geometry drifted")


@dataclass(frozen=True)
class OriginalEAMailCanvasRowOverlay:
    native_node_serial: int
    x: int
    y: int
    width: int
    height: int
    png: bytes
    source_path: str
    native_full_text_and_art_rendered: bool = False
    native_selected: bool = False


def load_verified_original_eamail_row_art(
    source_root: str | Path,
    original_executable: str | Path,
) -> OriginalEAMailRowArt:
    """Decode original normal AND selected row bitmaps from verified source.

    Other original EAM controls exist but are not drawn as decorative guesses.
    """
    root = Path(source_root)
    validate_original_eamail_grid_resources(root)
    validate_original_eamail_control_art(root)
    normal, selected = ORIGINAL_EAMAIL_GRID_RESOURCES[:2]
    if ((normal.name, normal.source_wrapper_va) != ("normal", 0x945E30)
            or (selected.name, selected.source_wrapper_va) != ("selected", 0x945DF0)):
        raise OriginalEAMailCanvasError("Original native row bitmap mapping drifted")
    executable = Path(original_executable).read_bytes()
    quant = quantization_from_verified_executable(executable)
    tables = tables_from_original_executable(executable)

    def decoded(resource):
        return decode_staged_or_original(
            (root / resource.source_path).read_bytes(), tables=tables, quant=quant,
        )

    return OriginalEAMailRowArt(decoded(normal), decoded(selected))


def original_eamail_row_at_screen_point(
    visible: OriginalEAMNativeVisibleRowsSource,
    x: int,
    y: int,
) -> int | None:
    """Hit-test the native eight displayed 532x18 row-owner rectangles.

    0x46E680 constructs each row and 0x471B80 handles neutral row activation.
    Panel-local list origin (233,30) plus screen panel y148 has been verified.
    No mailbox/pending rows outside the projected native viewport are clickable.
    """
    if type(visible) is not OriginalEAMNativeVisibleRowsSource:
        raise OriginalEAMailCanvasError("Original delivered Inbox viewport required")
    if type(x) is not int or type(y) is not int:
        raise OriginalEAMailCanvasError("Original row pointer coordinates must be integers")
    for row in visible.native_rows:
        rx, ry, width, height = row.row_screen_rect
        if (width, height) != ORIGINAL_EAMAIL_ROW_RECT[2:]:
            raise OriginalEAMailCanvasError("Original native row hit rectangle drifted")
        if rx <= x < rx + width and ry <= y < ry + height:
            return row.original_internal_node_serial
    return None


def source_original_eamail_row_backgrounds(
    visible: OriginalEAMNativeVisibleRowsSource,
    art: OriginalEAMailRowArt,
    *,
    selected_node_serial: int | None = None,
) -> tuple[OriginalEAMailCanvasRowOverlay, ...]:
    """Use original normal 0x945E30 or selected 0x945DF0 row bitmap.

    Hover/disabled/status effects and glyphs are unqualified for this renderer.
    """
    if type(visible) is not OriginalEAMNativeVisibleRowsSource or type(art) is not OriginalEAMailRowArt:
        raise OriginalEAMailCanvasError("Source original Inbox rows and art required")
    if len(visible.native_rows) > ORIGINAL_EAMAIL_VISIBLE_ROWS:
        raise OriginalEAMailCanvasError("Native CMessageList has eight visible slots")
    expected = ORIGINAL_EAMAIL_GRID_RESOURCES[0]
    selected_resource = ORIGINAL_EAMAIL_GRID_RESOURCES[1]
    if selected_node_serial is not None and art.selected is None:
        raise OriginalEAMailCanvasError("Original selected bitmap is required")
    seen = set()
    png = encode_rgba_png(art.normal.width, art.normal.height, art.normal.rgba)
    selected_png = (None if art.selected is None else
                    encode_rgba_png(art.selected.width, art.selected.height, art.selected.rgba))
    layers = []
    for row in visible.native_rows:
        if (row.original_internal_node_serial in seen or
                row.source_default_background_va != expected.source_wrapper_va):
            raise OriginalEAMailCanvasError("Original normal row owner/bitmap mismatch")
        seen.add(row.original_internal_node_serial)
        x, y, w, h = row.row_screen_rect
        if (w, h) != ORIGINAL_EAMAIL_ROW_RECT[2:]:
            raise OriginalEAMailCanvasError("Original rendered row bounds mismatch")
        selected = row.original_internal_node_serial == selected_node_serial
        layers.append(OriginalEAMailCanvasRowOverlay(
            native_node_serial=row.original_internal_node_serial,
            x=x, y=y, width=w, height=h,
            png=selected_png if selected else png,
            source_path=selected_resource.source_path if selected else expected.source_path,
            native_selected=selected,
        ))
    if selected_node_serial is not None and selected_node_serial not in seen:
        raise OriginalEAMailCanvasError("Selected native row is not in delivered viewport")
    return tuple(layers)
