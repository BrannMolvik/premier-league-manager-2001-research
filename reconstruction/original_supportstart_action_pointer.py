"""Original PSupportStart Win32 mouse-down -> native Cancel/Apply transaction.

Original footballmanager.exe SHA-256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3

Source 0x653B40/0x653480 dispatches window children by native bounds;
PSupportStart action children +0x1EB8/+0x1F08 use final vtables
0x7C0DA0/0x7C0C58, both vft+0x6C = 0x5D39C0. After source
0x64F7A0 accepts, its modal callback vft+0x10 = 0x4D05E0 handles
event 1/2 on mouse DOWN, BEFORE mouse-up 0x653C40/0x653510.
No native GUI execution or current GameState write is asserted.
"""
from __future__ import annotations

from dataclasses import dataclass

from original_supportstart_editor_projection import (
    OriginalSupportStartCloseProjection,
    OriginalSupportStartEditorProjection,
)
from original_supportstart_layout import (
    original_supportstart_action_children,
    original_supportstart_action_native_screen_rect,
    original_supportstart_native_modal_origin,
    SOURCE_SUPPORTSTART_NATIVE_SIZE,
)
from original_supportstart_modal_result import (
    SourceOriginalSupportStartModalDispatch,
    source_teamselect_supportstart_modal_dispatch,
)
from original_supportstart_pointer_candidate import SourceSupportStartPointerCandidate
from original_window_event_stack import (
    NativeWindow,
    SOURCE_WIN32_WM_LBUTTONDOWN,
    SOURCE_WIN32_WM_LBUTTONDBLCLK,
)


class OriginalSupportStartActionPointerError(ValueError):
    """Original action window/control/input prerequisites not established."""


@dataclass(frozen=True)
class OriginalSupportStartActionPointerReceipt:
    native_event: int
    source_button_owner_offset: int
    source_button_state_after_press: int
    editor_close: OriginalSupportStartCloseProjection
    modal_dispatch: SourceOriginalSupportStartModalDispatch


def project_original_supportstart_action_pointer_down(
    editor: OriginalSupportStartEditorProjection,
    *,
    candidate: SourceSupportStartPointerCandidate,
    source_windows: tuple[NativeWindow, ...],
    modal_window_identity: int,
    viewport_size: tuple[int, int],
    action_control_dwords: tuple[int, int],
    teamselect_owner_event_accepted: bool,
    teamselect_selected_control_bit15: bool,
) -> OriginalSupportStartActionPointerReceipt | None:
    """Resolve original accepted action click in a known captured modal.

    The caller MUST own authentic NativeWindow registration, window capture,
    viewport and POST-parent-dispatch +0x18 action flags, plus the source
    original-user/staff editor. The existing candidate first verifies the
    Win32 original stack route, modal identity, and any staff row prefilter.
    Require capture of this modal alone; unknown multiwindow concurrency
    remains intentionally fail-closed.

    Native 0x4C7CC6/0x4C7CFA registers the Exit/Tick controls with
    IDs 1/2, owner PSupportStart, and native graphics bounds
    (729,1,30,30)/(697,1,30,30). 0x653480 tests child bit0 and
    half-open bounds. Both final action vfts+0x6C -> 0x5D39C0,
    which sets state bit2 (0x4), calls 0x64F7A0, then restores bit2.
    0x64F7A0 requires state bit1 (0x2) and NOT pressed bit4 (0x10).
    The nonzero event ID with owner PSupportStart invokes virtual+0x0C
    0x42DE00 (returns 1); accepted action sets pressed bit4,
    and immediately calls owner virtual+0x10 0x4D05E0 with native
    control+0x20=1/2. That dispatcher closes the modal via WM_USER;
    event1 skips staff/name Apply; event2 invokes 0x4D0830.

    This is a pure source transaction. It does not draw a UI, execute
    original binary, post Win32 messages, run unknown observers,
    advance CRT RNG, or mutate live GameState.
    """
    if type(editor) is not OriginalSupportStartEditorProjection:
        raise OriginalSupportStartActionPointerError("Require source-staged original editor")
    if type(candidate) is not SourceSupportStartPointerCandidate:
        raise OriginalSupportStartActionPointerError("Require original Win32 route candidate")
    if (candidate.original_win32_message not in
            (SOURCE_WIN32_WM_LBUTTONDOWN, SOURCE_WIN32_WM_LBUTTONDBLCLK)
            or not candidate.source_modal_window_reached
            or candidate.original_window_route is None
            or candidate.native_row_event_accepted
            or candidate.source_candidate_row_indices
            or candidate.source_candidate_native_control_ids):
        raise OriginalSupportStartActionPointerError(
            "Only an unclaimed original PSupportStart mouse-down route can close"
        )
    if (type(source_windows) is not tuple
            or any(type(win) is not NativeWindow for win in source_windows)
            or type(modal_window_identity) is not int
            or modal_window_identity < 0):
        raise OriginalSupportStartActionPointerError("Need genuine native window ownership")
    matches = [(i, win) for i, win in enumerate(source_windows)
               if win.source_identity == modal_window_identity]
    if len(matches) != 1:
        raise OriginalSupportStartActionPointerError("Modal identity absent or ambiguous")
    modal_index, modal = matches[0]
    origin = original_supportstart_native_modal_origin(viewport_size=viewport_size)
    if modal.bounds != (
        origin[0], origin[1],
        origin[0] + SOURCE_SUPPORTSTART_NATIVE_SIZE[0],
        origin[1] + SOURCE_SUPPORTSTART_NATIVE_SIZE[1],
    ) or not modal.virtual44_eligible:
        raise OriginalSupportStartActionPointerError("Modal native size/route differs")
    route = candidate.original_window_route
    if (not route.owner_capture_branch
            or route.selected_index != modal_index
            or route.dispatched_indices != (modal_index,)
            or modal_index not in route.checked_vft44_indices):
        raise OriginalSupportStartActionPointerError(
            "Captured original PSupportStart window not exclusively routed"
        )
    if (type(action_control_dwords) is not tuple
            or len(action_control_dwords) != 2
            or any(type(value) is not int or not 0 <= value <= 0xFFFFFFFF
                   for value in action_control_dwords)):
        raise OriginalSupportStartActionPointerError(
            "Require both source-native action control DWORDs"
        )
    if (type(teamselect_owner_event_accepted) is not bool
            or type(teamselect_selected_control_bit15) is not bool
            or not teamselect_owner_event_accepted
            or not teamselect_selected_control_bit15):
        raise OriginalSupportStartActionPointerError("Original modal entry not established")
    point = candidate.original_native_client_point
    if (type(point) is not tuple or len(point) != 2
            or any(type(coordinate) is not int for coordinate in point)
            or not modal.contains(point)):
        raise OriginalSupportStartActionPointerError("Native point outside registered modal")

    for i, action in enumerate(original_supportstart_action_children()):
        x, y, width, height = original_supportstart_action_native_screen_rect(
            action.native_event, viewport_size=viewport_size,
        )
        if not (x <= point[0] < x + width and y <= point[1] < y + height):
            continue
        flags = action_control_dwords[i]
        # Original 0x6534C7 enabled bit0, then 0x64F7A5 state bit1
        # and 0x64F7B8 pressed bit4. No synthetic disabled click.
        if not (flags & 1 and flags & 2 and not flags & 0x10):
            return None
        close = editor.close(action.native_event)
        dispatch = source_teamselect_supportstart_modal_dispatch(
            owner_event_accepted=True,
            selected_control_bit15=True,
            native_action_event=action.native_event,
        )
        if (close.source_modal_result != dispatch.native_modal_result_byte
                or close.invoked_original_apply != dispatch.native_apply_called):
            raise OriginalSupportStartActionPointerError(
                "Original source modal callback and editor state disagree"
            )
        return OriginalSupportStartActionPointerReceipt(
            native_event=action.native_event,
            source_button_owner_offset=action.object_owner_offset,
            source_button_state_after_press=flags | 0x14,
            editor_close=close,
            modal_dispatch=dispatch,
        )
    return None
