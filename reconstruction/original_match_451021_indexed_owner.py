"""Original 451021 indexed-manager scoring queue versus 5DB450 club-selected queue.

Static source from authorized original PE SHA833bf95e...b7cc3:
451005 reads WORD club+4 and 4139D0->413B10 treats it as a ZERO-BASED
manager-list ORDINAL, not a club key. 451014 fetches presentation +E0
DWORD index and 45101A uses user+(index*4)+670 pointer. In contrast
403850->413B40 selects first user whose context+4 equals club DWORD+4
masked to 16 bits; 5DB450 reads user+670 (zero index).

This is a *source snapshot comparison*; registered lists may change
between calls and normal game reachability is unproven. Never silently
treat these differently keyed user selections as the same manager or
produce GameState match scores from an inferred queue.
"""
from dataclasses import dataclass
from struct import unpack_from

from original_native_417340_registered_user_gate import Original417340ReachedUser


class Original451021IndexedOwnerError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal451021IndexedOwner:
    original_reader_manager_ordinal_from_d8_word: int
    original_reader_user_pointer: int
    original_reader_plus_e0_queue_slot_index: int
    original_reader_queue_pointer: int
    original_writer_full_club_key: int
    original_writer_masked_club_key: int
    original_writer_user_pointer: int
    original_writer_base_queue_pointer: int
    native_snapshot_user_pointers_equal: bool
    native_snapshot_queue_pointers_equal: bool
    native_intervening_mutations_excluded: bool = False
    original_native_451021_executed: bool = False
    live_original_match_owner_join_proven: bool = False
    game_state_updated: bool = False


def _u32(v, label, *, allow_zero=False):
    if type(v) is not int or not 0<=v<=0xffffffff or (not allow_zero and not v):
        raise Original451021IndexedOwnerError(label + ' exact native u32 required')
    return v


def source_original_451021_reader_5db450_writer_snapshot(
    *,
    original_874c10_global_at_comparison: bytes,
    original_complete_registered_manager_links: tuple[Original417340ReachedUser, ...],
    original_451005_club_d8_record: bytes,
    original_451014_presenter_record: bytes,
    original_5db3ac_first_side_club_record: bytes,
    original_reader_reached_4139d0_user_pointer: int,
    original_writer_reached_403850_user_pointer: int,
) -> SourceOriginal451021IndexedOwner:
    root=original_874c10_global_at_comparison
    if type(root) is not bytes or len(root)<0x9d0:
        raise Original451021IndexedOwnerError('actual original 874C10+9CC manager root required')
    nodes=original_complete_registered_manager_links
    if type(nodes) is not tuple or len(nodes)>65536:
        raise Original451021IndexedOwnerError('complete native manager tuple required')
    cursor=unpack_from('<I',root,0x9cc)[0]
    visited=set()
    owners=[]
    for node in nodes:
        if type(node) is not Original417340ReachedUser:
            raise Original451021IndexedOwnerError('actual native typed manager node required')
        ptr=_u32(node.original_manager_link_pointer,'manager link')
        userptr=_u32(node.original_user_pointer,'registered user')
        contextptr=_u32(node.original_user_context_pointer,'registered context')
        if ptr!=cursor or ptr in visited or userptr in (n[0] for n in owners):
            raise Original451021IndexedOwnerError('manager root chain order, cycle or duplicate user')
        link=node.original_manager_link_record
        user=node.original_user_record
        context=node.original_user_context_record
        if (type(link) is not bytes or len(link)<8 or
            type(user) is not bytes or len(user)<0x674 or
            type(context) is not bytes or len(context)<8 or
            unpack_from('<I',link)[0]!=userptr or
            unpack_from('<I',user,0x5b4)[0]!=contextptr):
            raise Original451021IndexedOwnerError('manager native records or pointer ownership mismatch')
        owners.append((userptr,unpack_from('<I',context,4)[0],user))
        visited.add(ptr)
        cursor=unpack_from('<I',link,4)[0]
    if cursor:
        raise Original451021IndexedOwnerError('source manager chain incomplete')
    reader_club=original_451005_club_d8_record
    writer_club=original_5db3ac_first_side_club_record
    presenter=original_451014_presenter_record
    if (type(reader_club) is not bytes or len(reader_club)<8 or
        type(writer_club) is not bytes or len(writer_club)<8 or
        type(presenter) is not bytes or len(presenter)<0xe4):
        raise Original451021IndexedOwnerError('actual reader club, writer club and presenter+E0 bytes required')
    ordinal=unpack_from('<H',reader_club,4)[0]
    writer_key=unpack_from('<I',writer_club,4)[0]
    slot=unpack_from('<I',presenter,0xe0)[0]
    if ordinal>=len(owners):
        raise Original451021IndexedOwnerError('ordinal 413B10 returned null; no reached 45101A read')
    reader=owners[ordinal]
    readerptr=_u32(original_reader_reached_4139d0_user_pointer,'reached reader user')
    if readerptr!=reader[0]:
        raise Original451021IndexedOwnerError('original reader 413B10 index result differs')
    full_match=next((u for u in owners if u[1]==writer_key),None)
    if full_match is None:
        raise Original451021IndexedOwnerError('writer original full-key 4037B0 false; no human callback')
    masked_key=writer_key & 0xffff
    writer=next((u for u in owners if u[1]==masked_key),None)
    if writer is None:
        raise Original451021IndexedOwnerError('403850 masked writer user missing after full-key gate')
    writerptr=_u32(original_writer_reached_403850_user_pointer,'reached writer user')
    if writerptr!=writer[0]:
        raise Original451021IndexedOwnerError('original 413B40 writer masked lookup differs')
    offset=0x670+4*slot
    if slot>0x3fffffff or offset+4>len(reader[2]):
        raise Original451021IndexedOwnerError('reader dynamic +670 indexed slot bytes unavailable')
    readqueue=unpack_from('<I',reader[2],offset)[0]
    writequeue=unpack_from('<I',writer[2],0x670)[0]
    _u32(readqueue,'reader queue object')
    _u32(writequeue,'writer queue object')
    return SourceOriginal451021IndexedOwner(
        ordinal,readerptr,slot,readqueue,writer_key,masked_key,
        writerptr,writequeue,readerptr==writerptr,readqueue==writequeue)
