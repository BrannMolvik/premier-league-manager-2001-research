"""Source-closed chant record shuffle and pool routing.

After bank-prefix classification, the canonical loader repeatedly chooses one
remaining matched record by RNG modulo the current list count, removes that
record, and appends it to the pool identified by record type:
0=home, 1=away, 2=generic.

This module models only that without-replacement ordering. It does not generate
the original RNG sequence or assign chant/event/playback semantics.
"""
from __future__ import annotations

from dataclasses import dataclass

from gate14_chant_bank_selection import (
    AWAY_POOL_TYPE,
    GENERIC_POOL_TYPE,
    HOME_POOL_TYPE,
)


class Gate14ChantPoolOrderError(ValueError):
    pass


SOURCE_LIST_COUNT_VA = 0x723142
RNG_DRAW_VA = 0x723157
REMOVE_BY_INDEX_VA = 0x6B2810
POOL_ROUTE_SWITCH_VA = 0x723171
POOL_APPEND_VA = 0x6B1F90

HOME_POOL_GLOBAL_VA = 0xA87984
AWAY_POOL_GLOBAL_VA = 0xA879A0
GENERIC_POOL_GLOBAL_VA = 0xA87968
GENERIC_POOL_COUNT_GLOBAL_VA = 0xA878DC


@dataclass(frozen=True)
class ChantMatchedRecord:
    basename: str
    pool_type: int

    def __post_init__(self) -> None:
        if not isinstance(self.basename, str) or not self.basename:
            raise Gate14ChantPoolOrderError("chant record basename must be non-empty")
        if self.pool_type not in (HOME_POOL_TYPE, AWAY_POOL_TYPE, GENERIC_POOL_TYPE):
            raise Gate14ChantPoolOrderError("chant record pool type must be 0, 1, or 2")


@dataclass(frozen=True)
class ChantPoolOrder:
    home: tuple[ChantMatchedRecord, ...]
    away: tuple[ChantMatchedRecord, ...]
    generic: tuple[ChantMatchedRecord, ...]
    source_record_count: int
    random_without_replacement_recovered: bool = True
    event_binding_recovered: bool = False
    playback_timing_recovered: bool = False

    def __post_init__(self) -> None:
        if type(self.source_record_count) is not int or self.source_record_count < 0:
            raise Gate14ChantPoolOrderError("source record count must be non-negative")
        if (
            len(self.home) + len(self.away) + len(self.generic)
            != self.source_record_count
        ):
            raise Gate14ChantPoolOrderError(
                "chant pools must account for every matched source record exactly once"
            )
        if not self.random_without_replacement_recovered:
            raise Gate14ChantPoolOrderError(
                "pool order contract cannot weaken recovered shuffle behavior"
            )
        if self.event_binding_recovered or self.playback_timing_recovered:
            raise Gate14ChantPoolOrderError(
                "pool ordering cannot promote event/timing semantics"
            )


def route_chant_records_by_source_shuffle(
    records: tuple[ChantMatchedRecord, ...],
    selection_indices: tuple[int, ...],
) -> ChantPoolOrder:
    """Apply the exact remove-by-index routing performed at 0x723157.

    selection_indices are the already-reduced RNG remainders. At each step the
    value must be a valid index into the current remaining list. The selected
    record is removed, then appended to its type-specific pool.
    """
    if type(records) is not tuple or any(
        type(item) is not ChantMatchedRecord for item in records
    ):
        raise Gate14ChantPoolOrderError(
            "records must be a tuple of exact ChantMatchedRecord objects"
        )
    if type(selection_indices) is not tuple or any(
        type(value) is not int for value in selection_indices
    ):
        raise Gate14ChantPoolOrderError("selection indices must be an integer tuple")
    if len(selection_indices) != len(records):
        raise Gate14ChantPoolOrderError(
            "source shuffle requires exactly one selection index per record"
        )

    remaining = list(records)
    home: list[ChantMatchedRecord] = []
    away: list[ChantMatchedRecord] = []
    generic: list[ChantMatchedRecord] = []

    for index in selection_indices:
        if not 0 <= index < len(remaining):
            raise Gate14ChantPoolOrderError(
                "selection index must address the current remaining record list"
            )
        record = remaining.pop(index)
        if record.pool_type == HOME_POOL_TYPE:
            home.append(record)
        elif record.pool_type == AWAY_POOL_TYPE:
            away.append(record)
        else:
            generic.append(record)

    return ChantPoolOrder(
        home=tuple(home),
        away=tuple(away),
        generic=tuple(generic),
        source_record_count=len(records),
    )
