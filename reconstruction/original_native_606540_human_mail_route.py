"""Original 606540 injury notice -> 7BD564 due -> 413020 type 2/30/31 user route.

Private original footballmanager.exe: 4,714,541 bytes; SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Source 60667E..606CBB, 5CE660, 5CFA20, 413020/413510/413554.
No native executable launch, original heap/callback execution or live Inbox.

IMPORTANT: 606540's three constructor families use DIFFERENT type descriptors:
4D1190 nonnull -> 5CE660 kind31, 4D1110 nonnull -> kind30, both null
-> kind2 with a DBRPlayer+72 signed association. 413020's type31 and
type30 native jump cases RETEST the lookup when the pending wrapper is DUE;
type2 goes directly to the generic category1 owner path. The outcome at
constructor time cannot stand in for the later lookup result.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import pack_into, unpack_from

from original_native_606540_human_notice import (
    Original606540HumanNoticeReached,
    source_original_606540_human_notice_plan,
)
from original_native_413020_type12_human_route import Original413020ReachedManager


class Original606540HumanMailRouteError(ValueError):
    pass


# Original constructor-address -> (vtable, virtual+0x0C literal tag).
# Source original 606540 status jump tables, each constructor stores this
# precise vtable after 5CE660's category1/second descriptor initialization.
_CONSTRUCTORS = {
    0x58AD80:(0x7D1D34,244),0x58B670:(0x7D1E30,247),
    0x58BEA0:(0x7D1F2C,250),0x58AA70:(0x7D1CE0,243),
    0x58B360:(0x7D1DDC,246),0x58BB90:(0x7D1ED8,249),
    0x58B090:(0x7D1D88,245),0x58B980:(0x7D1E84,248),
    0x58C1B0:(0x7D1F80,251),0x59FEC0:(0x7D42D4,361),
    0x5A04E0:(0x7D437C,363),0x59F8E0:(0x7D422C,359),
    0x5A01D0:(0x7D4328,362),0x59FBF0:(0x7D4280,360),
    0x5A07F0:(0x7D43D0,364),
}
_TYPE_BY_LOOKUP_FAMILY = (31,30,2)
# In 413020, 31 -> 413218/4D1190, 30 -> 4130DC/4D1110,
# 2 -> category1 default (no conditional second lookup).
_TYPE_CASE_BRANCHES = (0x413218,0x4130DC,0x41325A)


@dataclass(frozen=True)
class Original606540HumanDueReached:
    original_construction_source: Original606540HumanNoticeReached
    original_417270_constructor_club_pointer: int
    original_417270_constructor_club_record: bytes
    original_constructed_notice_pointer: int
    original_constructed_notice_bytes_before_due: bytes
    original_7bd564_wrapper_pointer: int
    original_7bd564_wrapper_before_due: bytes
    original_native_current_date_raw_u32: int
    original_global_874c10_record_at_due: bytes
    original_413020_reached_manager_nodes: tuple[Original413020ReachedManager, ...]
    # Re-read only for the reached matched user and 30/31 dispatch branch.
    original_413020_type_lookup_nonnull_if_reached: bool | None = None


@dataclass(frozen=True)
class Original606540HumanDueReceipt:
    original_player_id: int
    original_constructor: int
    original_concrete_notice_vtable: int
    original_native_virtual0c_tag: int
    original_native_type_descriptor: int
    original_type_case_address: int
    original_source_due_date_signed32: int
    original_source_current_date_signed32: int
    original_source_due_wrapper_after_5cfa20: bytes
    original_source_notice_after_5cfa20: bytes
    original_413020_reached_manager_links: tuple[int, ...]
    original_413020_qualified_recipient_user_pointer: int | None
    original_413020_candidate_user_queue_pointer: int | None
    original_413020_deferred_lookup_gated_out: bool
    original_native_constructor_executed: bool = False
    original_native_5cfa20_executed: bool = False
    original_native_413020_executed: bool = False
    original_user_queue_mutated: bool = False
    original_inbox_row_rendered: bool = False
    live_game_state_updated: bool = False


def _ptr(n: int, name: str) -> int:
    if type(n) is not int or not 0<n<=0xffffffff:
        raise Original606540HumanMailRouteError(f"reached native {name} non-null DWORD required")
    return n


def _signed(n: int) -> int:
    return n-0x100000000 if n>=0x80000000 else n


def source_original_606540_human_notice_due_to_user(
    reached: Original606540HumanDueReached,
) -> Original606540HumanDueReceipt:
    """Proven source candidate, NOT a native event insertion/delivered row.

    Native source 5CFA20 first reads referenced vft+3C (all fifteen are
    4093E0 constant1), copies wrapper+4 date to record+4, clears
    wrapper+8 and passes record to 413020. The latter visits the global
    ordered registered-user chain; source registered club+40 must match
    constructor category1 +14 manager key. For kind30/31 it then rechecks
    native 4D1110/4D1190, respectively; if NULL it returns through the
    constant-zero vft+10 branch without user queue append. For kind2 the
    source jumps immediately to category1 and appends. No branch equates
    a pending envelope with a user-visible inbox row or successful free.
    """
    if not isinstance(reached,Original606540HumanDueReached):
        raise Original606540HumanMailRouteError("typed original human due stage required")
    plan=source_original_606540_human_notice_plan(reached.original_construction_source)
    entry=_CONSTRUCTORS.get(plan.original_selected_constructor_address)
    if entry is None:
        raise Original606540HumanMailRouteError("unqualified original notice constructor")
    vt,tag=entry
    clubptr=_ptr(reached.original_417270_constructor_club_pointer,"constructor club")
    owner=reached.original_construction_source.original_registered_417340_owner_proof
    if clubptr!=owner.original_source_club_pointer:
        raise Original606540HumanMailRouteError("constructor reached 417270 club owner disagrees with original 417340")
    club=reached.original_417270_constructor_club_record
    if type(club) is not bytes or len(club)<0x44:
        raise Original606540HumanMailRouteError("reached native club +40 manager key required")
    club_key=unpack_from("<I",club,0x40)[0]
    noticeptr=_ptr(reached.original_constructed_notice_pointer,"notice object")
    wrap_ptr=_ptr(reached.original_7bd564_wrapper_pointer,"wrapper")
    raw=reached.original_constructed_notice_bytes_before_due
    if type(raw) is not bytes or len(raw)!=plan.original_constructor_object_size:
        raise Original606540HumanMailRouteError("actual constructor-size original notice object bytes required")
    pid=plan.original_player_id
    kind=_TYPE_BY_LOOKUP_FAMILY[plan.original_lookup_family]
    if (unpack_from("<I",raw,0)[0]!=vt or
            unpack_from("<I",raw,4)[0]!=0xffffffff or
            unpack_from("<I",raw,8)[0]&6!=6 or
            unpack_from("<I",raw,0xc)[0]!=5 or
            unpack_from("<I",raw,0x10)[0]!=1 or
            unpack_from("<I",raw,0x14)[0]!=club_key or
            unpack_from("<I",raw,0x1c)[0]!=kind or
            unpack_from("<I",raw,0x3c)[0]!=pid):
        raise Original606540HumanMailRouteError("native constructor vtable/category/type/player/manager identity mismatch")
    # For type2 the second 5CE660 input is a separately resolved native
    # player ID; only the player identity and source +72 signed club
    # association are accepted, never a made-up zero or generic squad ID.
    player=owner.original_native_player_at_call
    if kind==2:
        if (unpack_from("<I",raw,0x20)[0]!=pid or
                unpack_from("<i",raw,0x24)[0]!=unpack_from("<h",player,0x72)[0] or
                unpack_from("<I",raw,0x40)[0]!=pid or
                unpack_from("<I",raw,0x44)[0]!=club_key):
            raise Original606540HumanMailRouteError("native kind2 player+72 / third club-key owner mismatch")
    elif (unpack_from("<I",raw,0x20)[0]!=0 or
            unpack_from("<I",raw,0x24)[0]!=0xffffffff or
            unpack_from("<I",raw,0x40)[0]!=club_key):
        raise Original606540HumanMailRouteError("native kind30/31 three-word descriptor owner mismatch")
    envelope=reached.original_7bd564_wrapper_before_due
    if (type(envelope) is not bytes or len(envelope)!=12 or
            unpack_from("<I",envelope,0)[0]!=0x7bd564 or
            unpack_from("<I",envelope,4)[0]!=plan.original_notice_wrapper_date_raw_u32 or
            unpack_from("<I",envelope,8)[0]!=noticeptr):
        raise Original606540HumanMailRouteError("original 7BD564 due wrapper/constructor ownership mismatch")
    day=reached.original_native_current_date_raw_u32
    if type(day) is not int or not 0<=day<=0xffffffff:
        raise Original606540HumanMailRouteError("actual native due-current calendar uint32 required")
    due=_signed(unpack_from("<I",envelope,4)[0])
    current=_signed(day)
    if due>current:
        raise Original606540HumanMailRouteError("original 613EE0 signed future event not dispatched")
    # 5CFA20 source mutations only. It is not the append to user+6B4.
    next_raw=bytearray(raw)
    pack_into("<I",next_raw,4,unpack_from("<I",envelope,4)[0])
    next_wrapper=bytearray(envelope)
    pack_into("<I",next_wrapper,8,0)
    globalrec=reached.original_global_874c10_record_at_due
    if type(globalrec) is not bytes or len(globalrec)<0x9d0:
        raise Original606540HumanMailRouteError("original 874C10 registered-user root +9CC required")
    nodes=reached.original_413020_reached_manager_nodes
    if type(nodes) is not tuple or len(nodes)>6:
        raise Original606540HumanMailRouteError("actual ordered 1-6 original manager links required")
    addr=unpack_from("<I",globalrec,0x9cc)[0]
    visited=[]; seen=set()
    candidate_user=None;candidate_queue=None
    for n in nodes:
        if not addr or addr in seen or not isinstance(n,Original413020ReachedManager):
            raise Original606540HumanMailRouteError("stale or cyclic registered user link")
        if n.original_manager_link_pointer!=addr:
            raise Original606540HumanMailRouteError("native 413020 linked-user traversal order mismatch")
        node=n.original_manager_link_record
        if type(node) is not bytes or len(node)<8 or unpack_from("<I",node,0)[0]!=_ptr(n.original_user_pointer,"user"):
            raise Original606540HumanMailRouteError("native manager node+0 user owner mismatch")
        user=n.original_user_record
        if type(user) is not bytes or len(user)<0x6b8:
            raise Original606540HumanMailRouteError("original user bytes through+6B4 required")
        ctxptr=_ptr(n.original_user_context_pointer,"user context")
        ctx=n.original_user_context_record
        if (unpack_from("<I",user,0x5b4)[0]!=ctxptr or type(ctx) is not bytes
                or len(ctx)<0x44):
            raise Original606540HumanMailRouteError("reached original manager context through+40 required")
        seen.add(addr); visited.append(addr)
        if unpack_from("<I",ctx,0x40)[0]==club_key:
            candidate_user=_ptr(n.original_user_pointer,"matched user")
            candidate_queue=_ptr(unpack_from("<I",user,0x6b4)[0],"matched user+6B4")
            addr=0
            break
        addr=unpack_from("<I",node,4)[0]
    if addr or len(visited)!=len(nodes):
        raise Original606540HumanMailRouteError("incomplete or extra original registered-user source scans")
    lookup=reached.original_413020_type_lookup_nonnull_if_reached
    gated_out=False
    if candidate_user is not None:
        if kind in (30,31):
            if type(lookup) is not bool:
                raise Original606540HumanMailRouteError("native 413020 later 4D1110/4D1190 recheck required")
            gated_out=not lookup
        elif lookup is not None:
            raise Original606540HumanMailRouteError("native type2 skips 4D lookup entirely")
    elif lookup is not None:
        raise Original606540HumanMailRouteError("unmatched user never reaches conditional type lookup")
    return Original606540HumanDueReceipt(
        pid,plan.original_selected_constructor_address,vt,tag,kind,
        _TYPE_CASE_BRANCHES[plan.original_lookup_family],due,current,
        bytes(next_wrapper),bytes(next_raw),tuple(visited),
        candidate_user if not gated_out else None,
        candidate_queue if not gated_out else None,gated_out,
    )
