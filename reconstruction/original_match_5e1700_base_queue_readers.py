"""Original 5E1700 current registered-user base+670 two numeric queue readers.

Independent original PE source: 5E1700 calls 4139D0, selecting the
registered-user list ordinal stored at global 874C10+9C4. 5E1756
reads user+670 and stores it at stack T+1C. 5E1765 SUB ESP,0C;
5E177A PUSH 65; 5E177E [ESP+2C] reads exactly T+1C and is ECX
for 5E178C CALL 5DC890. At 5E17D1 second user+670 is stored
and 5E17E7 SUB ESP,0C / 5E1804 PUSH 66 / 5E1810 [ESP+2C]
selects its exact same base queue for 5E1814 CALL 5DC890.
These are READERS, not proofs the earlier original match 5DB450
writer owns the same reached user instance or either result is
applied during the normal LeagueMatch 513252 lifecycle.
"""
from dataclasses import dataclass
from struct import unpack_from
from original_native_417340_registered_user_gate import Original417340ReachedUser


class Original5E1700SourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal5E1700BaseQueueReaders:
    original_registered_current_user_ordinal: int
    original_registered_current_user_pointer: int
    original_user_base_670_queue_pointer: int
    original_first_5dc890_selector: int = 0x65
    original_second_5dc890_selector: int = 0x66
    original_first_call: int = 0x5E178C
    original_second_call: int = 0x5E1814
    source_same_base_queue_pointer_both_reads: bool = True
    original_match_writer_user_identity_proven: bool = False
    original_5dc890_native_calculations_executed: bool = False
    game_state_updated: bool = False


def source_original_5e1700_current_user_base_queue(
    *,
    original_874c10_global_record: bytes,
    original_registered_manager_links: tuple[Original417340ReachedUser, ...],
    original_reached_4139d0_user_pointer_at_5e170a: int,
    original_reached_queue_pointer_at_5e1756: int,
    original_reached_queue_pointer_at_5e17d1: int,
) -> SourceOriginal5E1700BaseQueueReaders:
    root=original_874c10_global_record
    links=original_registered_manager_links
    if type(root) is not bytes or len(root)<0x9d0 or type(links) is not tuple or len(links)>65536:
        raise Original5E1700SourceError('complete native root and ordered manager chain required')
    ordinal=unpack_from('<I',root,0x9c4)[0]
    cursor=unpack_from('<I',root,0x9cc)[0]
    users=[]
    seen=set()
    for link in links:
        if type(link) is not Original417340ReachedUser:
            raise Original5E1700SourceError('typed original native manager link required')
        ptr=link.original_manager_link_pointer
        userptr=link.original_user_pointer
        contextptr=link.original_user_context_pointer
        if (type(ptr) is not int or not 0<ptr<=0xffffffff or
            type(userptr) is not int or not 0<userptr<=0xffffffff or
            type(contextptr) is not int or not 0<contextptr<=0xffffffff or
            ptr!=cursor or ptr in seen or any(u[0]==userptr for u in users)):
            raise Original5E1700SourceError('native manager link chain/alias corrupted')
        node,user,ctx=(link.original_manager_link_record,
            link.original_user_record,link.original_user_context_record)
        if (type(node) is not bytes or len(node)<8 or
            type(user) is not bytes or len(user)<0x674 or
            type(ctx) is not bytes or len(ctx)<8 or
            unpack_from('<I',node)[0]!=userptr or
            unpack_from('<I',user,0x5b4)[0]!=contextptr):
            raise Original5E1700SourceError('native registered user/context pointers mismatch')
        users.append((userptr,user))
        seen.add(ptr)
        cursor=unpack_from('<I',node,4)[0]
    if cursor or ordinal>=len(users):
        raise Original5E1700SourceError('global+9C4 original 413B10 index unresolved')
    ptr,user=users[ordinal]
    if (type(original_reached_4139d0_user_pointer_at_5e170a) is not int or
        original_reached_4139d0_user_pointer_at_5e170a!=ptr):
        raise Original5E1700SourceError('original 4139D0 reached selected user mismatches list ordinal')
    base=unpack_from('<I',user,0x670)[0]
    if not base:
        raise Original5E1700SourceError('native user+670 queue pointer missing')
    for pointer in (original_reached_queue_pointer_at_5e1756,
                    original_reached_queue_pointer_at_5e17d1):
        if type(pointer) is not int or pointer!=base:
            raise Original5E1700SourceError('native source base queue changed before two score queries')
    return SourceOriginal5E1700BaseQueueReaders(ordinal,ptr,base)
