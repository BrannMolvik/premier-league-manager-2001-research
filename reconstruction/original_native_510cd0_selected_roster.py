"""Native original 510CD0 dual roster pointer arrays, bounded 5111A0 tail.

Canonical private original EXE SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Static x86 source analysis, no original execution or in-process pointer deref.
This produces an immutable receipt for just 510CD0 called at 51126C/511287;
it DOES NOT run original 5111A0 4037B0/409B50/405A20 or native context
mutation and is not an ordinary match or saved GameState implementation.
"""
from dataclasses import dataclass
from struct import unpack_from

from original_native_406be0_roster_count import SourceOriginal406BE0Player
from original_native_405a20_sort_roster import SourceOriginal405A20NativeRosterSort
from original_leaguematch_native_process_owners import (
    source_original_leaguematch_process_owners_for_native_record,
)


class Original510CD0SourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal510CD0SelectedRoster:
    original_team_club_key_dword: int
    source_roster_count: int
    source_original_target_context_offset: int
    source_original_count_context_offset: int
    source_selected_player_pointers: tuple[int, ...]
    source_reached_417f50_player_ids: tuple[int,...]
    source_reached_417f60_player_ids: tuple[int,...]
    source_select_bit4_or_bit5_player_ids: tuple[int,...]
    source_selection_count_return_eax: int
    original_510cd0_was_executed: bool = False
    original_context_array_modified: bool = False
    saved_game_state_modified: bool = False


SOURCE_510CD0_SELECTION_ARRAY_SLOTS = {0x4:0x5A4, 0x5B4:0xB54}
SOURCE_510CD0_ARRAY_CAPACITY = 360


def source_original_510cd0_selected_player_pointers(
    *, original_team_record: bytes,
    original_global_875640_player_array_address: int,
    original_ordered_player_records: tuple[SourceOriginal406BE0Player,...],
    original_target_processing_context_offset: int,
) -> SourceOriginal510CD0SelectedRoster:
    """Original 510CD0, WORD player ID->875640 base+ID*0x250.

    417F50 dereferences player+10 signed team owner and player+14 bit4.
    If false, 417F60 uses the same signed owner and bit5 (via 417F00).
    Only one entry per player is appended when either flag qualifies,
    preserving native source roster order. 5111A0 calls this for source
    team0→context+4 (count context+5A4), then side1→context+5B4
    (count context+B54), after other unmodeled mutable callbacks.
    """
    team=original_team_record
    if type(team) is not bytes or len(team)<0x298:
        raise Original510CD0SourceError("original team bytes through +294 required")
    target=original_target_processing_context_offset
    if type(target) is not int or target not in SOURCE_510CD0_SELECTION_ARRAY_SLOTS:
        raise Original510CD0SourceError("source 5111A0 context +4/+5B4 target required")
    base=original_global_875640_player_array_address
    if type(base) is not int or not 0<base<=0xffffffff:
        raise Original510CD0SourceError("source global 875640 player base required")
    original_count=unpack_from("<i",team,0x294)[0]
    key=unpack_from("<I",team,0x04)[0]
    records=original_ordered_player_records
    if type(records) is not tuple:
        raise Original510CD0SourceError("native roster records tuple required")
    if original_count<=0:
        if records:
            raise Original510CD0SourceError("zero/negative roster never reaches 417F50")
        return SourceOriginal510CD0SelectedRoster(
            key,original_count,target,SOURCE_510CD0_SELECTION_ARRAY_SLOTS[target],
            (),(),(),(),0)
    if (original_count>SOURCE_510CD0_ARRAY_CAPACITY or
            len(team)<0x244+2*original_count or len(records)!=original_count):
        raise Original510CD0SourceError(
            "original selected-array capacity or ordered complete roster violated")
    reached_a=[]
    reached_b=[]
    selected_pointers=[]
    selected_ids=[]
    for index,r in enumerate(records):
        if type(r) is not SourceOriginal406BE0Player:
            raise Original510CD0SourceError("original player source receipt required")
        pid=unpack_from("<H",team,0x244+2*index)[0]
        ptr=base+pid*0x250
        if (ptr>0xffffffff or type(r.original_roster_word_id) is not int or
                r.original_roster_word_id!=pid or
                type(r.original_player_record_native_pointer) is not int or
                r.original_player_record_native_pointer!=ptr):
            raise Original510CD0SourceError("original player pointer/WORD roster order mismatch")
        raw=r.original_player_record_bytes
        if type(raw) is not bytes or len(raw)<0x18:
            raise Original510CD0SourceError("player+10 signed owner and +14 flags required")
        sign_owner=unpack_from("<h",raw,0x10)[0]&0xffffffff
        flags14=unpack_from("<I",raw,0x14)[0]
        reached_a.append(pid)
        first=(sign_owner==key and bool(flags14&0x10))
        if first:
            valid=True
        else:
            reached_b.append(pid)
            valid=sign_owner==key and bool(flags14&0x20)
        if valid:
            selected_pointers.append(ptr)
            selected_ids.append(pid)
    return SourceOriginal510CD0SelectedRoster(
        key,original_count,target,SOURCE_510CD0_SELECTION_ARRAY_SLOTS[target],
        tuple(selected_pointers),tuple(reached_a),tuple(reached_b),
        tuple(selected_ids),len(selected_pointers))


@dataclass(frozen=True)
class SourceOriginal5111A0SelectionArrayTail:
    original_match_vtable: int
    source_first_team_receipt: SourceOriginal510CD0SelectedRoster
    source_second_team_receipt: SourceOriginal510CD0SelectedRoster
    original_5111a0_other_callbacks_executed: bool = False
    original_context_mutations_executed: bool = False
    original_match_executed: bool = False
    saved_game_state_updated: bool = False


def source_original_5111a0_two_source_selection_arrays(
    *, original_match_record: bytes,
    original_first_407770_zero_gate_nonzero: bool,
    original_second_407770_zero_gate_nonzero: bool,
    original_first_405a20_source_sort: SourceOriginal405A20NativeRosterSort,
    original_second_405a20_source_sort: SourceOriginal405A20NativeRosterSort,
    original_global_875640_player_array_address: int,
) -> SourceOriginal5111A0SelectionArrayTail:
    """ONLY final source 5111A0 510CD0 collection writes, no full 5111A0.

    Called by 510D60 only when the earlier TWO 407770(0) returned nonzero,
    before the remaining two 407770(1). Requires authentic native match
    vtable/record, but does not guess original 409B50 side effects.

    Critical: 5111A0 calls TWO mutating 405A20 sorts before 510CD0.
    This composes only explicit 405A20 *source-projected* sorted snapshots.
    Neither the source-projected sort nor 5111A0 callbacks actually ran.
    A caller MUST source-qualify original team snapshots at the entry to
    both 405A20 calls, after any 409B50 modifications. A prior unsorted
    raw roster is NOT an original reached 510CD0 input.
    """
    from original_leaguematch_native_process_owners import (
        OriginalLeagueMatchProcessOwnerError,
    )
    if (type(original_first_407770_zero_gate_nonzero) is not bool or
            type(original_second_407770_zero_gate_nonzero) is not bool or
            not original_first_407770_zero_gate_nonzero or
            not original_second_407770_zero_gate_nonzero):
        raise Original510CD0SourceError(
            "original 5111A0 not reached without two 407770(0) successes")
    try:
        owners=source_original_leaguematch_process_owners_for_native_record(
            original_match_record=original_match_record)
    except OriginalLeagueMatchProcessOwnerError as exc:
        raise Original510CD0SourceError(
            "source LeagueMatch vtable required before 5111A0") from exc
    a=original_first_405a20_source_sort
    b=original_second_405a20_source_sort
    if (type(a) is not SourceOriginal405A20NativeRosterSort or
            type(b) is not SourceOriginal405A20NativeRosterSort or
            a.original_405a20_executed or b.original_405a20_executed):
        raise Original510CD0SourceError("two native 405A20 source projections, not execution receipts, required")
    first=source_original_510cd0_selected_player_pointers(
        original_team_record=a.source_projected_team_after_405a20,
        original_global_875640_player_array_address=original_global_875640_player_array_address,
        original_ordered_player_records=a.original_player_records_sorted_for_510cd0,
        original_target_processing_context_offset=0x4)
    second=source_original_510cd0_selected_player_pointers(
        original_team_record=b.source_projected_team_after_405a20,
        original_global_875640_player_array_address=original_global_875640_player_array_address,
        original_ordered_player_records=b.original_player_records_sorted_for_510cd0,
        original_target_processing_context_offset=0x5B4)
    return SourceOriginal5111A0SelectionArrayTail(owners.source_vtable_va,first,second)
