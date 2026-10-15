"""Read-only native 5DB185..5DB280 fourth-stage coefficient and player index.

The native code checks the 410FF0 category via unsigned JA 5, selects a
source QWORD from global 821E00..821E24 (categories 5 and invalid both use
821E20), loads signed per-player +8 of 21-DWORD row rooted at [874C08].
All original callbacks, 5DA250, 42B0E0, 668350, 64D540 and GUI are UNRUN.
"""
from dataclasses import dataclass
from struct import pack, unpack_from


class OriginalStageFourSourceError(ValueError):
    pass


_STAGE4_QWORD_VA = (0x821E00, 0x821E08, 0x821E10, 0x821E18,
                    0x821E20, 0x821E20)
_STAGE4_COEFF = (0.9, 0.8, 0.7, 0.6, 0.5, 0.5)


@dataclass(frozen=True)
class SourceOriginalStageFourCoefficientReceipt:
    native_410ff0_unsigned_category: int
    original_jump_target: int
    original_coefficient_qword_va: int
    original_coefficient_qword: bytes
    original_first_side_club_pointer: int
    original_first_side_player_index: int
    original_global_874c08_base_pointer: int
    original_global_player_signed_dword: int
    original_native_5da250_executed: bool = False
    original_rng_64d540_executed: bool = False
    live_game_state_updated: bool = False


def source_original_stage_four_coefficient_player(
    *, original_reached_stage4_x87_ah: int,
    original_410ff0_category_eax: int,
    original_first_side_club_pointer: int,
    original_first_side_club_before_stage: bytes,
    original_874c08_global_player_table_pointer: int,
    original_global_player_21_dword_records: bytes,
) -> SourceOriginalStageFourCoefficientReceipt:
    """Require independently reached stage-4 native bytes and pointer owners."""
    ah = original_reached_stage4_x87_ah
    cat = original_410ff0_category_eax
    clubptr = original_first_side_club_pointer
    globalptr = original_874c08_global_player_table_pointer
    if type(ah) is not int or not 0 <= ah <= 255 or ah & 0x40:
        raise OriginalStageFourSourceError("stage4 source guard was skipped or missing")
    if type(cat) is not int or not 0 <= cat <= 0xffffffff:
        raise OriginalStageFourSourceError("original 410FF0 native DWORD category required")
    if (type(clubptr) is not int or not 0 < clubptr <= 0xffffffff or
            type(globalptr) is not int or not 0 < globalptr <= 0xffffffff):
        raise OriginalStageFourSourceError("original native first-side/table pointers required")
    club = original_first_side_club_before_stage
    rows = original_global_player_21_dword_records
    if type(club) is not bytes or len(club) < 0x74:
        raise OriginalStageFourSourceError("actual first-side club bytes through +73 required")
    if type(rows) is not bytes or not rows or len(rows) % 84:
        raise OriginalStageFourSourceError("complete source global table 21-DWORD rows required")
    player_index = unpack_from("<I", club, 0x70)[0]
    # Native LEA computes (index * 21) in 32-bit arithmetic. An index that
    # wraps the EDX arithmetic or escapes this received source owner region
    # is unresolved; do not accidentally read a different runtime object.
    if player_index > 0xffffffff // 21 or player_index >= len(rows) // 84:
        raise OriginalStageFourSourceError("native player row unqualified/wrapped")
    per_player = unpack_from("<i", rows, player_index * 84 + 8)[0]
    effective = cat if cat <= 5 else 5
    jumps = (0x5db1cd, 0x5db1da, 0x5db1f0, 0x5db205, 0x5db212, 0x5db228)
    target = jumps[cat] if cat <= 5 else 0x5db23d
    return SourceOriginalStageFourCoefficientReceipt(
        cat, target, _STAGE4_QWORD_VA[effective],
        pack("<d", _STAGE4_COEFF[effective]), clubptr, player_index,
        globalptr, per_player)
