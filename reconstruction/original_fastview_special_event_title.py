"""Source-exact bounded value projection of original 0x51FC37 FastView title.

Authenticated shipped original footballmanager.exe SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Source disassembled STATICALLY only, original executable not launched.

Reached from native 0x51FA70 when a linked event's WORD+0x40
equals 0xFFFF. The original reads first club from event+0x14
virtual +0, follows returned +0x0C to indirect C bytes, appends
native static literal 0x829754 (" v "), reads second club from
event+0x28 virtual +0 via the same indirect string path, appends,
and jumps to 0x5211DE. It does NOT sort/append the ordinary list.
"""
from __future__ import annotations

from dataclasses import dataclass

SOURCE_FASTVIEW_SPECIAL_TITLE_START_VA = 0x51FC37
SOURCE_FASTVIEW_SPECIAL_TITLE_FIRST_CLUB_VA = 0x51FC41
SOURCE_FASTVIEW_SPECIAL_TITLE_LITERAL_VA = 0x829754
SOURCE_FASTVIEW_SPECIAL_TITLE_SECOND_CLUB_VA = 0x51FCA9
SOURCE_FASTVIEW_SPECIAL_TITLE_EARLY_EXIT_VA = 0x5211DE
SOURCE_FASTVIEW_SPECIAL_TITLE_LITERAL_BYTES = b" v "


class OriginalFastViewSpecialTitleError(ValueError):
    """Unproven original event/club indirect text prevents source projection."""


@dataclass(frozen=True)
class OriginalFastViewSpecialTitleReceipt:
    original_resolved_title_nul: bytes
    native_local_flag_2b4_after: int
    native_control_exits_to_5211de: bool


def source_fastview_original_special_event_title_51fc37(
    *, original_candidate_event_record: bytes,
    original_event_first_club_indirect_title_nul: bytes,
    original_event_second_club_indirect_title_nul: bytes,
) -> OriginalFastViewSpecialTitleReceipt:
    """Only reached source-string transformation, not real UI or linked state.

    Original uses repnz SCAS and 0x526AF0 to append exact unnormalized
    bytes. NULs in the input terminate strings. The source uses a
    dynamic temporary object and can fail allocation; no C++ original
    allocation, reference lifetime, UI, or other event flags simulated.
    Caller supplies actual bytes via both ORIGINAL event virtual club
    getters and their +0x0C indirect C strings, not guessed club names.
    """
    if type(original_candidate_event_record) is not bytes or len(original_candidate_event_record)<0x42:
        raise OriginalFastViewSpecialTitleError(
            "actual original event record WORD+0x40 required")
    word=(original_candidate_event_record[0x40] |
          original_candidate_event_record[0x41]<<8)
    if word!=0xFFFF:
        raise OriginalFastViewSpecialTitleError(
            "original special 0x51FC37 branch not reached unless WORD+0x40 is 0xFFFF")
    parts=[]
    for raw in (original_event_first_club_indirect_title_nul,
                original_event_second_club_indirect_title_nul):
        if type(raw) is not bytes or b"\x00" not in raw:
            raise OriginalFastViewSpecialTitleError(
                "both reached source club virtual getters require NUL C strings")
        parts.append(raw.split(b"\x00",1)[0])
    return OriginalFastViewSpecialTitleReceipt(
        original_resolved_title_nul=(
            parts[0]+SOURCE_FASTVIEW_SPECIAL_TITLE_LITERAL_BYTES+parts[1]+b"\x00"),
        native_local_flag_2b4_after=0,
        native_control_exits_to_5211de=True)
