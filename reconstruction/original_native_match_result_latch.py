"""Authenticated original 0x51329D LeagueMatch v+0x38 score latch.

Original common 0x5112A0 reads WORD context+0xD4C and +0xD50 and
writes respectively WORD LeagueMatch+0x3C and +0x3E. Four specific
LeagueMatch classes use 0x5136C0 which calls 0x5112A0 FIRST and
then 0x513570. This models only the two exact word stores and marks
unexecuted remainder, not original match, status, human career,
report, event mutation, or 0x5132A9 virtual+0x3C callback.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from, pack_into

from original_leaguematch_native_process_owners import (
    OriginalLeagueMatchProcessOwnerError,
    source_original_leaguematch_process_owners_for_native_record,
)

SOURCE_ORIGINAL_MATCH_V38_POST_VA = 0x51329D
SOURCE_ORIGINAL_MATCH_V38_WORD_COPY_VA = 0x5112A0
SOURCE_ORIGINAL_MATCH_V38_WRAPPED_VA = 0x5136C0
SOURCE_ORIGINAL_MATCH_V38_WRAPPED_EXTRA_VA = 0x513570
SOURCE_ORIGINAL_MATCH_V3C_POST_VA = 0x5132A9

SOURCE_ORIGINAL_MATCH_FIRST_SCORE_WORD_OFFSET = 0x3C
SOURCE_ORIGINAL_MATCH_SECOND_SCORE_WORD_OFFSET = 0x3E
SOURCE_ORIGINAL_CONTEXT_FIRST_SCORE_WORD_OFFSET = 0xD4C
SOURCE_ORIGINAL_CONTEXT_SECOND_SCORE_WORD_OFFSET = 0xD50


@dataclass(frozen=True)
class OriginalNativeMatchV38ScoreLatchReceipt:
    original_native_match_vtable: int
    original_v38_function: int
    updated_match_record_after_two_word_stores: bytes
    first_score_word: int
    second_score_word: int
    original_wrapped_513570_required: bool
    original_later_v3c_callback_required: bool = True


def source_original_native_match_v38_two_score_words_5112a0(
    *, original_native_match_record_before_v38: bytes,
    original_processing_context_after_match: bytes,
) -> OriginalNativeMatchV38ScoreLatchReceipt:
    """Project exactly native 0x5112A0 writes in 0x51329D v38 callback.

    This accepts a proven original LeagueMatch vtable (not a prototype
    node kind), a genuine pre-callback original native object through +0x3F,
    and a source-qualified original processing context through +0xD51.
    Unrecovered 0x513570 (wrapped v38) and all virtual+0x3C effects
    MUST be executed before declaring an original match completed.
    """
    record=original_native_match_record_before_v38
    context=original_processing_context_after_match
    if type(record) is not bytes or len(record)<0x40:
        raise OriginalLeagueMatchProcessOwnerError(
            "original native LeagueMatch record through +0x3F required"
        )
    if type(context) is not bytes or len(context)<0xD52:
        raise OriginalLeagueMatchProcessOwnerError(
            "original reached match-processing context through +0xD51 required"
        )
    owners=source_original_leaguematch_process_owners_for_native_record(
        original_match_record=record)
    if owners.virtual38_cleanup_va not in (
        SOURCE_ORIGINAL_MATCH_V38_WORD_COPY_VA,
        SOURCE_ORIGINAL_MATCH_V38_WRAPPED_VA,
    ):
        raise OriginalLeagueMatchProcessOwnerError(
            "original v38 method is not a proven score-copy owner"
        )
    first=unpack_from("<H",context,SOURCE_ORIGINAL_CONTEXT_FIRST_SCORE_WORD_OFFSET)[0]
    second=unpack_from("<H",context,SOURCE_ORIGINAL_CONTEXT_SECOND_SCORE_WORD_OFFSET)[0]
    updated=bytearray(record)
    pack_into("<HH",updated,SOURCE_ORIGINAL_MATCH_FIRST_SCORE_WORD_OFFSET,
              first,second)
    return OriginalNativeMatchV38ScoreLatchReceipt(
        original_native_match_vtable=owners.source_vtable_va,
        original_v38_function=owners.virtual38_cleanup_va,
        updated_match_record_after_two_word_stores=bytes(updated),
        first_score_word=first,
        second_score_word=second,
        original_wrapped_513570_required=(
            owners.virtual38_cleanup_va==SOURCE_ORIGINAL_MATCH_V38_WRAPPED_VA
        ),
    )
