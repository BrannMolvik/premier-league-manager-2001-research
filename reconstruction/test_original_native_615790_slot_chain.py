"""Original 0x615790 slot linked node virtual dispatch negative cases."""
from __future__ import annotations

import unittest
from struct import pack_into
from original_native_615790_slot_chain import (
    Original615790SourceError,
    Original615790ReachedNode,
    source_original_615790_slot_chain_from_reached,
)


def node(*,following=0,active=0):
    raw=bytearray(12)
    pack_into("<I",raw,0,0x7C4D70)
    pack_into("<I",raw,4,following)
    pack_into("<I",raw,8,active)
    return bytes(raw)


def event(flags=0):
    raw=bytearray(0x48)
    pack_into("<I",raw,0x44,flags)
    return bytes(raw)


def reached(*,flags=0,v0=None):
    return Original615790ReachedNode(
        original_reached_virtual18_event_pointer=0x9000,
        original_event_record_after_v18=event(flags),
        original_reached_virtual0_eax=v0)


def run(head,records,calls,**kwargs):
    return source_original_615790_slot_chain_from_reached(
        original_slot_head_pointer=head,
        original_node_records_by_pointer=records,
        original_reached_node_calls=calls,**kwargs)


class Native615790SlotChainTests(unittest.TestCase):
    def test_null_head_skips_every_original_getter(self):
        result=run(0,{}, {})
        self.assertEqual(result.visited_node_pointers,())
        self.assertEqual(result.original_result_eax,0)
        self.assertIsNone(result.first_source_matching_node_pointer)
        self.assertFalse(result.native_calendar_world_mutated)

    def test_active_bit6_and_virtual0_zero_walks_to_first_nonzero(self):
        records={0x1000:node(following=0x2000,active=1),
                 0x2000:node(following=0x3000),
                 0x3000:node(following=0x4000),
                 0x4000:node(following=0x5000),
                 0x5000:node()}
        calls={0x2000:reached(flags=0x40),
               0x3000:reached(v0=0),
               0x4000:reached(v0=0x80)}
        result=run(0x1000,records,calls)
        self.assertEqual(result.visited_node_pointers,
                         (0x1000,0x2000,0x3000,0x4000))
        self.assertEqual(result.original_result_eax,1)
        self.assertEqual(result.first_source_matching_node_pointer,0x4000)
        self.assertFalse(result.original_world_callback_results_reconstructed)

    def test_all_zero_results_returns_zero(self):
        result=run(0x1000,{0x1000:node(following=0x2000),
                           0x2000:node()},
                   {0x1000:reached(v0=0),0x2000:reached(v0=0)})
        self.assertEqual(result.visited_node_pointers,(0x1000,0x2000))
        self.assertEqual(result.original_result_eax,0)

    def test_unsupported_world_or_missing_results_fail_closed(self):
        base={0x1000:node(following=0x2000),0x2000:node()}
        cases=(
            (0x1000,base,{}),
            (0x1000,base,{0x1000:reached(v0=None)}),
            (0x1000,base,{0x1000:reached(flags=0x40,v0=1)}),
            (0x1000,base,{0x1000:reached(v0=True)}),
            (0x1000,base,{0x1000:reached(v0=2**32)}),
            (0x1000,base,{0x1000:reached(v0=1),0x2000:reached(v0=1)}),
            (0x1000,{0x1000:node(following=0x3000)}, {0x1000:reached(v0=0)}),
            (0x1000,{0x1000:node(following=0x1000)}, {0x1000:reached(v0=0)}),
            (0x1000,{0x1000:node(active=1)}, {0x1000:reached(v0=0)}),
            (0x1000,{0x1000:bytes(11)}, {}),
            (0x1000,{0x1000:node()}, {0x1000:Original615790ReachedNode(0,None,None)}),
        )
        for head,records,calls in cases:
            with self.subTest(head=head,calls=calls):
                with self.assertRaises(Original615790SourceError):
                    run(head,records,calls)
        for invalid in (None,-1,2**32,True):
            with self.assertRaises(Original615790SourceError):
                run(invalid,{},{})

    def test_cycle_and_bound_are_rejected_before_result(self):
        with self.assertRaisesRegex(Original615790SourceError,"cycle"):
            run(0x1000,
                {0x1000:node(following=0x2000),0x2000:node(following=0x1000)},
                {0x1000:reached(v0=0),0x2000:reached(v0=0)})
        with self.assertRaisesRegex(Original615790SourceError,"bound"):
            run(0x1000,
                {0x1000:node(following=0x2000),0x2000:node()},
                {0x1000:reached(v0=0)},max_nodes=1)


if __name__=="__main__":
    unittest.main()
