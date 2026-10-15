"""Original 5DA2F0 non-managed team numeric inputs and registered-user predicate.

This source projection covers exactly the entry decision 5DA31A->4037B0
(4139E0->4139F0 manager-owned club membership) and the FALSE branch at
5DA538..5DA5CF. It does not execute 5DA2F0, calculate a match result,
or equate player/club/registration pointers. Other team branch 5DA327
reads separate user+694/+6B0 sources and remains outstanding.
Canonical original PE: 4714541 bytes sha256 833bf95e...b7cc3.
"""
from __future__ import annotations
from dataclasses import dataclass
from struct import unpack_from

from original_native_417340_registered_user_gate import Original417340ReachedUser


class OriginalNonManagedMatchInputError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalMatch4037B0TeamOwner:
    native_team_pointer: int
    native_team_club_key: int
    visited_registered_user_pointers: tuple[int, ...]
    source_matching_registered_user_pointer: int | None
    source_4037b0_return_al: int
    original_callbacks_executed: bool = False


@dataclass(frozen=True)
class Original5DA2F0NonManagedStats:
    native_team_pointer: int
    original_team_fields_134_138_13c_140: tuple[int,int,int,int]
    source_nonmanaged_double_values_134_138_13c_140: tuple[float,float,float,float]
    original_comparison_limit: int = 200000
    original_match_calculator_invoked: bool = False
    game_state_modified: bool = False


def original_5da2f0_4037b0_team_registration(
    *, original_team_pointer:int, original_team_record:bytes,
    original_874c10_registry_root:bytes,
    original_reached_manager_links:tuple[Original417340ReachedUser,...],
) -> OriginalMatch4037B0TeamOwner:
    """Source 4037B0 passes team+4 to 4139E0/4139F0.

    The manager list is traversed only until first match, or to its null
    terminator. Context +4 is compared FULL DWORD, not masked first 16 bits;
    403850 performs a separate low-16 user lookup after the decision.
    """
    if type(original_team_pointer) is not int or not 0<original_team_pointer<=0xffffffff:
        raise OriginalNonManagedMatchInputError("actual team object pointer required")
    team=original_team_record
    root=original_874c10_registry_root
    if type(team) is not bytes or len(team)<0x144 or type(root) is not bytes or len(root)<0x9d0:
        raise OriginalNonManagedMatchInputError("original complete team/registry bytes required")
    nodes=original_reached_manager_links
    if type(nodes) is not tuple or len(nodes)>65536:
        raise OriginalNonManagedMatchInputError("bounded ordered original registered-user records required")
    key=unpack_from("<I",team,4)[0]
    cursor=unpack_from("<I",root,0x9cc)[0]
    visited=[]
    seen=set()
    match=None
    for link in nodes:
        if not cursor or type(link) is not Original417340ReachedUser:
            raise OriginalNonManagedMatchInputError("unreached/invalid original registered manager link")
        if type(link.original_manager_link_pointer) is not int or link.original_manager_link_pointer!=cursor or cursor in seen:
            raise OriginalNonManagedMatchInputError("source manager list cycle/order mismatch")
        node,user,context=link.original_manager_link_record,link.original_user_record,link.original_user_context_record
        userptr,contextptr=link.original_user_pointer,link.original_user_context_pointer
        if (type(userptr) is not int or not 0<userptr<=0xffffffff or
            type(contextptr) is not int or not 0<contextptr<=0xffffffff or
            type(node) is not bytes or len(node)<8 or
            type(user) is not bytes or len(user)<0x5b8 or
            type(context) is not bytes or len(context)<8 or
            unpack_from("<I",node)[0]!=userptr or
            unpack_from("<I",user,0x5b4)[0]!=contextptr):
            raise OriginalNonManagedMatchInputError("original user/context pointer chain mismatch")
        seen.add(cursor)
        visited.append(userptr)
        if unpack_from("<I",context,4)[0]==key:
            match=userptr
            cursor=0
            break
        cursor=unpack_from("<I",node,4)[0]
    if cursor or len(visited)!=len(nodes):
        raise OriginalNonManagedMatchInputError("native 4139F0 list truncated or includes unvisited links")
    return OriginalMatch4037B0TeamOwner(original_team_pointer,key,tuple(visited),match,int(match is not None))


def source_original_5da538_nonmanaged_team_fields(
    *, original_registration:OriginalMatch4037B0TeamOwner,
    original_team_pointer:int,
    original_team_record_after_4037b0:bytes,
) -> Original5DA2F0NonManagedStats:
    """Source native 5DA538 branch: 4 unsigned DWORDs converted as QWORD fild.

    Native code zero extends each DWORD to signed QWORD by zeroing the
    high DWORD. The first two (team+140,+13C) then compare to double
    constant 200000.0; if GREATER they are set to zero. The other two
    (+138,+134) are not subject to that comparison in this source path.
    Note return tuple ordered by ascending field address.
    """
    r=original_registration
    if type(r) is not OriginalMatch4037B0TeamOwner or r.source_4037b0_return_al!=0 or r.source_matching_registered_user_pointer is not None:
        raise OriginalNonManagedMatchInputError("original 5DA538 requires confirmed 4037B0 false branch")
    if (type(original_team_pointer) is not int or original_team_pointer!=r.native_team_pointer or
        type(original_team_record_after_4037b0) is not bytes or len(original_team_record_after_4037b0)<0x144 or
        unpack_from("<I",original_team_record_after_4037b0,4)[0]!=r.native_team_club_key):
        raise OriginalNonManagedMatchInputError("source original post-4037B0 same team record required")
    raw=tuple(unpack_from("<I",original_team_record_after_4037b0,o)[0] for o in (0x134,0x138,0x13c,0x140))
    converted=(float(raw[0]),float(raw[1]),float(raw[2] if raw[2]<=200000 else 0),
               float(raw[3] if raw[3]<=200000 else 0))
    return Original5DA2F0NonManagedStats(original_team_pointer,raw,converted)
