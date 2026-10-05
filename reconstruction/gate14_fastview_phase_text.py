"""Source-closed ScoreComposite runtime phase-label contract.

The canonical FM2001 localization initializer performs exactly 2,714
sequential uint16 reads, matching English.idx entry-for-entry. Each index is
resolved through 0x64E320 into a descending table of string pointers beginning
at global 0x9847F8. This closes the four ScoreComposite phase-label globals
without guessing from nearby key names or decoded art.

This module records text identity and generic text-control render parameters
only. It deliberately does not flatten runtime icon/text pixels because
0x51BA30 appends one PictureControl and then one TextControl per callback, so
multiple ScoreComposite callbacks may interleave their icon/text pairs at the
current parent tail.
"""
from __future__ import annotations

from dataclasses import dataclass

from gate14_fastview_scores import (
    SCORE_COMPOSITE_PHASE_DISPLAY_HELPER_VA,
    SCORE_COMPOSITE_PHASE_TEXT_LOCAL_RECT,
    SCORE_COMPOSITE_PHASE_TEXT_RAW_FLAGS,
    SCORE_COMPOSITE_PHASE_TEXT_STYLE_INDEX,
    SCORE_COMPOSITE_PHASE_RESOURCE_BY_EVENT,
)


class FastViewScorePhaseTextError(ValueError):
    pass


CANONICAL_ENGLISH_IDX_SIZE = 5_428
CANONICAL_ENGLISH_IDX_SHA256 = (
    "98fcbe9e9eb5d1068739a58cc46aaaedab2749b2c65460861b18beeac7361db1"
)
CANONICAL_ENGLISH_STR_SIZE = 369_644
CANONICAL_ENGLISH_STR_SHA256 = (
    "aa594a55ad95c672b69184e5f3ff8349e41fe95b48c5dcb3c8fcfe2bcdf5b601"
)
CANONICAL_ENGLISH_IDX_ENTRY_COUNT = 2_714

LANGUAGE_INDEX_READ_VA = 0x667E90
LANGUAGE_POINTER_RESOLVE_VA = 0x64E320
LANGUAGE_INITIALIZER_FIRST_READ_CALLSITE_VA = 0x635F56
LANGUAGE_INITIALIZER_LAST_READ_CALLSITE_VA = 0x64C7AC
LANGUAGE_GLOBAL_FIRST_VA = 0x9847F8
LANGUAGE_GLOBAL_LAST_VA = 0x981D94
LANGUAGE_GLOBAL_STRIDE = -4

GENERIC_TEXT_CONSTRUCTOR_VA = 0x527960
GENERIC_TEXT_DRAW_VA = 0x64F090
GENERIC_TEXT_STYLE_SELECTOR_VA = 0x527BA0
PHASE_TEXT_STYLE_WRAPPER_VA = 0x87BE90
PHASE_TEXT_FONT_OBJECT_VA = 0x9197E0
PHASE_TEXT_NATIVE_COLOR_16 = 0xFFFF
GENERIC_TEXT_FORCED_RENDER_FLAG = 0x08
PHASE_TEXT_RENDER_FLAGS = (
    SCORE_COMPOSITE_PHASE_TEXT_RAW_FLAGS | GENERIC_TEXT_FORCED_RENDER_FLAG
)
PHASE_TEXT_HORIZONTAL_CENTER_BIT = 0x04
PHASE_TEXT_VERTICAL_CENTER_BIT = 0x20

PHASE_ICON_CONSTRUCTOR_CALLSITE_VA = 0x51BB05
PHASE_TEXT_CONSTRUCTOR_CALLSITE_VA = 0x51BB9A


@dataclass(frozen=True)
class FastViewScorePhaseText:
    event_name: str
    label_global_va: int
    english_idx_entry: int
    english_string_id: int
    text: str
    local_rect: tuple[int, int, int, int] = SCORE_COMPOSITE_PHASE_TEXT_LOCAL_RECT
    style_index: int = SCORE_COMPOSITE_PHASE_TEXT_STYLE_INDEX
    native_color_16: int = PHASE_TEXT_NATIVE_COLOR_16
    render_flags: int = PHASE_TEXT_RENDER_FLAGS
    horizontal_alignment: str = "center"
    vertical_alignment: str = "center"

    def __post_init__(self) -> None:
        if self.event_name not in SCORE_COMPOSITE_PHASE_RESOURCE_BY_EVENT:
            raise FastViewScorePhaseTextError("unknown ScoreComposite phase event")
        expected_entry = language_entry_for_global(self.label_global_va)
        if self.english_idx_entry != expected_entry:
            raise FastViewScorePhaseTextError(
                "phase label global/index mapping drifted"
            )
        if type(self.english_string_id) is not int or self.english_string_id < 0:
            raise FastViewScorePhaseTextError("English STR id must be non-negative")
        if not isinstance(self.text, str) or not self.text:
            raise FastViewScorePhaseTextError("phase label text must be non-empty")
        if self.local_rect != SCORE_COMPOSITE_PHASE_TEXT_LOCAL_RECT:
            raise FastViewScorePhaseTextError("phase label rect drifted")
        if self.style_index != 1:
            raise FastViewScorePhaseTextError("phase label style must remain index 1")
        if self.native_color_16 != 0xFFFF:
            raise FastViewScorePhaseTextError("phase label native color drifted")
        if self.render_flags != 0x2C:
            raise FastViewScorePhaseTextError("phase label render flags drifted")
        if (
            self.horizontal_alignment != "center"
            or self.vertical_alignment != "center"
        ):
            raise FastViewScorePhaseTextError(
                "phase label alignment must remain source-centered"
            )


def language_entry_for_global(global_va: int) -> int:
    """Map one initializer destination global to its exact English.idx entry."""
    if type(global_va) is not int:
        raise FastViewScorePhaseTextError("localization global must be integer")
    delta = LANGUAGE_GLOBAL_FIRST_VA - global_va
    if delta < 0 or delta % 4:
        raise FastViewScorePhaseTextError(
            "localization global is outside the exact descending table"
        )
    entry = delta // 4
    if not 0 <= entry < CANONICAL_ENGLISH_IDX_ENTRY_COUNT:
        raise FastViewScorePhaseTextError(
            "localization global is outside the 2,714-entry initializer"
        )
    expected_global = LANGUAGE_GLOBAL_FIRST_VA + entry * LANGUAGE_GLOBAL_STRIDE
    if expected_global != global_va:
        raise FastViewScorePhaseTextError("localization global stride mismatch")
    return entry


PHASE_TEXT_BY_EVENT = {
    "EventHalfTime": FastViewScorePhaseText(
        event_name="EventHalfTime",
        label_global_va=0x982380,
        english_idx_entry=2334,
        english_string_id=21533,
        text="HT",
    ),
    "EventFullTime": FastViewScorePhaseText(
        event_name="EventFullTime",
        label_global_va=0x98237C,
        english_idx_entry=2335,
        english_string_id=21534,
        text="FT",
    ),
    "EventExtraTime": FastViewScorePhaseText(
        event_name="EventExtraTime",
        label_global_va=0x982378,
        english_idx_entry=2336,
        english_string_id=21535,
        text="ET",
    ),
    "EventPenalties": FastViewScorePhaseText(
        event_name="EventPenalties",
        label_global_va=0x982374,
        english_idx_entry=2337,
        english_string_id=21536,
        text="PEN",
    ),
}


def score_phase_text(event_name: str) -> FastViewScorePhaseText:
    if type(event_name) is not str:
        raise FastViewScorePhaseTextError("phase event name must be a string")
    try:
        return PHASE_TEXT_BY_EVENT[event_name]
    except KeyError as exc:
        raise FastViewScorePhaseTextError(
            "no source-closed ScoreComposite phase label for this event"
        ) from exc


def score_phase_text_contract() -> dict:
    return {
        "language_index_read_va": LANGUAGE_INDEX_READ_VA,
        "language_pointer_resolve_va": LANGUAGE_POINTER_RESOLVE_VA,
        "initializer_first_read_callsite_va": (
            LANGUAGE_INITIALIZER_FIRST_READ_CALLSITE_VA
        ),
        "initializer_last_read_callsite_va": (
            LANGUAGE_INITIALIZER_LAST_READ_CALLSITE_VA
        ),
        "initializer_entry_count": CANONICAL_ENGLISH_IDX_ENTRY_COUNT,
        "global_first_va": LANGUAGE_GLOBAL_FIRST_VA,
        "global_last_va": LANGUAGE_GLOBAL_LAST_VA,
        "global_stride": LANGUAGE_GLOBAL_STRIDE,
        "phase_display_helper_va": SCORE_COMPOSITE_PHASE_DISPLAY_HELPER_VA,
        "generic_text_constructor_va": GENERIC_TEXT_CONSTRUCTOR_VA,
        "generic_text_draw_va": GENERIC_TEXT_DRAW_VA,
        "style_selector_va": GENERIC_TEXT_STYLE_SELECTOR_VA,
        "style_wrapper_va": PHASE_TEXT_STYLE_WRAPPER_VA,
        "font_object_va": PHASE_TEXT_FONT_OBJECT_VA,
        "raw_flags": SCORE_COMPOSITE_PHASE_TEXT_RAW_FLAGS,
        "render_flags": PHASE_TEXT_RENDER_FLAGS,
        "native_color_16": PHASE_TEXT_NATIVE_COLOR_16,
        "horizontal_alignment": "center",
        "vertical_alignment": "center",
        "icon_constructor_callsite_va": PHASE_ICON_CONSTRUCTOR_CALLSITE_VA,
        "text_constructor_callsite_va": PHASE_TEXT_CONSTRUCTOR_CALLSITE_VA,
        "per_callback_icon_before_text": True,
        "global_all_icons_before_all_text": False,
        "paired_phase_text_identity_recovered": True,
        "paired_phase_text_rasterized": False,
        "runtime_icon_text_interleaving_flattened": False,
        "global_fastview_z_order_recovered": False,
        "complete_fastview_frame_recovered": False,
    }
