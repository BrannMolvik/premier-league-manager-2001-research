"""Source-only native 5DC510 wrapper+payload layout (not a live event).

5DC5E7–627 copies original by-value args into 0x20 allocated payload.
Offset +0x12..+0x13 is not initialized by this copied constructor.
5DC62B–63A allocates a separate 0x0C intrusive queue wrapper that may
hold a null payload on 0x20 allocation failure. 617D70 links the wrapper.
Neither native allocation, nested 5DC650, original queues nor GameState
are executed by this contract.
"""
from dataclasses import dataclass
from struct import unpack_from


class Original5DC510EventPayloadError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal5DC510EventLayout:
    original_payload_first16: bytes
    original_payload_word10: int
    original_payload_tail14_1c: tuple[int, int, int]
    original_uninitialized_padding_12_13: bool = True
    original_payload_allocated_bytes: int = 0x20
    original_wrapper_allocated_bytes: int = 0x0c
    original_linker_617d70: int = 0x617D70
    original_native_allocations_executed: bool = False
    live_queue_updated: bool = False


def source_original_5dc510_event_payload_layout(
    *, original_5dc510_byvalue_arguments: bytes
) -> SourceOriginal5DC510EventLayout:
    raw=original_5dc510_byvalue_arguments
    if type(raw) is not bytes or len(raw)!=0x24:
        raise Original5DC510EventPayloadError('actual original 5DC510 stack arguments (0x24 bytes) required')
    return SourceOriginal5DC510EventLayout(
        raw[:16],unpack_from('<H',raw,0x10)[0],
        unpack_from('<III',raw,0x14),
    )
