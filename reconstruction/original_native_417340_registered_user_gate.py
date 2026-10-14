"""Original 0x417340 -> 0x417270 -> 0x4037B0 -> 0x4139E0/0x4139F0.

Read-only source projection from the original private footballmanager.exe
(SHA-256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3).
The native chain checks whether a player's CURRENT signed +0x10 team owner
has a registered human user. This is NOT player+0x72 registered-club
ownership, a delivered Inbox event or a native callback execution.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from


class Original417340SourceError(ValueError):
    pass


@dataclass(frozen=True)
class Original417340ReachedUser:
    original_manager_link_pointer: int
    original_manager_link_record: bytes
    original_user_pointer: int
    original_user_record: bytes
    original_user_context_pointer: int
    original_user_context_record: bytes


@dataclass(frozen=True)
class Original417340RegisteredUserReceipt:
    original_native_player_at_call: bytes
    original_native_player_id: int
    original_current_club_index_signed: int
    original_source_club_pointer: int
    original_source_club_owner_key: int
    original_visited_manager_link_pointers: tuple[int, ...]
    original_matching_user_pointer: int | None
    original_417340_return_al: int
    native_callback_executed: bool = False
    live_game_state_updated: bool = False


def _ptr(value: int, name: str, *, allow_zero: bool = False) -> int:
    if type(value) is not int or not (0 <= value <= 0xffffffff) or (
        not allow_zero and value == 0
    ):
        raise Original417340SourceError(f"actual original {name} pointer required")
    return value


def source_original_417340_registered_user_from_reached(
    *,
    original_player_at_call: bytes,
    original_874b90_club_array_base: int | None,
    original_874b94_default_club_pointer: int | None,
    original_reached_club_pointer: int,
    original_reached_club_record: bytes,
    original_global_874c10_record: bytes,
    original_reached_manager_links: tuple[Original417340ReachedUser, ...],
    max_manager_links: int = 65536,
) -> Original417340RegisteredUserReceipt:
    """Reproduce the exact source *read-only* team/manager predicate.

    417270: signed player+10; negative selects global 874B94 pointer,
    nonnegative selects global 874B90 + (680 * signed index).
    4037B0->4139E0: loads DWORD team+4 as comparison key.
    4139F0: scans global 874C10+9CC singly linked manager/user list;
    node+0 is user*, node+4 is next*, user+5B4 is context*;
    context+4 equals original team+4 -> original AL 1, else AL 0.
    No getter, heap, RNG or message mutation occurs in this native chain.
    """
    p=original_player_at_call
    if type(p) is not bytes or len(p)<0x12:
        raise Original417340SourceError("source player bytes through signed +10 required")
    club_index=unpack_from("<h",p,0x10)[0]
    if club_index < 0:
        selected=_ptr(original_874b94_default_club_pointer,"874B94 negative-side fallback")
        if original_874b90_club_array_base is not None:
            raise Original417340SourceError("negative club path skips 874B90")
    else:
        base=_ptr(original_874b90_club_array_base,"874B90 indexed-club base")
        if original_874b94_default_club_pointer is not None:
            raise Original417340SourceError("indexed-club path skips 874B94")
        selected=base+club_index*680
        if not 0 < selected <= 0xffffffff:
            raise Original417340SourceError("indexed-club pointer overflow/zero unresolved")
    received=_ptr(original_reached_club_pointer,"reached original club")
    if selected != received:
        raise Original417340SourceError("native 417270 reached club pointer identity mismatch")
    club=original_reached_club_record
    if type(club) is not bytes or len(club)<8:
        raise Original417340SourceError("native club source bytes through +4 required")
    key=unpack_from("<I",club,4)[0]
    owner=original_global_874c10_record
    if type(owner) is not bytes or len(owner)<0x9d0:
        raise Original417340SourceError("native global owner bytes through +9CC required")
    if type(original_reached_manager_links) is not tuple:
        raise Original417340SourceError("ordered original reached manager links tuple required")
    if type(max_manager_links) is not int or not 1<=max_manager_links<=65536:
        raise Original417340SourceError("bounded native manager link cap required")
    cur=unpack_from("<I",owner,0x9cc)[0]
    seen=set()
    visited=[]
    matching_user=None
    for link in original_reached_manager_links:
        if not cur:
            raise Original417340SourceError("extra original manager link after zero/first match")
        if cur in seen or len(visited)>=max_manager_links:
            raise Original417340SourceError("source manager chain cyclic/too long")
        if not isinstance(link,Original417340ReachedUser):
            raise Original417340SourceError("source reached manager record type required")
        if _ptr(link.original_manager_link_pointer,"manager link") != cur:
            raise Original417340SourceError("actual reached manager link pointer mismatch")
        node=link.original_manager_link_record
        if type(node) is not bytes or len(node)<8:
            raise Original417340SourceError("manager link+0/+4 bytes required")
        user_pointer=_ptr(link.original_user_pointer,"manager user")
        if unpack_from("<I",node,0)[0]!=user_pointer:
            raise Original417340SourceError("manager node+0 user pointer identity mismatch")
        user=link.original_user_record
        if type(user) is not bytes or len(user)<0x5b8:
            raise Original417340SourceError("user native +5B4 context bytes required")
        ctx_ptr=_ptr(link.original_user_context_pointer,"user context")
        if unpack_from("<I",user,0x5b4)[0]!=ctx_ptr:
            raise Original417340SourceError("user+5B4 context pointer identity mismatch")
        ctx=link.original_user_context_record
        if type(ctx) is not bytes or len(ctx)<8:
            raise Original417340SourceError("manager context+4 key bytes required")
        seen.add(cur)
        visited.append(cur)
        if unpack_from("<I",ctx,4)[0]==key:
            matching_user=user_pointer
            cur=0
            break
        cur=unpack_from("<I",node,4)[0]
    if len(visited)!=len(original_reached_manager_links):
        raise Original417340SourceError("extra original manager link after first source match")
    if cur:
        raise Original417340SourceError("original manager scan stopped at nonterminal/unreached link")
    return Original417340RegisteredUserReceipt(
        original_native_player_at_call=p,
        original_native_player_id=unpack_from("<H",p,4)[0],
        original_current_club_index_signed=club_index,
        original_source_club_pointer=selected,
        original_source_club_owner_key=key,
        original_visited_manager_link_pointers=tuple(visited),
        original_matching_user_pointer=matching_user,
        original_417340_return_al=int(matching_user is not None),
    )
