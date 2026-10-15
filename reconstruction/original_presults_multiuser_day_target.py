"""Native PResults 4A83F0 multi-registered-user earliest match date boundary.

Canonical original PE (SHA 833bf95e...b7cc3) static source, not executed.
4A8435 sets 8755D4=0; for each registered manager it reaches 4139D0
then 615D10(947AD8, current date, manager+5B4 club*, 1).
4A8463..471 chooses earliest event+0x10, ties retain earlier manager.
4A8473..488 increments/modulo registered user count.
If any match source exists, 510A20 derives next match date; original
only subtracts one day if current+1 < match date. Otherwise
616A30 obtains next date-bucket limit, subtracts one day.
4A84D2 caps target to current + global 87753C. 4A84E5
pre-counts via 4A7210 only when current < capped target.

This does not prove original 615D10 execution, date event+0x10 contents,
510A20 return, primary/secondary collection parity, day callback effects,
or any modern GameState/GUI behavior. Caller must supply actual reached
source outputs rather than inferred fixture names or calendar scores.
"""
from dataclasses import dataclass


class OriginalPResultsMultiuserSourceError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalPResultsRegisteredMatchCandidate:
    native_registered_user_pointer: int
    native_user_5b4_club_pointer: int
    source_615d10_event_pointer: int
    source_event10_date_slot: int | None

    def __post_init__(self):
        for val in (self.native_registered_user_pointer,
                    self.native_user_5b4_club_pointer,
                    self.source_615d10_event_pointer):
            if type(val) is not int or not 0<=val<=0xffffffff:
                raise OriginalPResultsMultiuserSourceError("original reached user/club/615D10 pointer DWORD required")
        if not self.native_registered_user_pointer or not self.native_user_5b4_club_pointer:
            raise OriginalPResultsMultiuserSourceError("original selected registered user and club cannot be null")
        if self.source_615d10_event_pointer==0:
            if self.source_event10_date_slot is not None:
                raise OriginalPResultsMultiuserSourceError("null original 615D10 skips event+0x10 read")
        elif type(self.source_event10_date_slot) is not int or not 0<=self.source_event10_date_slot<=0x7fffffff:
            raise OriginalPResultsMultiuserSourceError("reached original event+0x10 source date slot required")


@dataclass(frozen=True)
class SourceOriginalPResultsMultiuserTarget:
    earliest_reached_event_pointer: int | None
    earliest_original_manager_ordinal: int | None
    original_selected_registered_user_ordinal_after_loop: int
    original_current_date_index: int
    original_native_target_date_index: int
    source_original_precount_4a7210_reached: bool
    source_original_615d10_callbacks_executed: bool = False
    original_native_510a20_executed: bool = False
    original_world_state_mutated: bool = False
    real_human_gui_accepted: bool = False


def source_original_presults_4a83f0_multiuser_target(
    *,
    original_registered_615d10_results: tuple[OriginalPResultsRegisteredMatchCandidate,...],
    original_current_date_global_9847fc: int,
    original_max_days_global_87753c: int,
    original_selected_event_510a20_date: int | None,
    original_no_match_616a30_next_date: int | None,
) -> SourceOriginalPResultsMultiuserTarget:
    candidates=original_registered_615d10_results
    current=original_current_date_global_9847fc
    days=original_max_days_global_87753c
    if (type(candidates) is not tuple or not 1<=len(candidates)<=6
        or any(type(x) is not OriginalPResultsRegisteredMatchCandidate for x in candidates)
        or type(current) is not int or not 0<=current<=0x7fffffff
        or type(days) is not int or not 0<=days<=0x7fffffff-current):
        raise OriginalPResultsMultiuserSourceError(
            "source ordered original 1–6 registered human results, date and cap required")
    seen=set()
    earliest=None
    best_ordinal=None
    best_date=None
    for ordinal,c in enumerate(candidates):
        if c.native_registered_user_pointer in seen:
            raise OriginalPResultsMultiuserSourceError("source registry user pointer duplicated")
        seen.add(c.native_registered_user_pointer)
        if c.source_615d10_event_pointer and (best_date is None or
                c.source_event10_date_slot < best_date):
            earliest=c.source_615d10_event_pointer
            best_date=c.source_event10_date_slot
            best_ordinal=ordinal
    if earliest is not None:
        if (type(original_selected_event_510a20_date) is not int
                or not 0<=original_selected_event_510a20_date<=0x7fffffff
                or original_no_match_616a30_next_date is not None):
            raise OriginalPResultsMultiuserSourceError(
                "source selected event requires original 510A20 date; 616A30 bypassed")
        reached=original_selected_event_510a20_date
        target = reached-1 if current+1<reached else reached
    else:
        if (type(original_no_match_616a30_next_date) is not int
                or not 1<=original_no_match_616a30_next_date<=0x7fffffff
                or original_selected_event_510a20_date is not None):
            raise OriginalPResultsMultiuserSourceError(
                "source null match requires reached 616A30 next date, no 510A20")
        target=original_no_match_616a30_next_date-1
    target=min(current+days,target)
    return SourceOriginalPResultsMultiuserTarget(
        earliest,best_ordinal,0,current,target,target>current)
