"""Original 5DB3BD–5DB6FA human callback gate, source-only.

The original re-reads human-club predicates within the alternate branch.
Do not collapse them to a single club-owner Boolean: callback-side effects
can precede later tests. This only returns reached callsite order, never
executes 5DC510/5DC650 or updates the original manager+670 event queue.
"""
from dataclasses import dataclass


class OriginalHumanCallbackDispatchError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginalHumanCallbackDispatch:
    original_callback_callsites: tuple[int, ...]
    original_694_dword0_ebx_bonus_reached: bool
    original_reached_5db4d7_alternate: bool
    original_common_5db6fa_reached: bool = True
    original_native_callbacks_executed: bool = False
    game_state_mutated: bool = False


def source_original_5db37c_human_callback_dispatch(
    *,
    original_first_4037b0_at_5db3b2: bool,
    original_flag_at_5db3b9: int,
    original_first_4037b0_at_5db4d7: bool | None = None,
    original_second_4037b0_at_5db4e2: bool | None = None,
    original_first_4037b0_at_5db4f3: bool | None = None,
    original_second_4037b0_at_5db5f5: bool | None = None,
) -> SourceOriginalHumanCallbackDispatch:
    if type(original_first_4037b0_at_5db3b2) is not bool:
        raise OriginalHumanCallbackDispatchError('first original human predicate required')
    if type(original_flag_at_5db3b9) is not int or not 0 <= original_flag_at_5db3b9 <= 255:
        raise OriginalHumanCallbackDispatchError('original source byte flag required')
    optional = (
        original_first_4037b0_at_5db4d7,
        original_second_4037b0_at_5db4e2,
        original_first_4037b0_at_5db4f3,
        original_second_4037b0_at_5db5f5,
    )
    def reject_extra(allowed: tuple[int, ...]):
        if any(value is not None for i, value in enumerate(optional) if i not in allowed):
            raise OriginalHumanCallbackDispatchError('unreached original human predicate supplied')
    if original_flag_at_5db3b9 == 0:
        reject_extra(())
        if original_first_4037b0_at_5db3b2:
            return SourceOriginalHumanCallbackDispatch((0x5DB456, 0x5DB4B9), True, False)
        return SourceOriginalHumanCallbackDispatch((), False, False)
    if type(optional[0]) is not bool:
        raise OriginalHumanCallbackDispatchError('reached 5DB4D7 original human predicate required')
    if not optional[0]:
        if type(optional[1]) is not bool:
            raise OriginalHumanCallbackDispatchError('reached 5DB4E2 second-side predicate required')
        if not optional[1]:
            reject_extra((0, 1))
            return SourceOriginalHumanCallbackDispatch((), False, True)
    elif optional[1] is not None:
        raise OriginalHumanCallbackDispatchError('5DB4E2 bypassed when first club is human')
    if type(optional[2]) is not bool or type(optional[3]) is not bool:
        raise OriginalHumanCallbackDispatchError('reached alternate human predicate rereads required')
    calls = ((0x5DB58D, 0x5DB5F0) if optional[2] else ()) + (
        (0x5DB692, 0x5DB6F5) if optional[3] else ()
    )
    return SourceOriginalHumanCallbackDispatch(calls, False, True)
