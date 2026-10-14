"""Original 513244 -> 5DA2F0 human-side registry branch, source only.

The original PE (SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3)
uses TWO different ownership tests: 4037B0/4139F0 tests the entire
DWORD club+4 against user context+4; after success 403850/413B40 selects
FIRST linked registered user whose context+4 equals club+4 & 0xffff.
They may select different users if high bits are present. Do not collapse
into one Python club_id lookup, a generic current human or any GameState write.

This only projects reached source bytes. It never executes an original
callback, returns a native process pointer, loads a real user from a game,
performs match simulation, or approves original modes 0..3/PResults.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from

from original_native_417340_registered_user_gate import Original417340ReachedUser


class OriginalFirstSideHumanOwnerSourceError(ValueError):
    """A native record, side identity or reached registered-user chain is missing."""


@dataclass(frozen=True)
class SourceOriginalFirstSideHumanOwnerReceipt:
    original_side_club_pointer: int
    original_full_dword_club_key: int
    original_413b40_masked_club_key: int
    original_manager_chain_pointers_in_order: tuple[int, ...]
    original_4037b0_full_key_human: bool
    original_first_full_key_user_pointer: int | None
    original_403850_selected_masked_user_pointer: int | None
    original_selected_user_694_pointer: int | None
    original_selected_user_6b0_pointer: int | None
    native_registry_callbacks_executed: bool = False
    original_5da2f0_calculation_executed: bool = False
    live_game_state_updated: bool = False


def _native_u32(value: int, name: str, *, nonzero: bool = True) -> int:
    if type(value) is not int or not 0 <= value <= 0xffffffff or (nonzero and value == 0):
        raise OriginalFirstSideHumanOwnerSourceError(
            "original native " + name + " uint32/pointer required"
        )
    return value


def source_original_5da2f0_first_side_human_owner(
    *,
    original_513238_flags44_at_entry: int,
    original_513244_first_side_club_pointer: int,
    original_513244_first_side_club_record: bytes,
    original_global_874c10_record_at_5da31a: bytes,
    original_4139f0_manager_links_at_5da31a: tuple[Original417340ReachedUser, ...],
) -> SourceOriginalFirstSideHumanOwnerReceipt:
    """Qualify original first-side human owner before 5DA2F0 mutable work.

    At 513238, flag 0x20 skips the entire 5DA2F0 stage. When clear,
    513244 reads match+14 side virtual+0 and passes the returned club to
    5DA2F0 in ECX. 5DA31A tests 4037B0 against global 874C10 user links.
    A positive result reaches 403850/413B40; this masks club+4 to low16.
    The first masked-match user then supplies +694 and +6B0 original
    pointers to later native match calculation. No stat values inferred.

    Registered user list must reflect the actual bytes AT this call, not
    an earlier +44 human-presence probe or saved speculative manager data.
    The receipt still cannot prove earlier 5130C2/v34 and side virtual
    getter runtime reachability; callers must keep those guards separate.
    """
    flags = _native_u32(original_513238_flags44_at_entry, "match +44 flags", nonzero=False)
    if flags & 0x20:
        raise OriginalFirstSideHumanOwnerSourceError(
            "original 513238 bit20 skips side getter and 5DA2F0"
        )
    side_pointer = _native_u32(
        original_513244_first_side_club_pointer, "first side club pointer"
    )
    club = original_513244_first_side_club_record
    if type(club) is not bytes or len(club) < 8:
        raise OriginalFirstSideHumanOwnerSourceError(
            "actual source first side club record through +4 required"
        )
    club_key = unpack_from("<I", club, 4)[0]
    root = original_global_874c10_record_at_5da31a
    if type(root) is not bytes or len(root) < 0x9d0:
        raise OriginalFirstSideHumanOwnerSourceError("original 874C10+9CC root required")
    links = original_4139f0_manager_links_at_5da31a
    if type(links) is not tuple or len(links) > 65536:
        raise OriginalFirstSideHumanOwnerSourceError(
            "complete bounded original manager linked list required"
        )
    cursor = unpack_from("<I", root, 0x9cc)[0]
    seen = set()
    owners = []
    visited = []
    for item in links:
        if type(item) is not Original417340ReachedUser:
            raise OriginalFirstSideHumanOwnerSourceError("typed reached user node required")
        nodeptr = _native_u32(item.original_manager_link_pointer, "manager link")
        userptr = _native_u32(item.original_user_pointer, "registered user")
        ctxptr = _native_u32(item.original_user_context_pointer, "user context")
        if nodeptr != cursor or nodeptr in seen:
            raise OriginalFirstSideHumanOwnerSourceError(
                "original manager traversal order or cycle mismatch"
            )
        node, user, ctx = (item.original_manager_link_record,
                           item.original_user_record, item.original_user_context_record)
        if (type(node) is not bytes or len(node) < 8 or
            type(user) is not bytes or len(user) < 0x5b8 or
            type(ctx) is not bytes or len(ctx) < 8 or
            unpack_from("<I", node, 0)[0] != userptr or
            unpack_from("<I", user, 0x5b4)[0] != ctxptr):
            raise OriginalFirstSideHumanOwnerSourceError(
                "original registered user/link/context pointer ownership mismatch"
            )
        manager_key = unpack_from("<I", ctx, 4)[0]
        owners.append((userptr, manager_key, user))
        visited.append(nodeptr)
        seen.add(nodeptr)
        cursor = unpack_from("<I", node, 4)[0]
    if cursor:
        raise OriginalFirstSideHumanOwnerSourceError(
            "incomplete original user chain at 5DA31A"
        )
    full = next((o for o in owners if o[1] == club_key), None)
    masked = next((o for o in owners if o[1] == (club_key & 0xffff)), None)
    user694 = user6b0 = selected = None
    if full is not None:
        # This source 403850 lookup runs only after TRUE original 4037B0.
        # 413B40 masks DWORD club key and chooses the FIRST low16 match.
        if masked is None:
            raise OriginalFirstSideHumanOwnerSourceError(
                "original 403850 reached null masked manager after full-key 4037B0"
            )
        selected, _, selected_user = masked
        if len(selected_user) < 0x6b4:
            raise OriginalFirstSideHumanOwnerSourceError(
                "original selected human user bytes through +6B0 required"
            )
        user694 = unpack_from("<I", selected_user, 0x694)[0]
        user6b0 = unpack_from("<I", selected_user, 0x6b0)[0]
        _native_u32(user694, "selected human +694 owner")
        _native_u32(user6b0, "selected human +6B0 owner")
    return SourceOriginalFirstSideHumanOwnerReceipt(
        side_pointer, club_key, club_key & 0xffff, tuple(visited),
        full is not None, None if full is None else full[0], selected,
        user694, user6b0,
    )
