"""Original EAMail ten filter controls: native geometry/ownership only.

Owner reference: private SHA-256 833bf95e...b7cc3 original executable,
0x47B202/0x474C71 -> ten 0x4C controls at PEAMail+0x64C.
0x46EA57..0x46F05F -> 0x5D4F00 supplies (x22,y30+30*i,w183,h28),
child radio+0x44 wrapper0x941430 and label+0x48.
This module does NOT accept a click or select a filter. Native 0x5D4AC0
also tests +0x38, bit1, and optional callbacks and has not been mapped
to exact active window and radio state in normal GUI. Original bitmap
loader 0x5FFF60 refers to boost_type_11.444, whose availability from the
user's extracted game filesystem is presently UNRESOLVED.
"""
from __future__ import annotations

from dataclasses import dataclass

NATIVE_FILTER_COUNT = 10
NATIVE_FILTER_FIRST_OWNER_OFFSET = 0x64C
NATIVE_FILTER_OWNER_STRIDE = 0x4C
NATIVE_FILTER_LOCAL_X = 22
NATIVE_FILTER_LOCAL_FIRST_Y = 30
NATIVE_FILTER_VERTICAL_STRIDE = 30
NATIVE_FILTER_CONTROL_SIZE = (183, 28)
NATIVE_FILTER_LABEL_FIRST_IDX_ORDINAL = 177
NATIVE_FILTER_RADIO_CHILD_OFFSET = 0x44
NATIVE_FILTER_TEXT_CHILD_OFFSET = 0x48
NATIVE_FILTER_RADIO_WRAPPER = 0x941430


@dataclass(frozen=True)
class NativeEAMailFilterControl:
    index: int
    native_owner_offset: int
    original_english_idx_ordinal: int
    panel_local_rect: tuple[int, int, int, int]
    native_radio_child_offset: int = NATIVE_FILTER_RADIO_CHILD_OFFSET
    native_text_child_offset: int = NATIVE_FILTER_TEXT_CHILD_OFFSET
    native_radio_wrapper: int = NATIVE_FILTER_RADIO_WRAPPER


def original_eamail_filter_controls() -> tuple[NativeEAMailFilterControl, ...]:
    """Original source 10×0x4C owners and exactly spaced native rectangles.

    These are actual native geometric setup args, not source-confirmed
    pointer hits or evidence that a click changes the filtered mailbox.
    """
    return tuple(
        NativeEAMailFilterControl(
            index=i,
            native_owner_offset=NATIVE_FILTER_FIRST_OWNER_OFFSET
                + i * NATIVE_FILTER_OWNER_STRIDE,
            original_english_idx_ordinal=NATIVE_FILTER_LABEL_FIRST_IDX_ORDINAL + i,
            panel_local_rect=(
                NATIVE_FILTER_LOCAL_X,
                NATIVE_FILTER_LOCAL_FIRST_Y + NATIVE_FILTER_VERTICAL_STRIDE * i,
                *NATIVE_FILTER_CONTROL_SIZE,
            ),
        )
        for i in range(NATIVE_FILTER_COUNT)
    )


def original_eamail_filter_native_window_candidate(
    index: int,
    *,
    source_panel_origin: tuple[int, int],
    source_screen_point: tuple[int, int],
    native_filter_control_dword: int,
) -> bool:
    """Only original enabled/half-open window-child prefilter (0x653480).

    Native parent event0, vft+0x6C 0x5D4AC0 and its +0x38 callback path
    can further reject, consume, or modify the original radio state.
    This NEVER implies native selection, a completed filter action, or
    any modern GameState/mailbox mutation.
    """
    if type(index) is not int or not 0 <= index < NATIVE_FILTER_COUNT:
        raise ValueError("Original EAMail filter index must be 0..9")
    if (type(source_panel_origin) is not tuple
            or len(source_panel_origin) != 2
            or any(type(v) is not int or not -0x80000000 <= v <= 0x7FFFFFFF
                   for v in source_panel_origin)):
        raise ValueError("Source panel origin must be a signed native point")
    if (type(source_screen_point) is not tuple
            or len(source_screen_point) != 2
            or any(type(v) is not int or not -0x80000000 <= v <= 0x7FFFFFFF
                   for v in source_screen_point)):
        raise ValueError("Source mouse point must be a signed native point")
    if (type(native_filter_control_dword) is not int
            or not 0 <= native_filter_control_dword <= 0xFFFFFFFF):
        raise ValueError("Native control state must be DWORD")
    if not (native_filter_control_dword & 0x1):
        return False
    rect = original_eamail_filter_controls()[index].panel_local_rect
    x = source_screen_point[0] - source_panel_origin[0]
    y = source_screen_point[1] - source_panel_origin[1]
    return (rect[0] <= x < rect[0] + rect[2]
            and rect[1] <= y < rect[1] + rect[3])
