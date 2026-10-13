"""Authenticated original 0x532B80 Windows message pump source contract.

Original private footballmanager.exe SHA256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3
STATIC DISASSEMBLY ONLY. Does not execute Windows message APIs or original.
Original 0x532570 installs vtable 0x7CB294 on global view owner 0x877960,
vtable0 at 0x532B80. 0x5331C0→0x532650→0x654210 pushes a nested
0x51F490 view on stack, invokes global owner vtable0, then 0x654360
pops that view. Original 0x6539F0 PostMessageA posts WM_USER=0x400,
wParam masked to WORD. The 0x532B80 actual PeekMessage/GetMessage loop
returns on WM_USER or GetMessage=0, not when a Quick match is computed.
This is typed source evidence for later GUI integration, not a new game.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

NATIVE_FASTVIEW_VIEW_OWNER_VA = 0x877960
NATIVE_FASTVIEW_VIEW_CTOR_VA = 0x532570
NATIVE_FASTVIEW_VIEW_VTABLE_VA = 0x7CB294
NATIVE_FASTVIEW_VIEW_VTABLE0_VA = 0x532B80
NATIVE_FASTVIEW_MODAL_ACTIVATOR_VA = 0x654210
NATIVE_FASTVIEW_NESTED_VIEW_PUSH_VA = 0x6542B0
NATIVE_FASTVIEW_NESTED_VIEW_POP_VA = 0x654360
NATIVE_FASTVIEW_WINDOW_POST_VA = 0x6539F0
NATIVE_FASTVIEW_WM_USER = 0x400
NATIVE_FASTVIEW_PEEKMESSAGE_IAT_VA = 0x7BD29C
NATIVE_FASTVIEW_GETMESSAGE_IAT_VA = 0x7BD2A0
NATIVE_FASTVIEW_TRANSLATEMESSAGE_IAT_VA = 0x7BD2A4
NATIVE_FASTVIEW_DISPATCHMESSAGE_IAT_VA = 0x7BD2AC
NATIVE_FASTVIEW_WAITMESSAGE_IAT_VA = 0x7BD2B0
NATIVE_FASTVIEW_POSTMESSAGE_IAT_VA = 0x7BD2D8


class OriginalFastViewMessageSourceError(ValueError):
    """The original native message / owner source has not been established."""


class OriginalFastViewPumpAction(Enum):
    WAIT_FOR_MESSAGE = "wait_message"
    UPDATE_NESTED_VIEW = "update_nested_view"
    TRANSLATE_DISPATCH = "translate_dispatch"
    RETURN_FROM_MODAL = "return_from_modal"


@dataclass(frozen=True)
class OriginalFastViewWin32PostedEvent:
    original_hwnd: int
    message: int
    wparam: int
    lparam: int


def source_fastview_original_post_wm_user_6539f0(
    *, original_hwnd_from_view_plus64: int, original_event_dword: int,
) -> OriginalFastViewWin32PostedEvent:
    """Source PostMessageA(hwnd, WM_USER, event & 0xFFFF, 0)."""
    if (type(original_hwnd_from_view_plus64) is not int
            or not 0 < original_hwnd_from_view_plus64 <= 0xFFFFFFFF
            or type(original_event_dword) is not int
            or not 0 <= original_event_dword <= 0xFFFFFFFF):
        raise OriginalFastViewMessageSourceError("native HWND and event DWORD required")
    return OriginalFastViewWin32PostedEvent(
        original_hwnd_from_view_plus64,NATIVE_FASTVIEW_WM_USER,
        original_event_dword & 0xFFFF,0)


@dataclass(frozen=True)
class OriginalFastViewWin32MessageObservation:
    peek_had_message: bool
    active_nested_view_count: int
    get_message_result: int | None = None
    native_msg_type: int | None = None
    native_msg_wparam: int | None = None


@dataclass(frozen=True)
class OriginalFastViewWin32PumpStep:
    action: OriginalFastViewPumpAction
    exit_wparam: int | None = None
    observed_message: int | None = None


def source_fastview_original_modal_step_532b80(
    observed: OriginalFastViewWin32MessageObservation,
) -> OriginalFastViewWin32PumpStep:
    """One actual 0x532B80 Win32 event pump iteration; no artificial timeout.

    Native PeekMessageA(PM_NOREMOVE) false: when active depth > 0,
    0x5329D0 view update is called; otherwise WaitMessage. True:
    GetMessageA is called. GetMessage result 0 or MSG.message=0x400
    returns original MSG.wParam; else TranslateMessage/DispatchMessage
    and repeat. The original has no error check for GetMessage -1,
    so the port fail-closes rather than trusting undefined MSG contents.
    """
    if type(observed) is not OriginalFastViewWin32MessageObservation:
        raise OriginalFastViewMessageSourceError("typed original MSG observation required")
    if type(observed.peek_had_message) is not bool:
        raise OriginalFastViewMessageSourceError("native PeekMessage BOOL required")
    if (type(observed.active_nested_view_count) is not int
            or not 0 <= observed.active_nested_view_count <= 0x7FFFFFFF):
        raise OriginalFastViewMessageSourceError("native view stack count required")
    if not observed.peek_had_message:
        if any(x is not None for x in (
                observed.get_message_result,observed.native_msg_type,
                observed.native_msg_wparam)):
            raise OriginalFastViewMessageSourceError("unreached GetMessage/MSG supplied")
        return OriginalFastViewWin32PumpStep(
            OriginalFastViewPumpAction.UPDATE_NESTED_VIEW
            if observed.active_nested_view_count else OriginalFastViewPumpAction.WAIT_FOR_MESSAGE)
    if (type(observed.get_message_result) is not int
            or observed.get_message_result not in (-1,0,1)):
        raise OriginalFastViewMessageSourceError("actual GetMessage return required")
    if (type(observed.native_msg_type) is not int
            or not 0 <= observed.native_msg_type <= 0xFFFFFFFF
            or type(observed.native_msg_wparam) is not int
            or not 0 <= observed.native_msg_wparam <= 0xFFFFFFFF):
        raise OriginalFastViewMessageSourceError("original MSG.message and wParam DWORD required")
    if observed.get_message_result == -1:
        raise OriginalFastViewMessageSourceError("GetMessage error has unqualified original MSG")
    if (observed.get_message_result == 0 or
            observed.native_msg_type == NATIVE_FASTVIEW_WM_USER):
        return OriginalFastViewWin32PumpStep(
            OriginalFastViewPumpAction.RETURN_FROM_MODAL,
            observed.native_msg_wparam, observed.native_msg_type)
    return OriginalFastViewWin32PumpStep(
        OriginalFastViewPumpAction.TRANSLATE_DISPATCH,
        observed_message=observed.native_msg_type)


@dataclass(frozen=True)
class OriginalFastViewNativeViewReturn:
    """Only proves original Win32 activation returned, NOT match completion."""
    native_exit_message: int
    native_exit_wparam: int
    number_of_pump_observations: int
    number_of_view_updates: int
    dispatched_message_types: tuple[int, ...]


def source_fastview_original_nested_modal_trace_532b80(
    *, native_source_messages: tuple[OriginalFastViewWin32MessageObservation, ...],
) -> OriginalFastViewNativeViewReturn:
    """Original-source event sequence must exit before 0x533CA0 writeback."""
    if (type(native_source_messages) is not tuple or
            not 1 <= len(native_source_messages) <= 65536):
        raise OriginalFastViewMessageSourceError("bounded nonempty original MSG history required")
    updated=0
    dispatched=[]
    for i,item in enumerate(native_source_messages):
        step=source_fastview_original_modal_step_532b80(item)
        if step.action is OriginalFastViewPumpAction.UPDATE_NESTED_VIEW:
            updated+=1
        elif step.action is OriginalFastViewPumpAction.TRANSLATE_DISPATCH:
            dispatched.append(step.observed_message)
        elif step.action is OriginalFastViewPumpAction.RETURN_FROM_MODAL:
            if i != len(native_source_messages)-1:
                raise OriginalFastViewMessageSourceError("native Win32 modal cannot run after return")
            return OriginalFastViewNativeViewReturn(
                step.observed_message,step.exit_wparam,len(native_source_messages),
                updated,tuple(dispatched))
    raise OriginalFastViewMessageSourceError(
        "no original Win32 modal return observed; postmodal player writeback unavailable")


NATIVE_FASTVIEW_VIEW_CLOSE_IF_ACTIVE_VA = 0x653A10


def source_fastview_original_conditional_view_close_653a10(
    *, original_close_request_is_nonzero: bool,
    original_view_owner_event_word_plus68: int | None,
    original_nested_window_hwnd: int | None,
) -> OriginalFastViewWin32PostedEvent | None:
    """0x653A10: only a nonzero close request posts 0x400 via 0x6539F0.

    Source 0x653A10 tests input DWORD, then reads WORD [owner+0x68]
    and follows [owner+0x08]->+0x24 to the nested original window
    posting owner. It calls 0x6539F0, whose PostMessageA masks wParam
    to 16 bits; it neither closes the window directly nor simulates
    any match. When no request, native source reads neither field.
    """
    if type(original_close_request_is_nonzero) is not bool:
        raise OriginalFastViewMessageSourceError("native close request BOOL required")
    if not original_close_request_is_nonzero:
        if original_view_owner_event_word_plus68 is not None or original_nested_window_hwnd is not None:
            raise OriginalFastViewMessageSourceError(
                "native unvisited close-owner fields must not be supplied")
        return None
    if (type(original_view_owner_event_word_plus68) is not int or
        not 0 <= original_view_owner_event_word_plus68 <= 0xFFFF):
        raise OriginalFastViewMessageSourceError(
            "actual native owner WORD+0x68 event code required")
    return source_fastview_original_post_wm_user_6539f0(
        original_hwnd_from_view_plus64=original_nested_window_hwnd,
        original_event_dword=original_view_owner_event_word_plus68)
