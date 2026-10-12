"""Source-bounded PSupportStart seven-row geometry from the shipped original PE.

Not a complete window renderer. Source vtable 0x7C6DDC+4 -> 0x4C7B70
lays out seven staff child groups through 0x4C9510; that method calls the
native coordinate owner 0x64F380. The screen's full child rectangles,
button hit regions, glyphs and complete user interaction remain unresolved.
Original PE SHA-256: 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
"""
from __future__ import annotations
from dataclasses import dataclass

SOURCE_SUPPORTSTART_NATIVE_SIZE = (760, 500)
SOURCE_SUPPORTSTART_ROW_COUNT = 7
SOURCE_SUPPORTSTART_FIRST_ROW = (391, 181)
SOURCE_SUPPORTSTART_ROW_VERTICAL_STEP = 40
# Native Generic/user_entry/text_bars.444 has 306x68 source header.
# 0x5F61D0 creates its 306x17 cropped frame; +0x14/+0x18 fields
# are 306/17 (0x64E500); 0x4C9510 adds 20 to each dimension
# before calling native rectangle owner 0x64F380.
SOURCE_SUPPORTSTART_ROW_RECT_SIZE = (326, 37)
SOURCE_SUPPORTSTART_BACKGROUND_SOURCE = 'FM2001_Art/Generic/user_entry/background.444'
SOURCE_SUPPORTSTART_ROW_BARS_SOURCE = 'FM2001_Art/Generic/user_entry/text_bars.444'
SOURCE_SUPPORTSTART_ROW_BUTTON_SOURCE = 'FM2001_Art/Generic/GenericButtonsAndBars/user_entry_anim.444'
SOURCE_SUPPORTSTART_SELECTOR_FIRST_OFFSET = 0x2224
SOURCE_SUPPORTSTART_SELECTOR_STRIDE = 0x4C
SOURCE_SUPPORTSTART_TEXT_FIRST_OFFSET = 0x70
SOURCE_SUPPORTSTART_TEXT_SECOND_OFFSET = 0x4F0
SOURCE_SUPPORTSTART_TEXT_STRIDE = 0x80
SOURCE_SUPPORTSTART_CHILD_GROUP_FIRST_INDEX = 8


@dataclass(frozen=True)
class SourceSupportStartActionChild:
    """Actual original owner/dispatch edge; not a derived mouse hit rectangle."""

    native_event: int
    object_owner_offset: int
    animation_wrapper_address: int
    # Verified visual native local bounds, not mouse hit proof.
    source_layout_rect: tuple[int, int, int, int]
    result_byte_after_native_handler: int
    invokes_full_original_apply: bool


def original_supportstart_action_children() -> tuple[SourceSupportStartActionChild, ...]:
    """Vft+4 source 0x4C7B70 creates action children IDs 1/2.

    Native 0x4D05E0 event1 sets +0x1DE4=0 without apply; event2 calls
    virtual+0x4C 0x4D0830 (staff + names commit), then returns byte 1.
    This exposes exact original visual client rectangles only. Button hit masks,
    parent transforms, hover states and live Apply remain unresolved.
    """
    return (
        SourceSupportStartActionChild(1, 0x1EB8, 0x946190, (729, 1, 30, 30), 0, False),
        SourceSupportStartActionChild(2, 0x1F08, 0x946150, (697, 1, 30, 30), 1, True),
    )


@dataclass(frozen=True)
class SourceSupportStartRowAnchor:
    """Original editor row anchor and per-row owner offsets, not a hit rectangle."""

    index: int
    origin: tuple[int, int]
    # Source x/y/width/height through 0x4C9510 -> 0x64F380;
    # this is an original layout child bounding rect, not yet an input hit map.
    source_layout_rect: tuple[int, int, int, int]
    selector_owner_offset: int
    display_text_first_owner_offset: int
    display_text_second_owner_offset: int
    native_group_index: int


def original_supportstart_row_anchors() -> tuple[SourceSupportStartRowAnchor, ...]:
    """Original 0x4C8014..0x4C8263 repeated 0x4C9510 calls.

    `0x64F380` confirms the two source position values are x and y.
    Width/height come from original text_bars cropped frame 306x17 plus
    original native +20/+20 padding. Still NOT proof of on-screen click hit
    behavior, staff names, hover frame or fully decoded artwork.
    """
    return tuple(
        SourceSupportStartRowAnchor(
            index=i,
            origin=(
                SOURCE_SUPPORTSTART_FIRST_ROW[0],
                SOURCE_SUPPORTSTART_FIRST_ROW[1] + SOURCE_SUPPORTSTART_ROW_VERTICAL_STEP*i,
            ),
            source_layout_rect=(
                SOURCE_SUPPORTSTART_FIRST_ROW[0],
                SOURCE_SUPPORTSTART_FIRST_ROW[1] + SOURCE_SUPPORTSTART_ROW_VERTICAL_STEP*i,
                *SOURCE_SUPPORTSTART_ROW_RECT_SIZE,
            ),
            selector_owner_offset=SOURCE_SUPPORTSTART_SELECTOR_FIRST_OFFSET + SOURCE_SUPPORTSTART_SELECTOR_STRIDE*i,
            display_text_first_owner_offset=SOURCE_SUPPORTSTART_TEXT_FIRST_OFFSET + SOURCE_SUPPORTSTART_TEXT_STRIDE*i,
            display_text_second_owner_offset=SOURCE_SUPPORTSTART_TEXT_SECOND_OFFSET + SOURCE_SUPPORTSTART_TEXT_STRIDE*i,
            native_group_index=SOURCE_SUPPORTSTART_CHILD_GROUP_FIRST_INDEX + i,
        )
        for i in range(SOURCE_SUPPORTSTART_ROW_COUNT)
    )


def original_supportstart_native_modal_origin(
    *, viewport_size: tuple[int, int],
) -> tuple[int, int]:
    """Original 0x450C37..0x450C86 native viewport-relative 760x500 window.

    The actual source reads width from 0x8779C0 and height from
    0x8779C4. No viewport is hardcoded and these layout coordinates
    do NOT establish native pointer-hit geometry.
    """
    if (type(viewport_size) is not tuple or len(viewport_size) != 2
            or any(type(value) is not int or not 0 < value <= 0x7fffffff
                   for value in viewport_size)):
        raise ValueError("Require authentic positive signed-32-bit viewport dimensions")
    width, height = viewport_size
    x = width if width < 20 else width - 760 if width >= 780 else 20
    y = height if height < 50 else height - 500 if height >= 550 else 50
    return (x, y)


def original_supportstart_row_native_screen_rect(
    index: int, *, viewport_size: tuple[int, int],
) -> tuple[int, int, int, int]:
    """Translate authentic modal-local row bounds, NOT interactive hits."""
    if type(index) is not int or not 0 <= index < SOURCE_SUPPORTSTART_ROW_COUNT:
        raise ValueError("Expected genuine native PSupportStart row index 0..6")
    x, y = original_supportstart_native_modal_origin(viewport_size=viewport_size)
    local = original_supportstart_row_anchors()[index].source_layout_rect
    return (x + local[0], y + local[1], local[2], local[3])


def original_supportstart_action_native_screen_rect(
    native_event: int, *, viewport_size: tuple[int, int],
) -> tuple[int, int, int, int]:
    """Original exit/tick source rectangle translated, NOT pointer hit."""
    if type(native_event) is not int:
        raise ValueError("Native SupportStart action must be integer")
    action = next(
        (a for a in original_supportstart_action_children()
         if a.native_event == native_event), None
    )
    if action is None:
        raise ValueError("Only original event1 Exit and event2 Apply")
    x, y = original_supportstart_native_modal_origin(viewport_size=viewport_size)
    a, b, w, h = action.source_layout_rect
    return (x + a, y + b, w, h)


def original_supportstart_native_row_window_event_candidate(
    index: int,
    *,
    source_screen_point: tuple[int, int],
    viewport_size: tuple[int, int],
    native_row_control_dword: int,
) -> bool:
    """Source 0x653480 native window CHILD prefilter, not accepted click.

    Original modal local point = native screen point - modal owner x/y.
    0x6534C7 requires child control bit0 (enabled), followed by
    half-open rectangle: min_x<=x<max_x and min_y<=y<max_y.
    Only then does 0x6534EA dispatch row virtual+0x6C with arg2=1;
    actual 0x5D4790 parent/child callbacks may STILL reject input.

    IMPORTANT: 0x6534AD invokes window vft+0x10 BEFORE any child
    rectangle test. Caller must supply its resulting POST-callback
    control DWORD and genuine source-native event pixel, not pre-dispatch
    state or an arbitrary Tk mouse rectangle. Real root/row object
    identity must likewise come from upstream event routing.
    Source blank staff rows can pass THIS geometric prefilter,
    yet their own 0x64F7A0 bit1 acceptance gate rejects the event.
    """
    if (type(source_screen_point) is not tuple or len(source_screen_point) != 2
            or any(type(v) is not int or not -0x80000000 <= v <= 0x7fffffff
                   for v in source_screen_point)):
        raise ValueError("Native window event requires exact signed x/y point")
    if (type(native_row_control_dword) is not int
            or not 0 <= native_row_control_dword <= 0xffffffff):
        raise ValueError("Native row control state must be DWORD")
    x,y,w,h = original_supportstart_row_native_screen_rect(
        index, viewport_size=viewport_size
    )
    px,py = source_screen_point
    return bool(
        (native_row_control_dword & 0x0001)
        and x <= px < x + w
        and y <= py < y + h
    )
