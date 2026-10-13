"""Original ScheduleEvent 0x510380 authenticated two-container identity.

Owner-private original footballmanager.exe SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3
was statically inspected, never executed/distributed. Exact source
0x510380 derives event+0x0C from original container DWORD+0x0C
serial and whether the source collection pointer equals 0x947AF0.
Native constructor initializes event+8 and +0x10, but this helper
does not infer anything about a subsequently LOADED event record.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import pack_into

SOURCE_ORIGINAL_SCHEDULE_EVENT_CTOR_VA = 0x510380
SOURCE_ORIGINAL_EVENT_FIRST_COLLECTION_VA = 0x947AD8
SOURCE_ORIGINAL_EVENT_SECOND_COLLECTION_VA = 0x947AF0
SOURCE_ORIGINAL_EVENT_BASE_VTABLE_VA = 0x7C4D70
SOURCE_ORIGINAL_EVENT_SERIAL_OFFSET = 0x0C
SOURCE_ORIGINAL_EVENT_NEXT_POINTER_OFFSET = 0x08


class OriginalScheduleEventConstructorSourceError(ValueError):
    """Authentic native event/container input required."""


@dataclass(frozen=True)
class OriginalScheduleEventConstructorValue:
    source_native_event_record_after_constructor: bytes
    source_collection_counter_after_constructor: int
    source_collection_pointer: int
    source_event_id_dword_0c: int


def source_original_schedule_event_constructor_510380(
    *, original_uninitialized_event_record: bytes,
    original_collection_pointer: int,
    original_collection_serial_counter_before: int,
) -> OriginalScheduleEventConstructorValue:
    """Immutable source-only 0x510380 direct writes, not event execution.

    Native 0x510380 performs:
       selected= (arg collection pointer == 0x947AF0);
       event+8=0; event+0x10=0xFFFFFFFF;
       event+0x0C=(collection+0x0C *2 | selected) modulo DWORD;
       event vtable=0x7C4D70;
       collection+0x0C++ modulo DWORD.
    For an actual original 0x4F3B50-based manager schedule this
    source contract requires authentic 0x947AD8/0x947AF0 identity.
    Child constructor may then install one of seven LeagueMatch
    vtables, but no child association is guessed here.
    """
    if (type(original_uninitialized_event_record) is not bytes or
            len(original_uninitialized_event_record)<0x14):
        raise OriginalScheduleEventConstructorSourceError(
            "original native event scratch through +0x10 required")
    if type(original_collection_pointer) is not int or original_collection_pointer not in (
        SOURCE_ORIGINAL_EVENT_FIRST_COLLECTION_VA,
        SOURCE_ORIGINAL_EVENT_SECOND_COLLECTION_VA,
    ):
        raise OriginalScheduleEventConstructorSourceError(
            "source qualified original dated event collection pointer required")
    if (type(original_collection_serial_counter_before) is not int or
            not 0<=original_collection_serial_counter_before<=0xFFFFFFFF):
        raise OriginalScheduleEventConstructorSourceError(
            "native source collection DWORD serial required")
    ident=(((original_collection_serial_counter_before<<1)&0xFFFFFFFF) |
           int(original_collection_pointer==SOURCE_ORIGINAL_EVENT_SECOND_COLLECTION_VA))
    event=bytearray(original_uninitialized_event_record)
    pack_into("<I",event,0,SOURCE_ORIGINAL_EVENT_BASE_VTABLE_VA)
    pack_into("<I",event,0x08,0)
    pack_into("<I",event,SOURCE_ORIGINAL_EVENT_SERIAL_OFFSET,ident)
    pack_into("<I",event,0x10,0xFFFFFFFF)
    return OriginalScheduleEventConstructorValue(
        bytes(event),(original_collection_serial_counter_before+1)&0xFFFFFFFF,
        original_collection_pointer,ident)
