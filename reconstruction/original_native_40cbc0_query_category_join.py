"""Original 40CBC0 club dispatch -> 4056D0 query -> 4F3B10 lookup -> 4FA520 category.

A source-reached typed *read-only* join. No original 4056F0/4F3B10/
4FA510/4FA520 is invoked, no floating coefficient value inferred,
no native game or GameState mutation is performed.
"""
from dataclasses import dataclass
from original_native_40cbc0_coeff_route import (
    SourceOriginal40CBC0RouteReceipt,SourceOriginal40CBC0QueryWordReceipt,
    source_original_5da967_40cbc0_club_coefficient_route,
    source_original_40cbc0_4056d0_club_query_word,
)
from original_native_4f3b10_query_owner import (
    SourceOriginal4F3B10LookupReceipt,
    source_original_4f3b10_reached_query_owner,
)
from original_native_4fa520_category_source import (
    SourceOriginal4FA520CategoryReceipt,
    source_original_4fa520_signed_slot_category,
)

class Original40CBC0JoinedSourceError(ValueError):
    pass

@dataclass(frozen=True)
class SourceOriginal40CBC0ReachedQueryCategoryReceipt:
    first_side_dispatch: SourceOriginal40CBC0RouteReceipt
    native_staged_query: SourceOriginal40CBC0QueryWordReceipt
    native_linked_owner: SourceOriginal4F3B10LookupReceipt
    original_source_category: SourceOriginal4FA520CategoryReceipt
    original_coefficient_pair_computed: bool = False
    original_native_match_executed: bool = False
    live_game_state_updated: bool = False

def source_original_40cbc0_reached_query_category(
    *, original_40cbc0_dispatch_input: dict,
    original_4056d0_query_input: dict,
    original_4f3b10_lookup_input: dict,
    original_4fa520_category_input: dict,
) -> SourceOriginal40CBC0ReachedQueryCategoryReceipt:
    for value in (original_40cbc0_dispatch_input,original_4056d0_query_input,
                  original_4f3b10_lookup_input,original_4fa520_category_input):
        if type(value) is not dict:
            raise Original40CBC0JoinedSourceError("all original native source stages required")
    route=source_original_5da967_40cbc0_club_coefficient_route(**original_40cbc0_dispatch_input)
    if original_4056d0_query_input.get("original_route")!=route:
        raise Original40CBC0JoinedSourceError("original source 4056D0 route changed")
    query=source_original_40cbc0_4056d0_club_query_word(**original_4056d0_query_input)
    if original_4f3b10_lookup_input.get("original_4056d0_query_receipt")!=query:
        raise Original40CBC0JoinedSourceError("original 4F3B10 native query key differs")
    owner=source_original_4f3b10_reached_query_owner(**original_4f3b10_lookup_input)
    native_pointer=owner.original_found_object_pointer_or_zero
    if not native_pointer:
        raise Original40CBC0JoinedSourceError("4F3B10 returned null: 4FA520 native dereference not qualified")
    reached_nodes=original_4f3b10_lookup_input["original_native_list_nodes_in_order"]
    if not reached_nodes or reached_nodes[-1].original_native_pointer!=native_pointer:
        raise Original40CBC0JoinedSourceError("source 4F3B10 selected object not final matched node")
    if (original_4fa520_category_input.get("original_4fa520_ecx_object_pointer")!=native_pointer or
        original_4fa520_category_input.get("original_4fa520_object_record")!=
        reached_nodes[-1].original_native_record):
        raise Original40CBC0JoinedSourceError("native 4FA520 source object differs from 4F3B10 linked owner")
    category=source_original_4fa520_signed_slot_category(**original_4fa520_category_input)
    return SourceOriginal40CBC0ReachedQueryCategoryReceipt(route,query,owner,category)
