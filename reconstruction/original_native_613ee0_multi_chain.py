"""Original 0x613EE0 complete pre-callback pending-list scan, source only.

Canonical private footballmanager.exe SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Static source 613EE5..613F30: queue +4 first/+8 last; wrapper +0 event,
+4 next/+8 prev; signed event+4 <= target selects virtual+10, and
remove=1 calls 4EA190 after caching wrapper+4 next. Callbacks may
reenter/append/trigger deferred 614080: this does not execute those callbacks,
mutate a native queue, establish a finished multi-node scan or deliver mail.
It is the bounded source-verified missing multi-event identity/order stage.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from


class Original613EE0MultiChainSourceError(ValueError):
    pass


_ALLOWED_EVENT_VTABLES = (0x7BD564, 0x7D7760)
_ORIGINAL_FLAG1_CURRENT_DAY_CALLERS = (
    0x41A364, 0x41A475, 0x43216C, 0x4A8084, 0x5E3335,
)


def _u32(value: int, label: str, *, nonzero: bool = False) -> int:
    if (type(value) is not int or not 0 <= value <= 0xFFFFFFFF
            or (nonzero and value == 0)):
        raise Original613EE0MultiChainSourceError(
            "Source original " + label + " uint32 required"
        )
    return value


def _signed(value: int) -> int:
    return value - 0x100000000 if value >= 0x80000000 else value


@dataclass(frozen=True)
class Original613EE0LinkedEvent:
    """Independently reached original wrapper and owned native event bytes."""

    wrapper_pointer: int
    wrapper_before: bytes
    event_pointer: int
    event_before: bytes


@dataclass(frozen=True)
class Original613EE0MultiChainReached:
    global_947aa8_header_before: bytes
    ordered_source_nodes: tuple[Original613EE0LinkedEvent, ...]
    raw_current_date_9847fc: int
    native_caller_address: int
    native_remove_flag: int = 1


@dataclass(frozen=True)
class Original613EE0MultiNodeDecision:
    wrapper_pointer: int
    event_pointer: int
    event_vtable: int
    due_raw_day: int
    due_signed_day: int
    source_virtual10_would_be_called: bool
    # Native 613F12 calls 4EA190 only after virtual+10 completed.
    # The actual callback may change the queue, so NOT a completed unlink.
    source_4ea190_would_follow_callback: bool
    original_cached_next_wrapper_pointer: int


@dataclass(frozen=True)
class Original613EE0MultiChainReceipt:
    original_first_wrapper_pointer: int
    original_last_wrapper_pointer: int
    original_target_signed_day: int
    source_decisions_in_native_order: tuple[Original613EE0MultiNodeDecision, ...]
    original_full_input_chain_validated: bool = True
    original_native_callbacks_executed: bool = False
    original_native_global_queue_mutated: bool = False
    original_deferred_614080_drained: bool = False
    original_user_mailbox_retention_executed: bool = False
    live_game_state_updated: bool = False
    original_inbox_rendered: bool = False


def source_original_613ee0_multi_chain_pre_callback(
    reached: Original613EE0MultiChainReached,
) -> Original613EE0MultiChainReceipt:
    """Check whole original ordered chain and plan due dispatch/unlink order.

    This stage is deliberately pre-callback: the original may mutate links
    during 5D7B40 / 5CFA20 or the 614080 reentrant pass. Do not use the
    static source decisions to claim final queue bytes or actual delivery.
    """
    if type(reached) is not Original613EE0MultiChainReached:
        raise Original613EE0MultiChainSourceError(
            "Typed original 613EE0 multi-node input required"
        )
    raw_day = _u32(reached.raw_current_date_9847fc, "calendar day")
    caller = _u32(reached.native_caller_address, "due caller", nonzero=True)
    if caller not in _ORIGINAL_FLAG1_CURRENT_DAY_CALLERS:
        raise Original613EE0MultiChainSourceError(
            "Only five source-confirmed current-day call sites supported"
        )
    if type(reached.native_remove_flag) is not int or reached.native_remove_flag != 1:
        raise Original613EE0MultiChainSourceError(
            "All five source caller sites require remove=1"
        )
    header = reached.global_947aa8_header_before
    if type(header) is not bytes or len(header) < 0x14:
        raise Original613EE0MultiChainSourceError(
            "Native 947AA8 header through +10 required"
        )
    first, last, active, deferred = unpack_from("<IIII", header, 4)
    if active != 0 or deferred != 0:
        raise Original613EE0MultiChainSourceError(
            "Reentrant/active global queue needs independent native proof"
        )
    nodes = reached.ordered_source_nodes
    if type(nodes) is not tuple:
        raise Original613EE0MultiChainSourceError(
            "Native linked wrapper order must be a tuple"
        )
    if not nodes:
        if first != 0 or last != 0:
            raise Original613EE0MultiChainSourceError(
                "Nonempty native chain has no reached wrapper nodes"
            )
        return Original613EE0MultiChainReceipt(0, 0, _signed(raw_day), ())
    if first == 0 or last == 0 or len(nodes) > 10000:
        raise Original613EE0MultiChainSourceError(
            "Source first/tail or bounded linked list invalid"
        )
    expected_pointer = first
    previous = 0
    seen_nodes: set[int] = set()
    seen_events: set[int] = set()
    decisions: list[Original613EE0MultiNodeDecision] = []
    for node in nodes:
        if type(node) is not Original613EE0LinkedEvent:
            raise Original613EE0MultiChainSourceError(
                "Each native queue node requires typed reached evidence"
            )
        ptr = _u32(node.wrapper_pointer, "wrapper pointer", nonzero=True)
        eptr = _u32(node.event_pointer, "event pointer", nonzero=True)
        if (ptr != expected_pointer or ptr in seen_nodes or eptr in seen_events
                or ptr == eptr):
            raise Original613EE0MultiChainSourceError(
                "Native queue order, pointer alias, duplicate or cycle"
            )
        wrapper = node.wrapper_before
        if type(wrapper) is not bytes or len(wrapper) != 12:
            raise Original613EE0MultiChainSourceError(
                "Native 12-byte wrapper record required"
            )
        event_ptr, next_ptr, prev_ptr = unpack_from("<III", wrapper, 0)
        if event_ptr != eptr or prev_ptr != previous:
            raise Original613EE0MultiChainSourceError(
                "Native wrapper event ownership/previous link mismatch"
            )
        event = node.event_before
        if type(event) is not bytes or len(event) < 12:
            raise Original613EE0MultiChainSourceError(
                "Original event vtable/date/payload bytes required"
            )
        vtable, due = unpack_from("<II", event)
        if vtable not in _ALLOWED_EVENT_VTABLES:
            raise Original613EE0MultiChainSourceError(
                "Unqualified original pending event vtable"
            )
        if vtable == 0x7BD564:
            if len(event) != 12 or unpack_from("<I", event, 8)[0] == 0:
                raise Original613EE0MultiChainSourceError(
                    "7BD564 requires an owned pending human notice"
                )
        else:
            if len(event) < 0x14 or unpack_from("<I", event, 12)[0] == 0:
                raise Original613EE0MultiChainSourceError(
                    "7D7760 requires owned source player ID address"
                )
        dispatch_due = _signed(due) <= _signed(raw_day)
        decisions.append(Original613EE0MultiNodeDecision(
            ptr, eptr, vtable, due, _signed(due), dispatch_due,
            dispatch_due, next_ptr,
        ))
        seen_nodes.add(ptr)
        seen_events.add(eptr)
        previous = ptr
        expected_pointer = next_ptr
    if expected_pointer != 0 or previous != last:
        raise Original613EE0MultiChainSourceError(
            "Incomplete native source chain or wrong final tail"
        )
    return Original613EE0MultiChainReceipt(
        first, last, _signed(raw_day), tuple(decisions)
    )
