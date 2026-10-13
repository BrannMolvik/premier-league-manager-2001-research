"""Original PResults native dated-event pre-count and two-pass tick source.

Owner-original FM2001 PE SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3
is analyzed STATICALLY; not executed or bundled. This value model is based
on original 0x4A7210 and 0x6168C0/0x4A71F0. It accepts genuine
qualified native event/payload virtual-result values, and outputs
native callback/tick ORDER only. It does not mutate GameState, invoke
original event vtables, infer an event class, draw PResults, present
FastView, or authorize GUI completion.
"""
from __future__ import annotations
from dataclasses import dataclass


SOURCE_PRESULTS_PRECOUNT_VA = 0x4A7210
SOURCE_PRESULTS_EXECUTE_VA = 0x6168C0
SOURCE_PRESULTS_FIRST_HUMAN_TEST_VA = 0x616990
SOURCE_PRESULTS_FIRST_COUNTRY_TEST_VA = 0x510C90
SOURCE_PRESULTS_TICK_VA = 0x4A71F0
SOURCE_PRESULTS_GLOBAL_CURRENT_DATE_VA = 0x9847FC
SOURCE_PRESULTS_FIRST_DATE_ARRAY_VA = 0x947AD8
SOURCE_PRESULTS_FIRST_DATE_BASE_VA = 0x947AE0
SOURCE_PRESULTS_SECOND_DATE_ARRAY_VA = 0x947AF0
SOURCE_PRESULTS_SECOND_DATE_BASE_VA = 0x947AF8
SOURCE_PRESULTS_COMPLETED_BIT = 0x01
SOURCE_PRESULTS_FILTER_BIT = 0x40
SOURCE_PRESULTS_NATIVE_SIGNED_MAX = 0x7FFFFFFF


class OriginalPResultsEventSourceError(ValueError):
    """A native event owner/value is absent, malformed, or not reached."""


@dataclass(frozen=True)
class OriginalPResultsNativeQueuedEvent:
    """Caller-supplied actual original native event node and virtual evidence.

    before_event8 and before_payload44 are the source DWORD values read
    from event+8 and its vtable+0x18 payload+0x44. The virtual+0x0C
    pre-count return must be supplied separately and may disagree
    with the later execution gates, just as in the original.
    First-pass human/country callback results are ONLY supplied when
    reached. The first event vtable+0x10 can mutate the same native
    event/payload before the second pass; if reached, both AFTER values
    must be supplied from its actual effects (no guessed completion).
    """
    original_event_pointer: int
    source_virtual_0c_nonzero: bool
    before_event8: int
    before_payload44: int
    first_pass_616990_human_owned: bool | None = None
    first_pass_510c90_country_member: bool | None = None
    after_first_callback_event8: int | None = None
    after_first_callback_payload44: int | None = None

    def __post_init__(self):
        if (type(self.original_event_pointer) is not int or
                not 0<self.original_event_pointer<=0xFFFFFFFF or
                type(self.source_virtual_0c_nonzero) is not bool or
                any(type(x) is not int or not 0<=x<=0xFFFFFFFF
                    for x in (self.before_event8,self.before_payload44))):
            raise OriginalPResultsEventSourceError(
                "native pointer, original virtual+0x0C predicate and DWORD event/payload values required")
        for name in ("first_pass_616990_human_owned",
                     "first_pass_510c90_country_member"):
            val=getattr(self,name)
            if val is not None and type(val) is not bool:
                raise OriginalPResultsEventSourceError(
                    "only original reached native human/country callback bool permitted")
        for name in ("after_first_callback_event8",
                     "after_first_callback_payload44"):
            val=getattr(self,name)
            if val is not None and (type(val) is not int or not 0<=val<=0xFFFFFFFF):
                raise OriginalPResultsEventSourceError(
                    "actual original event/payload mutated DWORD required")


@dataclass(frozen=True)
class OriginalPResultsSourceCallback:
    original_event_pointer: int
    source_pass: int
    native_event_virtual_method_offset: int
    native_progress_callback_va: int


@dataclass(frozen=True)
class OriginalPResultsDatedEventReceipt:
    original_progress_callbacks: tuple[OriginalPResultsSourceCallback, ...]
    original_6168c0_return_al_nonzero: bool

    @property
    def source_progress_tick_count(self) -> int:
        return len(self.original_progress_callbacks)


def _clean_for_execution(event8: int, flags44: int) -> bool:
    return event8==0 and not flags44 & (SOURCE_PRESULTS_FILTER_BIT|SOURCE_PRESULTS_COMPLETED_BIT)


def source_original_presults_native_current_date_two_pass_6168c0(
    *, original_ordered_date_nodes: tuple[OriginalPResultsNativeQueuedEvent, ...],
) -> OriginalPResultsDatedEventReceipt:
    """Source original first pass followed by second pass over SAME date list.

    First loop 0x6168DE..0x616931: event v+0x18 payload, event+8=0,
    payload flags+0x44 bit0/6 both clear; if original 0x616990
    human-pointer check NONZERO skip, else original 0x510C90
    country check NONZERO skip. If both false, event v+0x10
    processes original work then PResults 0x4A71F0 increments one tick.

    Second loop 0x616946..0x616985: event v+0x18, event+8=0,
    payload bit6 AND bit0 clear; calls event v+0x10 and ticks with
    NO 616990/510C90 gate. Native source returns AL=1 only when
    this SECOND pass processes at least one callback, not merely
    because the first pass processed events. Event+8/flags may have
    been mutated by the first pass; require authentic AFTER values
    only if first pass invoked. No extra implicit suppression.
    """
    if type(original_ordered_date_nodes) is not tuple or any(
        type(e) is not OriginalPResultsNativeQueuedEvent
        for e in original_ordered_date_nodes
    ):
        raise OriginalPResultsEventSourceError("source ordered linked native date-event tuple required")
    callbacks=[]
    first_reached=[]
    for event in original_ordered_date_nodes:
        clean=_clean_for_execution(event.before_event8,event.before_payload44)
        human=event.first_pass_616990_human_owned
        country=event.first_pass_510c90_country_member
        if not clean:
            if human is not None or country is not None:
                raise OriginalPResultsEventSourceError(
                    "original early-flag return cannot read human/country callbacks")
            reached=False
        elif human is None:
            raise OriginalPResultsEventSourceError(
                "native 616990 human-result required on reached first-pass event")
        elif human:
            if country is not None:
                raise OriginalPResultsEventSourceError(
                    "native 510C90 country callback not reached on human-owned event")
            reached=False
        elif country is None:
            raise OriginalPResultsEventSourceError(
                "original 510C90 source country-result required on reached event")
        else:
            reached=not country
        if reached:
            if (event.after_first_callback_event8 is None or
                event.after_first_callback_payload44 is None):
                raise OriginalPResultsEventSourceError(
                    "native virtual+0x10 mutation source required before second original pass")
            callbacks.append(OriginalPResultsSourceCallback(
                event.original_event_pointer,1,0x10,SOURCE_PRESULTS_TICK_VA))
        elif (event.after_first_callback_event8 is not None or
              event.after_first_callback_payload44 is not None):
            raise OriginalPResultsEventSourceError(
                "unreached original event vtable+0x10 after state cannot be supplied")
        first_reached.append(reached)

    second_ran=False
    for event,first in zip(original_ordered_date_nodes,first_reached):
        event8=(event.after_first_callback_event8 if first else event.before_event8)
        flags=(event.after_first_callback_payload44 if first else event.before_payload44)
        if _clean_for_execution(event8,flags):
            callbacks.append(OriginalPResultsSourceCallback(
                event.original_event_pointer,2,0x10,SOURCE_PRESULTS_TICK_VA))
            second_ran=True
    # Source callback emission ORDER in each native pass is linked-list order.
    return OriginalPResultsDatedEventReceipt(tuple(callbacks),second_ran)


@dataclass(frozen=True)
class OriginalPResultsNativePreCountNode:
    """Pre-count virtual+0x0C short-circuits later node+8/payload reads."""
    original_event_pointer: int
    source_virtual_0c_nonzero: bool
    reached_event8: int | None = None
    reached_payload44: int | None = None

    def __post_init__(self):
        if (type(self.original_event_pointer) is not int or
            not 0<self.original_event_pointer<=0xFFFFFFFF or
            type(self.source_virtual_0c_nonzero) is not bool):
            raise OriginalPResultsEventSourceError("precount source event pointer and virtual result required")
        if not self.source_virtual_0c_nonzero:
            if self.reached_event8 is not None or self.reached_payload44 is not None:
                raise OriginalPResultsEventSourceError(
                    "native virtual+0x0C zero bypasses original event+8 and payload getters")
            return
        if (type(self.reached_event8) is not int or
            not 0<=self.reached_event8<=0xFFFFFFFF):
            raise OriginalPResultsEventSourceError("original reached event+8 DWORD required")
        if self.reached_event8:
            if self.reached_payload44 is not None:
                raise OriginalPResultsEventSourceError(
                    "native nonzero event+8 bypasses original payload+0x44 getter")
            return
        if (type(self.reached_payload44) is not int or
            not 0<=self.reached_payload44<=0xFFFFFFFF):
            raise OriginalPResultsEventSourceError("original reached payload+0x44 DWORD required")


@dataclass(frozen=True)
class OriginalPResultsNativeDateBucket:
    original_date_index: int
    original_linked_nodes: tuple[OriginalPResultsNativePreCountNode, ...]

    def __post_init__(self):
        if (type(self.original_date_index) is not int or
            not 0<=self.original_date_index<=SOURCE_PRESULTS_NATIVE_SIGNED_MAX or
            type(self.original_linked_nodes) is not tuple or
            any(type(e) is not OriginalPResultsNativePreCountNode
                for e in self.original_linked_nodes)):
            raise OriginalPResultsEventSourceError(
                "original date and authentic linked native event nodes required")


def source_original_presults_precount_4a7210(
    *, original_current_date_global_9847fc: int,
    original_inclusive_upper_date: int,
    original_947ad8_date_buckets: tuple[OriginalPResultsNativeDateBucket, ...],
    original_already_processed_64: int,
) -> int:
    """Exact original pre-count by virtual+0x0C, event+8, payload bit6.

    Source 0x4A7210 starts current_date+1 THROUGH inclusive upper
    original date and traverses only original 0x947AD8 buckets.
    Unlike execution pass, its virtual+0x0C must be NONZERO, its
    event+8 zero, and payload bit6 CLEAR. No bit0 test. This can
    differ from actual executed ticks and is not a result count.
    Returned total is original 0x4A84EA + already PResults+0x64.
    """
    current=original_current_date_global_9847fc
    upper=original_inclusive_upper_date
    processed=original_already_processed_64
    if (any(type(x) is not int or not 0<=x<=SOURCE_PRESULTS_NATIVE_SIGNED_MAX
            for x in (current,upper,processed)) or
            type(original_947ad8_date_buckets) is not tuple):
        raise OriginalPResultsEventSourceError("native signed date and count with source tuple required")
    if upper<=current:
        if original_947ad8_date_buckets:
            raise OriginalPResultsEventSourceError(
                "native 4A7210 skipped date traversal, no date buckets reached")
        return processed
    if len(original_947ad8_date_buckets)!=upper-current:
        raise OriginalPResultsEventSourceError(
            "complete source day buckets required, including empty dates")
    total=processed
    for index,bucket in enumerate(original_947ad8_date_buckets):
        if type(bucket) is not OriginalPResultsNativeDateBucket or bucket.original_date_index!=current+index+1:
            raise OriginalPResultsEventSourceError(
                "native dated 0x947AD8 original sequential buckets required")
        for e in bucket.original_linked_nodes:
            if (e.source_virtual_0c_nonzero and e.reached_event8==0 and
                not e.reached_payload44 & SOURCE_PRESULTS_FILTER_BIT):
                total+=1
                if total>SOURCE_PRESULTS_NATIVE_SIGNED_MAX:
                    raise OriginalPResultsEventSourceError(
                        "signed native progress pre-count overflow not qualified")
    return total


def source_original_presults_human_event_616990(
    *, original_human_count_global_8755e4: int,
    original_manager_club_pointers_by_413b10_index: tuple[int, ...],
    original_event_first_club_pointer: int | None,
    original_event_second_club_pointer: int | None,
) -> bool:
    """0x616990 pointer identity is the same reached native loop as 0x510C30.

    The original source loops all original human DBRUser +0x5B4 CLUB
    POINTERS and compares first/second event virtual+0 club pointers.
    This differs from country predicate 0x510C90 and must not be
    replaced with numerical source club IDs or a current-manager test.
    Native first hit skips later original getter calls.
    """
    from original_fastview_native_event_human_owners import (
        source_fastview_original_human_event_510c30,
    )
    return source_fastview_original_human_event_510c30(
        original_human_count_global_8755e4=original_human_count_global_8755e4,
        original_manager_club_pointers_by_413b10_index=(
            original_manager_club_pointers_by_413b10_index),
        original_event_first_club_pointer=original_event_first_club_pointer,
        original_event_second_club_pointer=original_event_second_club_pointer,
    ).original_callback_510c30_nonzero


def source_original_presults_country_event_510c90(
    *, original_event_first_club_record: bytes,
    original_event_second_club_record: bytes | None,
    original_533830_country_indexes_germany_france_england: tuple[int, int, int],
) -> bool:
    """Original 0x510C90 first-club 0x4037C0 then conditional second club.

    Source 0x510C93 reads first club virtual+0 and calls 0x4037C0.
    Nonzero immediately returns true: the second accessor is NOT
    called. Zero reads event+0x28 club virtual+0 and tests 0x4037C0.
    The predicates require the authentic actual club records and
    authenticated 0x533830 country registry indexes. No inference
    from currently selected league/team name is permitted.
    """
    from original_fastview_native_player_roster_stage import (
        source_fastview_original_country_header_5337c0,
    )
    first=source_fastview_original_country_header_5337c0(
        original_club_record=original_event_first_club_record,
        original_533830_country_indexes_germany_france_england=(
            original_533830_country_indexes_germany_france_england))
    if first:
        if original_event_second_club_record is not None:
            raise OriginalPResultsEventSourceError(
                "source first-country callback succeeded; second club never dereferenced")
        return True
    if original_event_second_club_record is None:
        raise OriginalPResultsEventSourceError(
            "original second club must be source-qualified after first country false")
    return source_fastview_original_country_header_5337c0(
        original_club_record=original_event_second_club_record,
        original_533830_country_indexes_germany_france_england=(
            original_533830_country_indexes_germany_france_england))


def source_original_presults_immutable_tick_receipts_4a71f0(
    *, source_6168c0_event_receipt: OriginalPResultsDatedEventReceipt,
    original_before_processed_64: int,
    original_live_denominator_68: int,
):
    """Bridge genuine source callback intents to existing GUI progress DTOs.

    Original 0x4A71F0 increments owner+0x64 once AFTER each genuine
    0x6168C0 event vtable+0x10 callback and repaints via 0x4A7190.
    The caller MUST supply actual 0x4A7210/0x4A84EA-derived current
    denominator separately; unlike generic match results, a source
    callback receipt does not imply that denominator is the count of
    match events, or that it is immutable across future dates.
    Returns one immutable OriginalResultsProgress per actual callback,
    with no queue/UI publication or wall-clock timer effects.
    """
    from human_gameplay import OriginalResultsProgress
    if (type(source_6168c0_event_receipt) is not OriginalPResultsDatedEventReceipt
        or type(original_before_processed_64) is not int
        or type(original_live_denominator_68) is not int
        or not 0<=original_before_processed_64<=SOURCE_PRESULTS_NATIVE_SIGNED_MAX
        or not 0<=original_live_denominator_68<=SOURCE_PRESULTS_NATIVE_SIGNED_MAX
        or original_before_processed_64+
            source_6168c0_event_receipt.source_progress_tick_count
            >SOURCE_PRESULTS_NATIVE_SIGNED_MAX):
        raise OriginalPResultsEventSourceError(
            "authentic source event pass receipt and nonoverflown PResults counters required")
    return tuple(
        OriginalResultsProgress(original_before_processed_64+ordinal,
                                original_live_denominator_68)
        for ordinal,_ in enumerate(
            source_6168c0_event_receipt.original_progress_callbacks,1))
