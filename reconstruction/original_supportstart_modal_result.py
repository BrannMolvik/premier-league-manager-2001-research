"""Original TeamSelect SupportStart nested modal result ownership.

Native TeamSelect 0x4D91C0 first calls owner 0x64F960 (result saved in EBX),
then tests selection bit15 via 0x652F80. Only when both accept does it
enter original 0x450BB0 PSupportStart. Inside the modal 0x4D05E0
action event 1 writes +0x1DE4 = 0 (Cancel, NO 0x4D0830 Apply);
action event 2 invokes 0x4D0830 and writes +0x1DE4 = 1.
0x450BB0 returns that inner BYTE in AL, but outer 0x4D91C0
overwrites EAX with the saved event-acceptance EBX at 0x4D922C.

Original 0x6539F0 posts WM_USER(0x400,wParam=0) on BOTH actions via
USER32.PostMessageA, and MyWindow::0x532B80 consumes it as a loop
termination without normal DispatchMessageA. That Win32 loop's result is
zero for BOTH actions, whereas the modal byte differs (0 vs 1).

This is the SOURCE CONTROL-RESULT boundary, not a new GUI/input handler.
It DOES NOT model native linked-list cleanup or the exact mapping of
screen-coordinate and keyboard input to action event 1/2. In particular,
a handled Cancel is NOT equivalent to a failed event or to Apply.
"""
from __future__ import annotations

from dataclasses import dataclass

from original_supportstart_layout import original_supportstart_action_children


class OriginalSupportStartModalResultError(ValueError):
    """The original modal event owner has not been qualified."""


@dataclass(frozen=True)
class SourceOriginalSupportStartModalDispatch:
    owner_event_accepted: bool
    selected_control_bit15: bool
    modal_opened: bool
    native_action_event: int | None
    native_modal_result_byte: int | None
    native_apply_called: bool
    outer_teamselect_handler_result: int

    @property
    def source_posted_close_message(self) -> tuple[int, int] | None:
        """Only after source-qualified native event1/2: (WM_USER, wParam).

        Both original actions at 0x4D0618 / 0x4D062A push literal zero
        into 0x6539F0 -> USER32.PostMessageA(Msg=0x400,wParam=0).
        The original MyWindow 0x532B80 message pump consumes 0x400
        without TranslateMessage/DispatchMessage and returns wParam=0.
        This is NOT the PSupportStart Apply/Cancel modal result byte.
        """
        return (0x400, 0) if self.modal_opened else None

    @property
    def source_window_loop_return(self) -> int | None:
        """Original MyWindow WM_USER terminates with *wParam*, not Apply."""
        return 0 if self.modal_opened else None

    @property
    def original_editor_applied(self) -> bool:
        return self.native_modal_result_byte == 1


def source_teamselect_supportstart_modal_dispatch(
    *,
    owner_event_accepted: bool,
    selected_control_bit15: bool,
    native_action_event: int | None = None,
) -> SourceOriginalSupportStartModalDispatch:
    """Project native event/selection gate and INNER vs OUTER return.

    The caller supplies an already source-qualified action event, never
    a clicked visual rectangle. This pure projection changes no staff,
    original user list, name, modal, presenter, or process RNG.
    """
    if (type(owner_event_accepted) is not bool
            or type(selected_control_bit15) is not bool):
        raise OriginalSupportStartModalResultError(
            "Require original event gate and selected-bit boolean"
        )
    opened = owner_event_accepted and selected_control_bit15
    if not opened:
        if native_action_event is not None:
            raise OriginalSupportStartModalResultError(
                "Native modal event cannot occur when original gate rejects"
            )
        return SourceOriginalSupportStartModalDispatch(
            owner_event_accepted=owner_event_accepted,
            selected_control_bit15=selected_control_bit15,
            modal_opened=False,
            native_action_event=None,
            native_modal_result_byte=None,
            native_apply_called=False,
            outer_teamselect_handler_result=int(owner_event_accepted),
        )
    child_actions = {
        action.native_event: action
        for action in original_supportstart_action_children()
    }
    if type(native_action_event) is not int or native_action_event not in child_actions:
        raise OriginalSupportStartModalResultError(
            "Source PSupportStart exit/tick action event 1 or 2 required"
        )
    child = child_actions[native_action_event]
    return SourceOriginalSupportStartModalDispatch(
        owner_event_accepted=True,
        selected_control_bit15=True,
        modal_opened=True,
        native_action_event=native_action_event,
        native_modal_result_byte=child.result_byte_after_native_handler,
        native_apply_called=child.invokes_full_original_apply,
        # 0x4D922C moves saved EBX into EAX after 0x450BB0 returns.
        outer_teamselect_handler_result=1,
    )
