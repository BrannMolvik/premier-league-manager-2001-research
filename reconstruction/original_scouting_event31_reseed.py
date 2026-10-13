"""PScouting2K native event31 -> optional double XOR CRT reseed callsites.

Source: private SHA-pinned original footballmanager.exe (not executed).
Actual native 0x47BB30 window vft 0x7C2E6C, +0x10 -> 0x4ADB50:
event+0x20 ID31 -> table 0x4AE168[30] ->0x4AE0FB
->0x4AE970. This stage ALWAYS calls 0x4AF7F0 at 0x4AEA48,
which reseeds CRT at 0x4AF876. After selecting manager user,
if native manager list +0x14 pointer is null, 0x4AEAA6 calls
0x4AEAE0 -> another 0x4AF7F0 at 0x4AED01.

No original PScouting2K event receipt, actual XOR seed,
list membership, shuffle size, or full callback CRT effects are
inferred or executed by this read-only source-branch projection.
"""
from __future__ import annotations
from dataclasses import dataclass

SOURCE_EVENT_ID = 31
SOURCE_WINDOW_VTABLE = 0x7C2E6C
SOURCE_WINDOW_RTTI = '.?AVPScouting2K@@'
SOURCE_WINDOW_EVENT_DISPATCH = 0x4ADB50
FIRST_RESEED_CALLER = 0x4AEA48
SECOND_RESEED_CALLER = 0x4AED01

class OriginalManagerEvent31Error(ValueError):
    pass

@dataclass(frozen=True)
class OriginalManagerEvent31SourcePath:
    native_event_id: int
    original_vtable: int
    native_first_reseed_callsite: int
    native_second_reseed_callsite: int | None
    source_window_rtti: str = SOURCE_WINDOW_RTTI
    original_qualifying_window_event_observed: bool = False
    actual_shared_crt_seed_verified: bool = False


def project_original_manager_event31_reseed_path(
    *,
    native_event_id: int,
    native_window_vtable: int,
    source_manager_list_pointer_is_null: bool,
) -> OriginalManagerEvent31SourcePath:
    """Exact accepted event31 branch *if actually dispatched*.

    The source first 0x4AF7F0 call is unconditional once this handler
    reaches event31; the second requires manager user field+0x14 null.
    Each is an XOR state-derived srand call, not a proven new-game call.
    This is a scouting-screen branch, not a proven TeamSelect startup event.
    Neither seed inputs nor number of shuffle draws are reconstructed.
    """
    if type(native_event_id) is not int or native_event_id != SOURCE_EVENT_ID:
        raise OriginalManagerEvent31Error("Require exact source event31")
    if type(native_window_vtable) is not int or native_window_vtable != SOURCE_WINDOW_VTABLE:
        raise OriginalManagerEvent31Error("Require actual original PScouting2K event vtable")
    if type(source_manager_list_pointer_is_null) is not bool:
        raise OriginalManagerEvent31Error("Require observed original list-pointer state")
    return OriginalManagerEvent31SourcePath(
        native_event_id, native_window_vtable, FIRST_RESEED_CALLER,
        SECOND_RESEED_CALLER if source_manager_list_pointer_is_null else None,
    )
