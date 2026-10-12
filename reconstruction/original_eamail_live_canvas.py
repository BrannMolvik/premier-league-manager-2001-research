"""Source original EAMail eight-row normal/selected bitmap compositing for live host.

Selection is original 0x471B80 -> 0x470B40, normal 0x470B90. Qualified
list text/icons and single-step arrows are separate from blocked body/actions.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_decoder import EA444DecodedImage
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from gate13_ea444_staged_rasters import decode_staged_or_original
from gate13_original_pixel_preview import encode_rgba_png
from original_eamail_control_art import (
    ORIGINAL_EAMAIL_ART_FOLDER, ORIGINAL_EAMAIL_CONTROL_ART,
    validate_original_eamail_control_art,
)
from original_eamail_source_contract import (
    ORIGINAL_EAMAIL_GRID_RESOURCES,
    ORIGINAL_EAMAIL_ROW_RECT,
    ORIGINAL_EAMAIL_VISIBLE_ROWS,
    validate_original_eamail_grid_resources,
)
from original_eamail_native_row_fields import OriginalEAMNativeVisibleRowsSource
from original_management_text import (
    OriginalManagementTextResources, load_verified_management_text_resources,
)
from original_pmatchinfo_scroll_readiness import PMATCHINFO_SCROLL_RESOURCE_LEADS


class OriginalEAMailCanvasError(ValueError):
    """Cannot render source original EAMail row art safely."""


@dataclass(frozen=True)
class OriginalEAMailRowArt:
    normal: EA444DecodedImage
    selected: EA444DecodedImage | None = None
    empty_preview: EA444DecodedImage | None = None
    text_resources: OriginalManagementTextResources | None = None
    unread_icon: EA444DecodedImage | None = None
    scroll_arrows: EA444DecodedImage | None = None
    received_header: EA444DecodedImage | None = None

    def __post_init__(self) -> None:
        for image in (self.normal, self.selected):
            if image is not None and (image.width, image.height) != ORIGINAL_EAMAIL_ROW_RECT[2:]:
                raise OriginalEAMailCanvasError("Original native row grid geometry drifted")
        if (self.empty_preview is not None
                and (self.empty_preview.width, self.empty_preview.height) != (532, 187)):
            raise OriginalEAMailCanvasError("Original native empty preview geometry drifted")
        for image, size in ((self.unread_icon, (18, 12)), (self.scroll_arrows, (72, 50))):
            if image is not None and (image.width, image.height) != size:
                raise OriginalEAMailCanvasError("Original Inbox control geometry drifted")


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



# Native PEAMail vft 0x7C2950 +0x8 = 0x4720D0. Opening its panel resets
# source selection and preview string to 0x874BA0 then calls 0x471620,
# which selects resource 0x945B30 when the initial string is empty.
# 0x945B30 maps to the shipped preview_panel_disabled.444 (532x187).
ORIGINAL_EAMAIL_EMPTY_PREVIEW_SOURCE_PATH = (
    ORIGINAL_EAMAIL_ART_FOLDER + "/preview_panel_disabled.444"
)
ORIGINAL_EAMAIL_EMPTY_PREVIEW_NATIVE_WRAPPER_VA = 0x945B30
ORIGINAL_EAMAIL_EMPTY_PREVIEW_SCREEN_RECT = (246, 343, 532, 187)


@dataclass(frozen=True)
class OriginalEAMailEmptyPreviewOverlay:
    screen_rect: tuple[int, int, int, int]
    source_path: str
    png: bytes
    native_body_text_rendered: bool = False


def original_empty_eamail_preview(
    visible: OriginalEAMNativeVisibleRowsSource,
    art: OriginalEAMailRowArt,
    *, selected_node_serial: int | None = None,
) -> OriginalEAMailEmptyPreviewOverlay | None:
    """Original native initial empty preview only; never fake selected body.

    Once a row is selected the original displays a dynamically formatted
    message and enabled preview art. That path is NOT implemented here.
    """
    if type(visible) is not OriginalEAMNativeVisibleRowsSource or type(art) is not OriginalEAMailRowArt:
        raise OriginalEAMailCanvasError("Verified original Inbox source required")
    if selected_node_serial is not None:
        return None
    if art.empty_preview is None:
        return None
    return OriginalEAMailEmptyPreviewOverlay(
        screen_rect=ORIGINAL_EAMAIL_EMPTY_PREVIEW_SCREEN_RECT,
        source_path=ORIGINAL_EAMAIL_EMPTY_PREVIEW_SOURCE_PATH,
        png=encode_rgba_png(
            art.empty_preview.width, art.empty_preview.height,
            art.empty_preview.rgba,
        ),
    )


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

    empty_spec = next(
        (x for x in ORIGINAL_EAMAIL_CONTROL_ART
         if x.name == "preview_panel_disabled.444"), None,
    )
    if (empty_spec is None or empty_spec.dimensions != (532, 187)
            or ORIGINAL_EAMAIL_EMPTY_PREVIEW_NATIVE_WRAPPER_VA != 0x945B30):
        raise OriginalEAMailCanvasError("Missing original native disabled preview map")
    empty_raw = (root / ORIGINAL_EAMAIL_EMPTY_PREVIEW_SOURCE_PATH).read_bytes()
    empty_art = decode_staged_or_original(empty_raw, tables=tables, quant=quant)
    unread = decode_staged_or_original(
        (root / ORIGINAL_EAMAIL_ART_FOLDER / 'unread_mail_icon.444').read_bytes(),
        tables=tables, quant=quant,
    )
    arrows = PMATCHINFO_SCROLL_RESOURCE_LEADS[0]
    raw = (root / arrows.source_path).read_bytes()
    if len(raw) != arrows.staged_size_bytes or sha256(raw).hexdigest() != arrows.staged_sha256:
        raise OriginalEAMailCanvasError("Original Inbox scroll atlas identity mismatch")
    return OriginalEAMailRowArt(
        decoded(normal), decoded(selected), empty_art,
        load_verified_management_text_resources(root), unread,
        decode_staged_or_original(raw, tables=tables, quant=quant),
        decode_staged_or_original(
            (root / ORIGINAL_EAMAIL_ART_FOLDER / 'recieved_tog.444').read_bytes(),
            tables=tables, quant=quant,
        ),
    )


def original_eamail_received_hit(x, y):
    # 46F389: panel-local (705,1), parent translation (0,148); 5F5A00:73x20.
    return 705 <= x < 778 and 149 <= y < 169


def original_eamail_received_layers(art, *, selected=False, hovered=False):
    from original_management_text import _clip_mask, _line_origin, _white_rgba
    atlas = art.received_header
    if atlas is None or art.text_resources is None:
        return ()
    if (atlas.width, atlas.height) != (73, 60):
        raise OriginalEAMailCanvasError('Original Received header geometry drifted')
    # Actual vft7C2B04+98=474F80: selected40, hover20, idle0. No pressed frame.
    sy = 40 if selected else 20 if hovered else 0
    rgba = atlas.rgba[sy * 73 * 4:(sy + 20) * 73 * 4]
    layers = [(705, 149, 73, 20, encode_rgba_png(73, 20, rgba))]
    font = art.text_resources.league_tables_row_font
    rect = (705, 149, 73, 20)
    label = _clip_mask(font.render_text_alpha('Received'),
                       _line_origin(font, 'Received', rect, 0x24), rect)
    if label is not None:
        x, y, width, height, alpha = label
        pixels = _white_rgba(alpha)
        if selected:
            pixels = b''.join(bytes((0, 0, 0, pixels[i + 3])) for i in range(0, len(pixels), 4))
        layers.append((x, y, width, height, encode_rgba_png(width, height, pixels)))
    return tuple(layers)


def original_eamail_initial_status_layers(visible, art):
    """471780: initial transfer flags6 choose unread wrapper945BF0 at (15,3)."""
    from original_eamail_native_filter import ORIGINAL_TRANSFER_EAM_NATIVE_INITIAL_FLAGS
    if (type(visible) is not OriginalEAMNativeVisibleRowsSource
            or type(art) is not OriginalEAMailRowArt or art.unread_icon is None):
        raise OriginalEAMailCanvasError("Original Inbox initial-status source required")
    if ORIGINAL_TRANSFER_EAM_NATIVE_INITIAL_FLAGS != 6:
        raise OriginalEAMailCanvasError("Native initial record flags drifted")
    png = encode_rgba_png(18, 12, art.unread_icon.rgba)
    layers = []
    for row in visible.native_rows:
        if row.native_record_class != 'EAMPlayerAskTransferListsub':
            raise OriginalEAMailCanvasError("Mutable/other Inbox status is not qualified")
        x, y, _, _ = row.row_screen_rect
        layers.append((x + 15, y + 3, 18, 12, png))
    return tuple(layers)


def original_eamail_scroll_at_point(x, y):
    """Original enabled press slots ID19/21; panel origin (0,148)."""
    for control_id, top in ((19, 178), (21, 311)):
        if 212 <= x < 230 and top <= y < top + 25:
            return control_id
    return None


def original_eamail_scroll_step(visible, control_id):
    """64FF30 coordinator step1; 64FF90 bound disabling."""
    if (type(visible) is not OriginalEAMNativeVisibleRowsSource
            or type(control_id) is not int or control_id not in (19, 21)):
        raise OriginalEAMailCanvasError("Original Inbox scroll owner/control required")
    current, maximum = visible.original_scroll_offset, visible.original_max_scroll_offset
    if maximum != max(0, visible.original_filtered_count - 8) or not 0 <= current <= maximum:
        raise OriginalEAMailCanvasError("Original Inbox scroll range drifted")
    return max(0, min(maximum, current + (-1 if control_id == 19 else 1)))


def original_eamail_scroll_layers(visible, art, *, pressed_control_id=None):
    """5F2BC0/5F2C00: original idle0, pressed1, disabled3 arrow crops."""
    if type(art) is not OriginalEAMailRowArt or art.scroll_arrows is None:
        raise OriginalEAMailCanvasError("Original Inbox arrow atlas required")
    if pressed_control_id not in (None, 19, 21):
        raise OriginalEAMailCanvasError("Invalid original Inbox pressed arrow")
    atlas = art.scroll_arrows
    layers = []
    for control_id, top, sy in ((19, 178, 0), (21, 311, 25)):
        enabled = original_eamail_scroll_step(visible, control_id) != visible.original_scroll_offset
        frame = (1 if pressed_control_id == control_id else 0) if enabled else 3
        sx = frame * 18
        rgba = b''.join(atlas.rgba[(y * 72 + sx) * 4:(y * 72 + sx + 18) * 4]
                        for y in range(sy, sy + 25))
        layers.append((212, top, 18, 25, encode_rgba_png(18, 25, rgba)))
    return tuple(layers)


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
