"""Original club+14 -> coefficient route -> 4056D0 -> 4F3B10 -> 4FA520 source join."""
from struct import pack_into
from unittest import TestCase
from original_native_40cbc0_coeff_route import (
    source_original_5da967_40cbc0_club_coefficient_route,
)
from original_native_40cbc0_query_category_join import (
    Original40CBC0JoinedSourceError,source_original_40cbc0_reached_query_category,
)
from test_original_native_4f3b10_query_owner import indexed
from test_original_native_4fa520_category_source import native

def fixture():
    club=bytearray(0x18)
    pack_into("<I",club,0x10,0x1234)
    pack_into("<I",club,0x14,24)
    dispatch=dict(original_5da967_first_side_club_pointer=0x70000,
                  original_40cbc0_ecx_club_pointer=0x70000,
                  original_40cbc0_club_record=bytes(club))
    route=source_original_5da967_40cbc0_club_coefficient_route(**dispatch)
    query=dict(original_route=route,
               original_40cbc0_club_record_at_query=bytes(club),
               original_4056d0_ecx_club_pointer_at_call=0x70000)
    lookup=indexed()
    category=native(category=3,slot=0,field=0x21)
    category["original_4fa520_ecx_object_pointer"]=0x30100
    category["original_4fa520_object_record"]=lookup["original_native_list_nodes_in_order"][-1].original_native_record
    return dict(original_40cbc0_dispatch_input=dispatch,
                original_4056d0_query_input=query,
                original_4f3b10_lookup_input=lookup,
                original_4fa520_category_input=category)

class SourceOriginal40CBC0JoinedTests(TestCase):
    def test_exact_native_linked_owner_feeds_4fa520_category(self):
        result=source_original_40cbc0_reached_query_category(**fixture())
        self.assertEqual(result.first_side_dispatch.original_selected_jump_target,0x40ce83)
        self.assertEqual(result.native_staged_query.original_4056d0_query_four_bytes,bytes.fromhex('34 12 00 00'))
        self.assertEqual(result.native_linked_owner.original_found_object_pointer_or_zero,0x30100)
        self.assertEqual(result.original_source_category.original_4fa520_returned_category,2)
        self.assertFalse(result.original_coefficient_pair_computed)
        self.assertFalse(result.live_game_state_updated)

    def test_cross_team_and_source_category_pointer_substitution_fails_closed(self):
        base=fixture()
        cat=base["original_4fa520_category_input"]
        for altered in (
            {"original_4fa520_ecx_object_pointer":0x30000},
            {"original_4fa520_object_record":bytes([0xcc])+bytes(0x23)},
        ):
            with self.subTest(altered=altered):
                with self.assertRaisesRegex(Original40CBC0JoinedSourceError,"native 4FA520 source object differs"):
                    source_original_40cbc0_reached_query_category(**(base|{
                        "original_4fa520_category_input":cat|altered}))
        changed=base["original_4056d0_query_input"]|{"original_4056d0_ecx_club_pointer_at_call":0x71000}
        with self.assertRaises(ValueError):
            source_original_40cbc0_reached_query_category(**(base|{
                "original_4056d0_query_input":changed}))

    def test_null_linked_lookup_cannot_become_forged_4fa520_object(self):
        base=fixture()
        lookup=base["original_4f3b10_lookup_input"]|{
            "original_reached_index_bucket_pointer_record_if_indexed":bytes(4),
            "original_native_list_nodes_in_order":()}
        with self.assertRaisesRegex(Original40CBC0JoinedSourceError,"returned null"):
            source_original_40cbc0_reached_query_category(**(base|{
                "original_4f3b10_lookup_input":lookup}))

    def test_reject_changed_first_stage_and_foreign_query_receipt(self):
        base=fixture()
        route=base["original_4056d0_query_input"]|{
            "original_route":None}
        with self.assertRaisesRegex(Original40CBC0JoinedSourceError,"route changed"):
            source_original_40cbc0_reached_query_category(**(base|{
                "original_4056d0_query_input":route}))
        lookup=base["original_4f3b10_lookup_input"]|{
            "original_4056d0_query_receipt":None}
        with self.assertRaisesRegex(Original40CBC0JoinedSourceError,"query key differs"):
            source_original_40cbc0_reached_query_category(**(base|{
                "original_4f3b10_lookup_input":lookup}))
