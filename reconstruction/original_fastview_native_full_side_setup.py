"""Source-bounded original FastView 0x533270 first two-side setup loop.

The original 0x533270 invokes 0x533370 (source roster, header, option),
0x6C1D00 (1556-byte copy), 0x533B20/0x533B70 (packed tactical
producer), and 0x6C1D30 (280-byte setup) for EACH side before any
subsequent events or modal. This immutable projection does not execute
the original game, resolve original native pointers, commit player state,
run the 0x631270+ later setup, or authorize a live match host route.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from

from original_fastview_native_player_roster_stage import (
    SourceFastViewNativePlayerRowInput,
    SourceFastViewNativePlayerRosterError,
    source_fastview_native_side_roster_stage_533370,
    source_fastview_original_native_header_titles_533480,
    source_fastview_original_controlled_club_label_403600,
    source_fastview_original_human_club_4037b0,
    source_fastview_original_formation_owner_413b40,
    source_fastview_native_formation_groups_533480,
    source_fastview_original_country_header_5337c0,
    source_fastview_native_side_header_direct_fields_533480,
    source_fastview_original_side_option_533ab0,
)
from original_fastview_two_sided_live_writeback import (
    SourceFastViewTwoSideNativeTacticalScratch,
    source_fastview_native_raw_tactical_280_from_packed_533b70,
    source_fastview_native_two_side_setup_533270,
)

SOURCE_FASTVIEW_FULL_FIRST_LOOP_VA = 0x533270
SOURCE_FASTVIEW_MATCH_NATIVE_SIDE_COUNT_OFFSETS = (0x5A4, 0xB54)


@dataclass(frozen=True)
class SourceFastViewOriginalNativeSideOwner:
    """Unresolved original pointer targets supplied by independently verified source.

    This object does not discover or infer a DBRClub/DBRPlayer identity.
    Original stack scratch is not assumed zero-initialized. Every field
    must correspond to the *same* original game match, player ordering,
    side-specific club, original global user list and original title.
    """
    original_stack_1556: bytes
    original_players_in_match_pointer_order: tuple[SourceFastViewNativePlayerRowInput, ...]
    original_club_record: bytes
    original_user_42c6d0_title_nul: bytes | None
    original_club_0c_title_nul: bytes
    original_40da90_temporary_title_nul: bytes
    original_formation_groups_from_403850: tuple[tuple[int, ...], ...] | None
    original_raw_tactical_stack_280: bytes
    original_packed_side_from_533b20: bytes
    original_62ac80_virtual30_result: int | None = None
    original_62ac80_signed_word20: int | None = None
    original_computed_registry_pointer_nonzero: bool | None = None
    original_registry_slot_bytes: bytes | None = None


def source_fastview_original_first_two_side_init_533270(
    *, original_match_object: bytes,
    source_side0: SourceFastViewOriginalNativeSideOwner,
    source_side1: SourceFastViewOriginalNativeSideOwner,
    original_human_registry_club_ids_in_link_order: tuple[int, ...],
    original_country_name_indexes_germany_france_england: tuple[int, int, int],
) -> SourceFastViewTwoSideNativeTacticalScratch:
    """Atomic immutable original *first-loop* 0x533270 stage, both teams.

    Precisely composes the original source-bounded 533370 row/header/option
    writes with 533b20/533b70 packed tactical source and 6c1d00/6c1d30
    global destination copies. The remaining 0x533270 stages
    (0x631270, 0x631290, 0x6CC890, 24 initializations and post-modal
    0x533CA0) have not been reproduced and cannot be bypassed.
    """
    if type(original_match_object) is not bytes or len(original_match_object) < 0xB58:
        raise SourceFastViewNativePlayerRosterError(
            "authentic original match object through side1 count required")
    if (type(source_side0) is not SourceFastViewOriginalNativeSideOwner or
        type(source_side1) is not SourceFastViewOriginalNativeSideOwner):
        raise SourceFastViewNativePlayerRosterError(
            "two independent verified native side owners required")
    full_sides = []
    raw_tactics = []
    for side_index, original in enumerate((source_side0, source_side1)):
        club = original.original_club_record
        if type(club) is not bytes or len(club) < 0xDA:
            raise SourceFastViewNativePlayerRosterError(
                "source DBRClub record through +0xD9 required")
        club_reference = unpack_from("<I", club, 4)[0]
        human_ordinal = source_fastview_original_human_club_4037b0(
            original_club_reference_dword=club_reference,
            original_human_registry_club_ids_in_link_order=(
                original_human_registry_club_ids_in_link_order))
        is_human = human_ordinal is not None
        formation_ordinal = source_fastview_original_formation_owner_413b40(
            original_club_reference_dword=club_reference,
            original_human_registry_club_ids_in_link_order=(
                original_human_registry_club_ids_in_link_order))
        if is_human and formation_ordinal is None:
            raise SourceFastViewNativePlayerRosterError(
                "source 403850 original human formation owner unresolved")
        if not is_human and original.original_formation_groups_from_403850 is not None:
            raise SourceFastViewNativePlayerRosterError(
                "nonhuman source cannot provide unvisited formation groups")

        primary_title = source_fastview_original_controlled_club_label_403600(
            original_4037b0_is_human=is_human,
            original_42c6d0_user_text_nul=original.original_user_42c6d0_title_nul,
            original_club_fallback_name_nul=original.original_club_0c_title_nul)
        option = source_fastview_original_side_option_533ab0(
            original_club_word18=unpack_from("<H", club, 0x18)[0],
            original_62ac80_virtual30_result=original.original_62ac80_virtual30_result,
            original_62ac80_signed_word20=original.original_62ac80_signed_word20,
            original_computed_registry_pointer_nonzero=(
                original.original_computed_registry_pointer_nonzero),
            original_registry_slot_bytes=original.original_registry_slot_bytes)
        row_stage = source_fastview_native_side_roster_stage_533370(
            original_side_after_533480_header=original.original_stack_1556,
            original_match_object=original_match_object,
            original_side_index=side_index,
            original_ordered_player_rows=original.original_players_in_match_pointer_order,
            original_533ab0_result=option)
        named = source_fastview_original_native_header_titles_533480(
            original_staged_side_1556=row_stage,
            original_club_record=club,
            source_40da70_resolved_nul_title=primary_title,
            source_40da90_resolved_nul_title=(
                original.original_40da90_temporary_title_nul),
            source_4037b0_human_controlled=is_human)
        with_groups = source_fastview_native_formation_groups_533480(
            original_staged_side_1556=named,
            original_4037b0_has_formation=is_human,
            source_formation_player_id_groups=(
                original.original_formation_groups_from_403850))
        is_country = source_fastview_original_country_header_5337c0(
            original_club_record=club,
            original_533830_country_indexes_germany_france_england=(
                original_country_name_indexes_germany_france_england))
        header = source_fastview_native_side_header_direct_fields_533480(
            original_staged_side_1556=with_groups,
            original_club_record=club,
            original_5337c0_result=is_country)
        full_sides.append(header)
        count = unpack_from("<I", original_match_object,
                            SOURCE_FASTVIEW_MATCH_NATIVE_SIDE_COUNT_OFFSETS[side_index])[0]
        raw_tactics.append(source_fastview_native_raw_tactical_280_from_packed_533b70(
            original_raw_stack_280=original.original_raw_tactical_stack_280,
            original_packed_side=original.original_packed_side_from_533b20,
            native_player_count=count))
    # No values escape before BOTH sides pass all original source predicates.
    return source_fastview_native_two_side_setup_533270(
        native_full_side0_1556=full_sides[0],
        native_full_side1_1556=full_sides[1],
        native_raw_tactics_side0_280=raw_tactics[0],
        native_raw_tactics_side1_280=raw_tactics[1])
