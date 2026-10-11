"""Source original EAMail eight-row normal bitmap compositing for live host.

Bounded first render: only default original 532x18 row graphic is source-exact.
Original row/text native font/colors/bit-dependent icons/selection/detail and
click actions remain unrecovered; those are intentionally NOT painted here.
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

    def __post_init__(self) -> None:
        if ((self.normal.width, self.normal.height) !=
                ORIGINAL_EAMAIL_ROW_RECT[2:]):
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


def load_verified_original_eamail_row_art(
    source_root: str | Path,
    original_executable: str | Path,
) -> OriginalEAMailRowArt:
    """Decode only the SHA-authenticated first normal EAM row background.

    All other original EAM control and status graphics must exist unchanged;
    loading them as decorative substitutions would be incorrect.
    """
    root = Path(source_root)
    validate_original_eamail_grid_resources(root)
    validate_original_eamail_control_art(root)
    original = ORIGINAL_EAMAIL_GRID_RESOURCES[0]
    if original.name != "normal" or original.source_wrapper_va != 0x945E30:
        raise OriginalEAMailCanvasError("Original normal row graphic mapping drifted")
    executable = Path(original_executable).read_bytes()
    quant = quantization_from_verified_executable(executable)
    tables = tables_from_original_executable(executable)
    bitmap = decode_staged_or_original(
        (root / original.source_path).read_bytes(),
        tables=tables,
        quant=quant,
    )
    return OriginalEAMailRowArt(bitmap)


def source_original_eamail_row_backgrounds(
    visible: OriginalEAMNativeVisibleRowsSource,
    art: OriginalEAMailRowArt,
) -> tuple[OriginalEAMailCanvasRowOverlay, ...]:
    """Produce original normal row bitmaps at exact native screen coordinates.

    Native PMessageRow ctor 0x46E705 initializes normal wrapper 0x945E30.
    Source selection/hover/status changes follow different unimplemented
    callbacks and must NOT be guessed here. Empty inbox yields no rows.
    """
    if type(visible) is not OriginalEAMNativeVisibleRowsSource or type(art) is not OriginalEAMailRowArt:
        raise OriginalEAMailCanvasError("Source original Inbox rows and art required")
    if len(visible.native_rows) > ORIGINAL_EAMAIL_VISIBLE_ROWS:
        raise OriginalEAMailCanvasError("Native CMessageList has eight visible slots")
    expected = ORIGINAL_EAMAIL_GRID_RESOURCES[0]
    seen = set()
    png = encode_rgba_png(art.normal.width, art.normal.height, art.normal.rgba)
    layers = []
    for row in visible.native_rows:
        if (row.original_internal_node_serial in seen or
                row.source_default_background_va != expected.source_wrapper_va):
            raise OriginalEAMailCanvasError("Original normal row owner/bitmap mismatch")
        seen.add(row.original_internal_node_serial)
        x, y, w, h = row.row_screen_rect
        if (w, h) != ORIGINAL_EAMAIL_ROW_RECT[2:]:
            raise OriginalEAMailCanvasError("Original rendered row bounds mismatch")
        layers.append(OriginalEAMailCanvasRowOverlay(
            native_node_serial=row.original_internal_node_serial,
            x=x, y=y, width=w, height=h, png=png,
            source_path=expected.source_path,
        ))
    return tuple(layers)
