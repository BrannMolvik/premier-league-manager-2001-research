"""FM2001 native LeagueMatch v+0x3C first world-processing bit write.

All seven shipped LeagueMatch virtual+0x3C owners use common 0x511370:
- two route directly to 0x511370;
- one 0x5132E0 invokes 0x511370 before downstream source callbacks;
- four 0x5136E0 invoke 0x511370 before downstream source callbacks.
Common original 0x511370 begins OR DWORD match+0x44 with bit0.

The subsequent original paths involve 0x5112E0 native competition virtual,
side getters 0x50EA40, dynamic 0x5127A0 scheduling, 0x512710,
0x512230 and owner writes; NONE are executed here. This does not mark a
completed original match, event, or game-world writeback.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import pack_into, unpack_from

from original_leaguematch_native_process_owners import (
    OriginalLeagueMatchProcessOwnerError,
    source_original_leaguematch_process_owners_for_native_record,
)

SOURCE_NATIVE_LEAGUEMATCH_V3C_OUTER_DISPATCH_VA = 0x5132A9
SOURCE_NATIVE_LEAGUEMATCH_V3C_COMMON_VA = 0x511370
SOURCE_NATIVE_LEAGUEMATCH_V3C_ORDINARY_WRAPPER_VA = 0x5132E0
SOURCE_NATIVE_LEAGUEMATCH_V3C_SPECIAL_WRAPPER_VA = 0x5136E0
SOURCE_NATIVE_LEAGUEMATCH_V3C_WRAPPER_COMMON_CALL_VAS = (
    0x5132EB,0x513703,
)
SOURCE_NATIVE_LEAGUEMATCH_V3C_STARTED_BIT = 0x1
SOURCE_NATIVE_LEAGUEMATCH_EVENT_FLAGS_OFFSET = 0x44
SOURCE_NATIVE_LEAGUEMATCH_V3C_RESCHEDULE_VA = 0x5127A0


@dataclass(frozen=True)
class SourceOriginalV3CEntryFlagWrite:
    original_vtable_va: int
    native_virtual3c_owner_va: int
    native_common_511370_called: bool
    match_record_after_first_bit0_store: bytes
    original_events_and_world_callbacks_outstanding: bool = True


def source_original_v3c_entry_bit0_write_511370(
    *, original_native_match_record_at_v3c_entry: bytes,
) -> SourceOriginalV3CEntryFlagWrite:
    """Project ONLY first original 0x511381 OR DWORD [match+0x44],1.

    The caller MUST provide actual raw source record AT virtual+0x3C
    entry, after all native +0x38 methods (including 0x513570 for
    wrapped owners). Symbolic modern score, node kind or user team is
    NOT the original's match bytes. Source contract expects at least
    DWORD+0x44; no native world callbacks are simulated.
    """
    record=original_native_match_record_at_v3c_entry
    if type(record) is not bytes or len(record)<0x48:
        raise OriginalLeagueMatchProcessOwnerError(
            "actual original native match record at v3C through flags+0x44 required"
        )
    owners=source_original_leaguematch_process_owners_for_native_record(
        original_match_record=record)
    if owners.virtual3c_cleanup_va not in (
        SOURCE_NATIVE_LEAGUEMATCH_V3C_COMMON_VA,
        SOURCE_NATIVE_LEAGUEMATCH_V3C_ORDINARY_WRAPPER_VA,
        SOURCE_NATIVE_LEAGUEMATCH_V3C_SPECIAL_WRAPPER_VA,
    ):
        raise OriginalLeagueMatchProcessOwnerError(
            "source native LeagueMatch virtual3C common-first owner unsupported"
        )
    updated=bytearray(record)
    flags=unpack_from("<I",updated,SOURCE_NATIVE_LEAGUEMATCH_EVENT_FLAGS_OFFSET)[0]
    pack_into("<I",updated,SOURCE_NATIVE_LEAGUEMATCH_EVENT_FLAGS_OFFSET,
              flags|SOURCE_NATIVE_LEAGUEMATCH_V3C_STARTED_BIT)
    return SourceOriginalV3CEntryFlagWrite(
        original_vtable_va=owners.source_vtable_va,
        native_virtual3c_owner_va=owners.virtual3c_cleanup_va,
        native_common_511370_called=True,
        match_record_after_first_bit0_store=bytes(updated),
    )
