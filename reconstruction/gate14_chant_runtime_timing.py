"""Source-closed timing arithmetic for the FM2001 chant runtime.

The canonical chant updater at 0x7235E0 drives two state-machine passes.
Private source tracing proves the exact clock arithmetic below but does not yet
assign semantic names to the CHANT.eam record timing fields at +0x18/+0x1C/+0x20.

This module therefore retains those offsets literally and exposes only the
verified deadline calculations. It does not decode CHANT.eam sequencing, map
states to match events, or claim which audible chant a record represents.
"""
from __future__ import annotations

from dataclasses import dataclass


class Gate14ChantRuntimeTimingError(ValueError):
    pass


CHANT_RUNTIME_UPDATE_VA = 0x7235E0
CHANT_PENDING_UPDATE_VA = 0x723600
CHANT_ACTIVE_UPDATE_VA = 0x7236E0
SOURCE_CLOCK_VA = 0x6AAE40

CHANT_READY_GLOBAL_VA = 0xA878D0
PENDING_LIST_GLOBAL_VA = 0xA87910
ACTIVE_LIST_GLOBAL_VA = 0xA8792C
RECYCLE_LIST_GLOBAL_VA = 0xA878F4

STATE_OFFSET = 0x08
GATE_DEADLINE_OFFSET = 0x10
PHASE_DEADLINE_OFFSET = 0x14
TIMING_FIELD_18_OFFSET = 0x18
TIMING_FIELD_1C_OFFSET = 0x1C
TIMING_FIELD_20_OFFSET = 0x20

POLL_GUARD_MS = 0xC8
POOL_COOLDOWN_MS = 0x1770

STATE_PENDING_RESOURCE = 0
STATE_READY = 1
STATE_PLAYING_FIRST_PHASE = 2
STATE_PLAYING_SECOND_PHASE = 3

STATE2_DEADLINE_WRITE_VA = 0x723850
STATE3_DEADLINE_WRITE_VA = 0x7237B1
POLL_GUARD_WRITE_VA = 0x723655
POOL_COOLDOWN_WRITE_VA = 0x723869


def _u32ish(value: int, field: str) -> int:
    if type(value) is not int or value < 0:
        raise Gate14ChantRuntimeTimingError(f"{field} must be a non-negative integer")
    return value


def first_phase_deadline(
    now_ms: int,
    timing_field_18_ms: int,
    timing_field_20_ms: int,
) -> int:
    """Exact 0x72383E-0x723857 arithmetic: now + [+0x20] + [+0x18]."""
    now_ms = _u32ish(now_ms, "now_ms")
    field18 = _u32ish(timing_field_18_ms, "timing_field_18_ms")
    field20 = _u32ish(timing_field_20_ms, "timing_field_20_ms")
    return now_ms + field20 + field18


def second_phase_deadline(now_ms: int, timing_field_1c_ms: int) -> int:
    """Exact 0x7237A9-0x7237BF arithmetic: now + [+0x1C] + 200."""
    now_ms = _u32ish(now_ms, "now_ms")
    field1c = _u32ish(timing_field_1c_ms, "timing_field_1c_ms")
    return now_ms + field1c + POLL_GUARD_MS


def pending_poll_deadline(now_ms: int) -> int:
    """Exact 0x723655-0x72365F retry guard: now + 200."""
    now_ms = _u32ish(now_ms, "now_ms")
    return now_ms + POLL_GUARD_MS


def pool_cooldown_deadline(now_ms: int) -> int:
    """Exact 0x723869-0x72387D pool gate reset: now + 6000."""
    now_ms = _u32ish(now_ms, "now_ms")
    return now_ms + POOL_COOLDOWN_MS


@dataclass(frozen=True)
class ChantRuntimeTimingBoundary:
    poll_guard_ms: int = POLL_GUARD_MS
    pool_cooldown_ms: int = POOL_COOLDOWN_MS
    source_clock_recovered: bool = True
    four_state_lifecycle_recovered: bool = True
    timing_field_semantics_recovered: bool = False
    event_binding_recovered: bool = False
    chant_meaning_recovered: bool = False

    def __post_init__(self) -> None:
        if self.poll_guard_ms != 200:
            raise Gate14ChantRuntimeTimingError("chant poll guard must remain 200 ms")
        if self.pool_cooldown_ms != 6000:
            raise Gate14ChantRuntimeTimingError(
                "chant pool cooldown must remain 6000 ms"
            )
        if not self.source_clock_recovered or not self.four_state_lifecycle_recovered:
            raise Gate14ChantRuntimeTimingError(
                "timing boundary cannot weaken recovered runtime facts"
            )
        if (
            self.timing_field_semantics_recovered
            or self.event_binding_recovered
            or self.chant_meaning_recovered
        ):
            raise Gate14ChantRuntimeTimingError(
                "timing arithmetic cannot promote unrecovered chant semantics"
            )


SOURCE_BOUNDARY = ChantRuntimeTimingBoundary()
