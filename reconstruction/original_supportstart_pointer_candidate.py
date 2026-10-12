"""Bounded native Win32 pointer -> PSupportStart row dispatch candidate.

Original SHA-verified footballmanager.exe disassembly proves:
0x531F70 WM201/203 unsigned LPARAM -> 0x532680 -> 0x653B40
captured/uncaptured window stack -> 0x653480 window child bit0,
half-open native row rectangles -> row vft+0x6C 0x5D6270.
PSupportStart row IDs8..14 are distinct from Cancel1/Apply2.

This module returns only a candidate for original native dispatch.
It does NOT assert native 0x64F7A0 accepted the mouse, infer other
modal child overlay behavior, mutate staff, simulate shared CRT, or
perform a Tk event. Only the actual native controller can qualify
the callback/press/hover side effects.
"""
from __future__ import annotations

from dataclasses import dataclass

from original_supportstart_editor_projection import OriginalSupportStartEditorProjection
from original_supportstart_input import original_supportstart_row_callback_contract
from original_supportstart_layout import (
    SOURCE_SUPPORTSTART_NATIVE_SIZE,
    original_supportstart_native_modal_origin,
    original_supportstart_native_row_window_event_candidate,
)
from original_window_event_stack import (
    NativeWindow,
    NativeWindowRoute,
    project_original_mywindow_left_button_event,
    SOURCE_WIN32_WM_LBUTTONDOWN,
    SOURCE_WIN32_WM_LBUTTONDBLCLK,
)


class SourceSupportStartPointerCandidateError(ValueError):
    pass


@dataclass(frozen=True)
class SourceSupportStartPointerCandidate:
    """Original source modal dispatch prefilter only, NOT hit acceptance."""
    original_win32_message: int
    original_native_client_point: tuple[int, int]
    source_modal_window_reached: bool
    source_candidate_row_indices: tuple[int, ...]
    source_candidate_native_control_ids: tuple[int, ...]
    original_window_route: NativeWindowRoute | None
    native_row_event_accepted: bool = False

    @property
    def has_candidate(self) -> bool:
        return bool(self.source_candidate_row_indices)


def project_source_supportstart_pointer_candidate(
    editor: OriginalSupportStartEditorProjection,
    *,
    win32_message: int,
    packed_lparam: int,
    original_guard_nonzero: bool,
    source_windows: tuple[NativeWindow, ...],
    source_modal_window_identity: int,
    owner_capture_flag_nonzero: bool,
    actual_viewport_size: tuple[int, int],
    post_window_parent_callback_state_qualified: bool,
) -> SourceSupportStartPointerCandidate:
    """Source 0x653480 candidate only after all upstream owner prerequisites.

    Window/modal registration and absolute native viewport must be given
    from the actual source state. The function checks original modal
    bounds and vft+0x44 eligibility and requires the caller to qualify
    that the original 0x4D05E0 event0 parent callback has completed.
    Even a returned candidate is NOT proof of native 0x64F7A0
    acceptance, actual clicked staff, or any editor/GUI mutation.
    """
    if type(editor) is not OriginalSupportStartEditorProjection:
        raise TypeError("Require original source-qualified seven-row editor")
    if (type(source_modal_window_identity) is not int
            or source_modal_window_identity < 0):
        raise SourceSupportStartPointerCandidateError(
            "Require source-owned native modal window pointer identity"
        )
    if type(post_window_parent_callback_state_qualified) is not bool:
        raise SourceSupportStartPointerCandidateError(
            "Require explicit original parent callback state qualification"
        )
    if type(win32_message) is not int or win32_message not in (
        SOURCE_WIN32_WM_LBUTTONDOWN, SOURCE_WIN32_WM_LBUTTONDBLCLK,
    ):
        raise SourceSupportStartPointerCandidateError(
            "Only actual original Win32 left-button down/double-click")
    x0,y0 = original_supportstart_native_modal_origin(
        viewport_size=actual_viewport_size
    )
    w,h = SOURCE_SUPPORTSTART_NATIVE_SIZE
    modal = tuple(
        window for window in source_windows
        if window.source_identity == source_modal_window_identity
    )
    if len(modal) != 1 or modal[0].bounds != (x0,y0,x0+w,y0+h):
        raise SourceSupportStartPointerCandidateError(
            "Registered source modal object or actual viewport bounds inconsistent"
        )
    if not modal[0].virtual44_eligible:
        raise SourceSupportStartPointerCandidateError(
            "Original PSupportStart vft+0x44 must return one"
        )
    result = project_original_mywindow_left_button_event(
        win32_message=win32_message,
        packed_lparam=packed_lparam,
        original_guard_nonzero=original_guard_nonzero,
        windows=source_windows,
        owner_capture_flag_nonzero=owner_capture_flag_nonzero,
    )
    point = result.native_client_point
    route = result.window_down_route
    if route is None:
        return SourceSupportStartPointerCandidate(
            win32_message, point, False, (), (), None
        )
    indices = tuple(
        i for i in route.dispatched_indices
        if source_windows[i].source_identity == source_modal_window_identity
    )
    if not indices:
        return SourceSupportStartPointerCandidate(
            win32_message, point, False, (), (), route
        )
    if not post_window_parent_callback_state_qualified:
        raise SourceSupportStartPointerCandidateError(
            "Original prechild parent event0 input state not source-qualified"
        )
    candidates = tuple(
        i for i, row in enumerate(editor.rows)
        if original_supportstart_native_row_window_event_candidate(
            i,
            source_screen_point=point,
            viewport_size=actual_viewport_size,
            native_row_control_dword=row.parent,
        )
    )
    return SourceSupportStartPointerCandidate(
        win32_message, point, True, candidates,
        tuple(original_supportstart_row_callback_contract(i).original_native_control_event_id
              for i in candidates),
        route,
    )
