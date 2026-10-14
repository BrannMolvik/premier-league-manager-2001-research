"""Source-only 5DC510 optional 5DC650 append then mandatory own FIFO event.

Requires independently reached source stage inputs; does not call or commit
native code/heap/FPU/GUI. 5DC650 may return zero early, whereas 5DC510
then still proceeds to its own event allocation/queue append.
"""
from dataclasses import dataclass
from original_native_5dc650_event_tail import (
    SourceOriginal5DC650EventTailReceipt,
    source_original_5dc650_reached_record_and_fifo,
)
from original_native_5dc510_event_tail import (
    SourceOriginal5DC510EventTailReceipt,
    source_original_5dc510_record_tail_append,
)

class Original5DC510TwoAppendError(ValueError):
    pass

@dataclass(frozen=True)
class SourceOriginal5DC510TwoAppendReceipt:
    optional_5dc650_first_append: SourceOriginal5DC650EventTailReceipt | None
    mandatory_5dc510_second_append: SourceOriginal5DC510EventTailReceipt
    original_true_native_call_executed: bool = False
    live_game_state_updated: bool = False

def source_original_5dc510_optional_then_main_append(
    *, original_5dc650_return_al_nonzero: bool,
    original_5dc650_reached_inputs_if_appended: dict | None,
    original_5dc510_main_reached_inputs: dict,
) -> SourceOriginal5DC510TwoAppendReceipt:
    if type(original_5dc650_return_al_nonzero) is not bool:
        raise Original5DC510TwoAppendError('actual native 5DC650 AL result required')
    if type(original_5dc510_main_reached_inputs) is not dict:
        raise Original5DC510TwoAppendError('reached 5DC510 main allocation input required')
    earlier=None
    if original_5dc650_return_al_nonzero:
        if type(original_5dc650_reached_inputs_if_appended) is not dict:
            raise Original5DC510TwoAppendError('successful 5DC650 must have a source event')
        earlier=source_original_5dc650_reached_record_and_fifo(
            **original_5dc650_reached_inputs_if_appended)
        old=earlier.original_source_fifo_projection
        main=original_5dc510_main_reached_inputs
        if (main.get('original_owner_pointer') !=
                original_5dc650_reached_inputs_if_appended.get('original_owner_pointer_at_5dc854')
            or main.get('original_owner_at_5dc5d9') != old.owner_after_append
            or main.get('original_old_tail_pointer_if_nonempty') != old.original_new_wrapper_pointer
            or main.get('original_old_tail_wrapper_if_nonempty') != old.new_native_wrapper_after_append
            or main.get('original_payload_pointer_allocated') in
                    (old.original_new_payload_pointer,old.original_new_wrapper_pointer)
            or main.get('original_wrapper_pointer_allocated') in
                    (old.original_new_payload_pointer,old.original_new_wrapper_pointer)):
            raise Original5DC510TwoAppendError(
                'original two native 617D70 appends have contradictory owner/tail/heap identity')
    elif original_5dc650_reached_inputs_if_appended is not None:
        raise Original5DC510TwoAppendError(
            'original 5DC650 returned AL zero; its event append was never reached')
    try:
        after=source_original_5dc510_record_tail_append(
            **original_5dc510_main_reached_inputs)
    except (TypeError,ValueError) as e:
        raise Original5DC510TwoAppendError('original main event invalid') from e
    return SourceOriginal5DC510TwoAppendReceipt(earlier,after)
