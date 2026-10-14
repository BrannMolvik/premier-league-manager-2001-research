"""Cross-qualify original 0x5127A0 both-side callback order and native players.

Original source 0x5127AF/+5127F7 resolves the two team pointers from the
same processing-owner record. Roster callback 0x875644 virtual receives
unsigned player ID; active row pointers are already-resolved native players.
This is a necessary identity / ordering proof, not native callback execution,
source-world mutation, calendar advancement, or PResults acceptance.

Original private footballmanager.exe SHA256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from

from original_native_5127a0_order_guard import (
    Original5127A0OrderedSide, Original5127A0OrderReceipt,
    source_original_5127a0_two_owner_order_from_reached,
)
from original_native_5127a0_player_identity import (
    Original5127A0ReachedPlayer, Original5127A0PlayerOwnerReceipt,
    source_original_5127a0_player_pointer_identity,
)


class Original5127A0CombinedSourceError(ValueError):
    pass


@dataclass(frozen=True)
class Original5127A0CombinedOwnerReceipt:
    first_side: Original5127A0PlayerOwnerReceipt
    second_side: Original5127A0PlayerOwnerReceipt
    order: Original5127A0OrderReceipt
    original_first_team_pointer: int
    original_second_team_pointer: int
    original_row_native_ids: tuple[tuple[int, ...], tuple[int, ...]]
    source_native_callbacks_executed: bool = False
    live_game_state_updated: bool = False
    finished_match_journey: bool = False


def source_original_5127a0_qualified_two_owner_identity(
    *,
    original_processing_owner_record: bytes,
    original_sides: tuple[Original5127A0OrderedSide,Original5127A0OrderedSide],
    original_reached_roster_players: tuple[
        tuple[Original5127A0ReachedPlayer,...],
        tuple[Original5127A0ReachedPlayer,...],
    ],
) -> Original5127A0CombinedOwnerReceipt:
    """Prove source team ownership, roster/row identity and callback ordering.

    Unlike isolated partial source projections, requires one shared actual
    processing-owner snapshot, two source-ordered EBX owner phases, and each
    side's *separately reached* per-roster player pointer/DBRPlayer+4 pair.
    The original virtual getter effects and player post-callback states are
    still unqualified; this is not a commit authorization for live NEXT.
    """
    owner=original_processing_owner_record
    if type(owner) is not bytes or len(owner)<0x5b4:
        raise Original5127A0CombinedSourceError(
            "original processing owner record through +5B0 required")
    first=unpack_from("<I",owner,0)[0]
    second=unpack_from("<I",owner,0x5b0)[0]
    if not first or not second or first==second:
        raise Original5127A0CombinedSourceError(
            "two distinct original team owner pointers required")
    if (type(original_sides) is not tuple or len(original_sides)!=2 or
        type(original_reached_roster_players) is not tuple or
        len(original_reached_roster_players)!=2):
        raise Original5127A0CombinedSourceError(
            "both source owner passes and roster records required")
    # Before reading any native source row, prove original caller phase order.
    ordered=source_original_5127a0_two_owner_order_from_reached(original_sides)
    maps=[]
    seen_pointers=set()
    seen_ids=set()
    for index,(side,roster) in enumerate(zip(original_sides,original_reached_roster_players)):
        if type(roster) is not tuple:
            raise Original5127A0CombinedSourceError(
                "source native reached roster must be a tuple")
        mapped=source_original_5127a0_player_pointer_identity(
            source_side=side,original_reached_players=roster)
        current,opponent=(first,second) if index==0 else (second,first)
        for row in side.source_rows:
            if (row.source_current_team_pointer!=current or
                row.source_opponent_team_pointer!=opponent or
                row.source_4197c0_arg3!=opponent):
                raise Original5127A0CombinedSourceError(
                    "original active row team / opposing team pointer mismatch")
        for p,pid in zip(mapped.native_roster_pointers,mapped.native_roster_ids):
            if p in seen_pointers or pid in seen_ids:
                raise Original5127A0CombinedSourceError(
                    "duplicate native player ID/pointer across opposing teams")
            seen_pointers.add(p)
            seen_ids.add(pid)
        if len(set(mapped.native_row_pointers))!=len(mapped.native_row_pointers):
            raise Original5127A0CombinedSourceError(
                "native active player pointer appears twice in one side's rows")
        maps.append(mapped)
    return Original5127A0CombinedOwnerReceipt(
        first_side=maps[0],second_side=maps[1],order=ordered,
        original_first_team_pointer=first,
        original_second_team_pointer=second,
        original_row_native_ids=(maps[0].native_row_ids,maps[1].native_row_ids),
    )
