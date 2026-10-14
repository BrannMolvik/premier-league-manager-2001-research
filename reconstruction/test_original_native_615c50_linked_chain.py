"""Original 0x615C50 reached node+4 chain and 0x615D10 source composition."""
from __future__ import annotations

from struct import pack_into
import unittest

from original_native_615c50_linked_chain import (
    Original615C50LinkedChainError,
    source_original_615c50_linked_chain_from_reached,
)
from original_native_615c50_reached_candidate import (
    source_original_615c50_reached_node_candidate,
)
from original_native_v3c_calendar_second_pass import (
    source_original_615d10_calendar_date_window,
)
from original_native_615d10_linked_slot_walk import (
    Original615D10ReachedStep,
    source_original_615d10_linked_slot_walk_from_reached,
)


def registry(base=0x2000,count=10,daybase=100):
    raw=bytearray(0x0C)
    pack_into("<III",raw,0,base,count,daybase)
    return bytes(raw)


def window():
    return source_original_615d10_calendar_date_window(
        original_calendar_registry_va=0x947AD8,
        original_registry_record=registry(),
        original_requested_date_index=102)


def node(nextptr=0,active=0):
    raw=bytearray(0x0C)
    pack_into("<I",raw,0,0x7C4D70)
    pack_into("<I",raw,4,nextptr)
    pack_into("<I",raw,8,active)
    return bytes(raw)


def event(flags=0):
    raw=bytearray(0x48)
    pack_into("<I",raw,0x44,flags)
    return bytes(raw)


def reject(ptr=0x1000,flags=0x20):
    return source_original_615c50_reached_node_candidate(
        original_reached_date_window=window(),
        original_slot_head_node_pointer=ptr,
        original_node_record_at_virtual18=node(),
        original_reached_virtual18_event_pointer=0xA000,
        original_event_record_after_virtual18=event(flags))


def accept(ptr=0x2000):
    return source_original_615c50_reached_node_candidate(
        original_reached_date_window=window(),
        original_slot_head_node_pointer=ptr,
        original_node_record_at_virtual18=node(),
        original_reached_virtual18_event_pointer=0xA000,
        original_event_record_after_virtual18=event(),
        original_reached_virtual4_comparison_eax=1,
        original_node_record_after_virtual4=node(),
        original_reached_node_state_after_514520=0)


def chain(head=0x1000, candidates=None, after=None, **kwargs):
    return source_original_615c50_linked_chain_from_reached(
        original_slot_head_pointer=head,
        original_reached_node_candidates={
            0x1000:reject(),0x2000:accept()
        } if candidates is None else candidates,
        original_post_callback_node_records={
            0x1000:node(nextptr=0x2000)
        } if after is None else after,
        **kwargs)


class Original615C50ChainTests(unittest.TestCase):
    def test_source_skips_mutating_first_node_and_returns_second_node(self):
        result=chain()
        self.assertEqual(result.original_reached_node_pointers,(0x1000,0x2000))
        self.assertEqual(result.original_returned_eax_node_pointer,0x2000)
        self.assertFalse(result.native_world_mutation_committed)
        self.assertFalse(result.native_side_callbacks_reconstructed)

    def test_source_reached_chain_fits_real_date_calendar_search(self):
        inner=chain()
        result=source_original_615d10_linked_slot_walk_from_reached(
            original_date_window=window(),
            original_reached_slot_calls=(
                Original615D10ReachedStep(
                    original_registry_at_slot_call=registry(),
                    original_slot_head_pointer=inner.source_original_slot_head_pointer,
                    original_reached_615c50_eax=inner.original_returned_eax_node_pointer),
            ),
        )
        self.assertEqual(result.original_reached_slot_indices,(2,))
        self.assertEqual(result.original_reached_slot_addresses,(0x2008,))
        self.assertEqual(result.original_returned_native_node_pointer,0x2000)
        self.assertFalse(result.native_match_world_updated)

    def test_null_source_slot_skips_all_native_callbacks(self):
        result=chain(head=0,candidates={},after={})
        self.assertEqual(result.original_reached_node_pointers,())
        self.assertEqual(result.original_returned_eax_node_pointer,0)

    def test_source_all_skipped_chain_returns_zero(self):
        result=chain(candidates={0x1000:reject(),0x2000:reject(0x2000)},
                     after={0x1000:node(nextptr=0x2000),0x2000:node()})
        self.assertEqual(result.original_reached_node_pointers,(0x1000,0x2000))
        self.assertEqual(result.original_returned_eax_node_pointer,0)

    def test_cycle_and_missing_post_mutation_snapshot_fail_closed(self):
        with self.assertRaisesRegex(Original615C50LinkedChainError,"cycle"):
            chain(candidates={0x1000:reject()},after={
                0x1000:node(nextptr=0x1000)})
        with self.assertRaisesRegex(Original615C50LinkedChainError,"post-callback"):
            chain(candidates={0x1000:reject()},after={})
        with self.assertRaises(Original615C50LinkedChainError):
            chain(max_nodes=1)

    def test_native_skipped_or_extra_candidate_records_disallowed(self):
        with self.assertRaisesRegex(Original615C50LinkedChainError,"skipped"):
            chain(candidates={0x1000:accept(0x1000),0x2000:accept()},
                  after={})
        with self.assertRaisesRegex(Original615C50LinkedChainError,"without reading"):
            chain(candidates={0x1000:accept(0x1000)},after={
                0x1000:node(nextptr=0x2000)})
        with self.assertRaisesRegex(Original615C50LinkedChainError,"missing"):
            chain(candidates={0x1000:reject()},after={
                0x1000:node(nextptr=0x2000)})
        with self.assertRaises(Original615C50LinkedChainError):
            chain(head=True,candidates={},after={})

if __name__=="__main__":
    unittest.main()
