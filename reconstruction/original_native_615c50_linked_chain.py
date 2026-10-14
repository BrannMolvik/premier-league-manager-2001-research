"""Complete source 0x615C50 inner native node+4 linked walk from reached calls.

Original private executable SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
This consumes 0x615C50 one-node source decisions already separately
qualified by original virtual18/virtual4/0x514520 reached evidence.
Only actual original post-callback node+4 snapshots may advance the list.
No source v0 or SideRef calls execute, no native world changes are published.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from
from typing import Mapping

from original_native_615c50_reached_candidate import (
    OriginalNative615C50Candidate,
)
from original_native_v3c_reschedule_gate import (
    OriginalV3CRescheduleGateError,
)


class Original615C50LinkedChainError(ValueError):
    pass


@dataclass(frozen=True)
class Original615C50LinkedChainReceipt:
    source_original_slot_head_pointer: int
    original_reached_node_pointers: tuple[int, ...]
    original_returned_eax_node_pointer: int
    native_side_callbacks_reconstructed: bool = False
    native_world_mutation_committed: bool = False


def source_original_615c50_linked_chain_from_reached(
    *, original_slot_head_pointer: int,
    original_reached_node_candidates: Mapping[int, OriginalNative615C50Candidate],
    original_post_callback_node_records: Mapping[int, bytes],
    max_nodes: int=4096,
) -> Original615C50LinkedChainReceipt:
    """Source 0x615C50 source node list until first matching EDI or null.

    Each reached candidate already captures source virtual18 and possible
    virtual4/514520 returns. If it rejects, 0x615CED reads [EDI+4] at
    the *post-mutating-callback* boundary to advance, never before.
    """
    ptr=original_slot_head_pointer
    if type(ptr) is not int or not 0 <= ptr <= 0xFFFFFFFF:
        raise Original615C50LinkedChainError(
            "actual original slot head uint32 required")
    if not isinstance(original_reached_node_candidates,Mapping) or not isinstance(
            original_post_callback_node_records,Mapping):
        raise Original615C50LinkedChainError(
            "actual original reached candidates and post-callback graph required")
    if type(max_nodes) is not int or not 1 <= max_nodes <= 1_000_000:
        raise Original615C50LinkedChainError("positive original traversal bound required")
    seen=set()
    visited=[]
    match=0
    while ptr:
        if ptr in seen:
            raise Original615C50LinkedChainError(
                "source original 615C50 native node chain contains a cycle")
        if len(visited)>=max_nodes:
            raise Original615C50LinkedChainError(
                "source original 615C50 chain exceeds traversal bound")
        seen.add(ptr)
        visited.append(ptr)
        candidate=original_reached_node_candidates.get(ptr)
        if not isinstance(candidate,OriginalNative615C50Candidate) or (
                candidate.reached_node_pointer!=ptr):
            raise Original615C50LinkedChainError(
                "actual original 615C50 reached candidate missing/mismatched")
        if candidate.original_returned_slot_node_pointer is not None:
            if (candidate.original_returned_slot_node_pointer!=ptr or
                    candidate.original_node_link_traversal_outstanding):
                raise Original615C50LinkedChainError(
                    "matched source 615C50 node must return current pointer without following next")
            if ptr in original_post_callback_node_records:
                raise Original615C50LinkedChainError(
                    "matched native slot returns without reading next node+4")
            match=ptr
            break
        if not candidate.original_node_link_traversal_outstanding:
            raise Original615C50LinkedChainError(
                "nonmatch original 615C50 candidate must follow native node+4")
        after=original_post_callback_node_records.get(ptr)
        if type(after) is not bytes or len(after)<8:
            raise Original615C50LinkedChainError(
                "actual original post-callback node bytes through +4 required")
        ptr=unpack_from("<I",after,4)[0]
    if set(visited)!=set(original_reached_node_candidates):
        raise Original615C50LinkedChainError(
            "source skipped original 615C50 node callback results supplied")
    if set(original_post_callback_node_records)!=(
            set(visited) - ({match} if match else set())):
        raise Original615C50LinkedChainError(
            "source skipped/extra native post-callback node+4 records supplied")
    return Original615C50LinkedChainReceipt(
        original_slot_head_pointer,tuple(visited),match)
