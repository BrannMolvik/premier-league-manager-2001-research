"""Original PResults bottom three source bitmaps, immutable EA444 rendering.

This is a *partial* PResults screen: 4A6E50 children 0, 3, 4 only.
The native event-progress bar accepts 6168C0/4A71F0 typed receipts, never
timers, match result cardinality or invented click-to-return handlers.
All assets are the authorized original .444 resources under original_assets.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_decoder import EA444DecodedImage
from ea444_header import parse_ea444_header
from ea444_tables import tables_from_original_executable
from ea444_quantization import quantization_from_verified_executable
from gate13_ea444_staged_rasters import decode_staged_or_original
from original_presults_child_inventory import (
    ORIGINAL_WAITING_BACK_2_SOURCE, ORIGINAL_WAITING_BACK_2_SIZE,
    ORIGINAL_WAITING_BACK_2_SHA256, ORIGINAL_WAITING_BACK_2_RECT,
    ORIGINAL_LOADING_BACK_SOURCE, ORIGINAL_LOADING_BACK_SIZE,
    ORIGINAL_LOADING_BACK_SHA256, ORIGINAL_LOADING_BACK_RECT,
    ORIGINAL_LOADING_FILL_SOURCE, ORIGINAL_LOADING_FILL_SIZE,
    ORIGINAL_LOADING_FILL_SHA256, ORIGINAL_LOADING_FILL_INITIAL_RECT,
    OriginalPResultsSourceError,
    source_original_presults_initial_children,
    source_original_presults_bar_rects_from_dated_callbacks,
)


@dataclass(frozen=True)
class OriginalPResultsBottomArt:
    original_waiting: EA444DecodedImage
    original_progress_back: EA444DecodedImage
    original_progress_fill: EA444DecodedImage

    def __post_init__(self):
        expected = ((self.original_waiting, (800, 87)),
                    (self.original_progress_back, (800, 14)),
                    (self.original_progress_fill, (800, 10)))
        if any(type(item) is not EA444DecodedImage or
               (item.width, item.height) != dims for item, dims in expected):
            raise OriginalPResultsSourceError("three exact original PResults decoded images required")


@dataclass(frozen=True)
class OriginalPResultsRgbaLayer:
    source_role: str
    native_rect: tuple[int, int, int, int]
    rgba: bytes

    def __post_init__(self):
        x, y, w, h = self.native_rect
        if (type(x) is not int or type(y) is not int or
            type(w) is not int or type(h) is not int or
            x < 0 or y < 0 or w <= 0 or h <= 0 or
            x + w > 800 or y + h > 600 or
            type(self.rgba) is not bytes or len(self.rgba) != 4 * w * h):
            raise OriginalPResultsSourceError("source PResults layer rectangle/rgba invalid")


@dataclass(frozen=True)
class OriginalPResultsBottomSurface:
    """Partial source graphics only, no claim of complete native panel."""
    source_layers: tuple[OriginalPResultsRgbaLayer, ...]
    original_native_progress_eligible: bool = False
    full_original_presults_screen: bool = False
    original_return_control_proven: bool = False
    normal_gameplay_result_committed: bool = False


def load_verified_original_presults_bottom_art(source_root, original_executable):
    """Hash-validate real .444 sources before using the existing PE decoder."""
    source_root = Path(source_root)
    requirements = (
        (ORIGINAL_WAITING_BACK_2_SOURCE, ORIGINAL_WAITING_BACK_2_SIZE,
         ORIGINAL_WAITING_BACK_2_SHA256, (800, 87)),
        (ORIGINAL_LOADING_BACK_SOURCE, ORIGINAL_LOADING_BACK_SIZE,
         ORIGINAL_LOADING_BACK_SHA256, (800, 14)),
        (ORIGINAL_LOADING_FILL_SOURCE, ORIGINAL_LOADING_FILL_SIZE,
         ORIGINAL_LOADING_FILL_SHA256, (800, 10)),
    )
    raw = []
    for path, size, digest, dims in requirements:
        item = (source_root / path).read_bytes()
        if len(item) != size or sha256(item).hexdigest() != digest:
            raise OriginalPResultsSourceError("original PResults .444 source identity mismatch: " + path)
        header = parse_ea444_header(item)
        if (header.width, header.height) != dims:
            raise OriginalPResultsSourceError("original PResults .444 header size mismatch: " + path)
        raw.append(item)
    source_original_presults_initial_children(
        waiting_back_2_raw=raw[0],
        loading_back_raw=raw[1],
        loading_fill_raw=raw[2],
    )
    original = Path(original_executable).read_bytes()
    tables = tables_from_original_executable(original)
    quant = quantization_from_verified_executable(original)
    images = tuple(decode_staged_or_original(item, tables=tables, quant=quant)
                   for item in raw)
    return OriginalPResultsBottomArt(*images)


def _clip_left_native(image: EA444DecodedImage, width: int) -> bytes:
    if type(width) is not int or not 0 < width <= image.width:
        raise OriginalPResultsSourceError("original clipped bar requires a positive supported width")
    if width == image.width:
        return image.rgba
    stride = image.width * 4
    portion = width * 4
    return b"".join(image.rgba[row * stride:row * stride + portion]
                    for row in range(image.height))


def source_original_presults_bottom_surface(
    art: OriginalPResultsBottomArt,
    *,
    original_dated_event_receipt=None,
    original_source_event_total: int | None = None,
    original_processed_before_callbacks: int | None = None,
    original_two_collection_4a8260=None,
) -> OriginalPResultsBottomSurface:
    """Build only source sprites; source-qualified dated events may add fill.

    No receipt = static empty original fill at zero width. A receipt without
    independently reached original 4A7210 count/starting counter is rejected.
    """
    if type(art) is not OriginalPResultsBottomArt:
        raise OriginalPResultsSourceError("validated original PResults source art required")
    waiting = OriginalPResultsRgbaLayer(
        "waiting_back_2", ORIGINAL_WAITING_BACK_2_RECT, art.original_waiting.rgba)
    background = OriginalPResultsRgbaLayer(
        "loading_back", ORIGINAL_LOADING_BACK_RECT, art.original_progress_back.rgba)
    layers = [waiting, background]
    if original_two_collection_4a8260 is not None:
        # The FIRST source registry is the only 4A7210 denominator owner,
        # but BOTH ordered 6168C0 callback lists increment PResults+64.
        # Never fabricate a merged receipt/AL or clamp an oversized bitmap.
        if original_dated_event_receipt is not None:
            raise OriginalPResultsSourceError(
                "PResults cannot mix single-collection and dual-collection event owners")
        if original_source_event_total is None or original_processed_before_callbacks is None:
            raise OriginalPResultsSourceError(
                "dual original registry callbacks require independent source 4A7210 counters")
        from original_presults_two_collection_dispatch import (
            source_original_4a8260_native_progress_counter_receipts,
        )
        counters=source_original_4a8260_native_progress_counter_receipts(
            original_two_collection_receipt=original_two_collection_4a8260,
            original_before_processed_64=original_processed_before_callbacks,
            original_first_collection_4a7210_total_68=original_source_event_total,
        )
        if counters and counters[-1].native_width > art.original_progress_fill.width:
            raise OriginalPResultsSourceError(
                "native two-registry event ticks exceed the source 800px fill; "
                "original clipping/overdraw behavior not verified")
        steps=()
        last_width=0 if not counters else counters[-1].native_width
        has_source_events=bool(counters)
    else:
        if original_dated_event_receipt is None:
            if original_source_event_total is not None or original_processed_before_callbacks is not None:
                raise OriginalPResultsSourceError("cannot synthesize progress without actual dated callbacks")
            return OriginalPResultsBottomSurface(tuple(layers))
        if original_source_event_total is None or original_processed_before_callbacks is None:
            raise OriginalPResultsSourceError("dated callbacks require authentic 4A7210 counters")
        steps = source_original_presults_bar_rects_from_dated_callbacks(
            original_6168c0_receipt=original_dated_event_receipt,
            original_source_total_4a7210=original_source_event_total,
            original_processed_before_callbacks=original_processed_before_callbacks,
        )
        has_source_events=bool(steps)
        last_width=0 if not steps else steps[-1].original_bar_rect_xywh[2]
    if has_source_events:
        x, y, width, height = (0, 581, last_width, 10)
        if width:
            expected = ORIGINAL_LOADING_FILL_INITIAL_RECT
            if (x, y, height) != (expected[0], expected[1], expected[3]):
                raise OriginalPResultsSourceError("original progress fill owner/rect changed")
            layers.append(OriginalPResultsRgbaLayer(
                "loading_fill", (x, y, width, height),
                _clip_left_native(art.original_progress_fill, width),
            ))
    return OriginalPResultsBottomSurface(tuple(layers), has_source_events)
