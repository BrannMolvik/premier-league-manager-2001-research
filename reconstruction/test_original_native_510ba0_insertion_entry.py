"""Native 0x510BA0 reached pointer, bit6 and allocation stage tests."""
from __future__ import annotations

import unittest
from struct import pack_into
from original_native_510ba0_insertion_entry import (
    Original510BA0EntryError,
    source_original_510ba0_calendar_node_insertion_entry,
)


def node(state=0,vt=0x7C4D70):
    n=bytearray(12)
    pack_into("<I",n,0,vt)
    pack_into("<I",n,8,state)
    return bytes(n)


def event(flags=0):
    e=bytearray(0x48)
    pack_into("<I",e,0x44,flags)
    return bytes(e)


class Original510BA0EntryTests(unittest.TestCase):
    def test_already_inserted_node_skips_all_original_callbacks(self):
        rec=source_original_510ba0_calendar_node_insertion_entry(
            original_node_record=node(state=1))
        self.assertEqual(rec.original_branch,"node_already_linked_return")
        self.assertFalse(rec.original_node_virtual18_called)
        self.assertFalse(rec.original_allocator_668140_called)
        self.assertFalse(rec.native_world_effects_reconstructed)

    def test_event_bit6_skips_original_allocation(self):
        rec=source_original_510ba0_calendar_node_insertion_entry(
            original_node_record=node(),
            original_reached_virtual18_event_pointer=0x1234,
            original_event_record_after_virtual18=event(flags=0x40))
        self.assertEqual(rec.original_branch,"event_bit6_return")
        self.assertTrue(rec.original_node_virtual18_called)
        self.assertFalse(rec.original_allocator_668140_called)

    def test_bit5_not_equal_to_bit6_for_original_insertion(self):
        for flags in (0,0x20,0x01,0x80):
            with self.subTest(flags=flags):
                rec=source_original_510ba0_calendar_node_insertion_entry(
                    original_node_record=node(),
                    original_reached_virtual18_event_pointer=0x1234,
                    original_event_record_after_virtual18=event(flags))
                self.assertEqual(rec.original_branch,"allocate_and_insert_unverified")
                self.assertEqual(rec.original_requested_allocation_bytes,0x1C)
                self.assertTrue(rec.original_510380_and_615a60_outstanding)
                self.assertFalse(rec.native_world_effects_reconstructed)

    def test_source_rejects_unqualified_or_skipped_reached_outputs(self):
        standard=dict(original_node_record=node(),
                      original_reached_virtual18_event_pointer=0x1234,
                      original_event_record_after_virtual18=event())
        variants=(
            dict(original_node_record=node(state=1)),
            dict(original_node_record=bytes(11)),
            dict(original_node_record=node(vt=0)),
            dict(original_node_record=bytearray(node())),
            dict(original_reached_virtual18_event_pointer=None),
            dict(original_reached_virtual18_event_pointer=0),
            dict(original_reached_virtual18_event_pointer=True),
            dict(original_reached_virtual18_event_pointer=-1),
            dict(original_reached_virtual18_event_pointer=0x100000000),
            dict(original_event_record_after_virtual18=None),
            dict(original_event_record_after_virtual18=bytes(0x47)),
            dict(original_event_record_after_virtual18=bytearray(event())),
        )
        for variant in variants:
            with self.subTest(variant=variant):
                with self.assertRaises(Original510BA0EntryError):
                    source_original_510ba0_calendar_node_insertion_entry(
                        **(standard|variant))
        with self.assertRaises(Original510BA0EntryError):
            source_original_510ba0_calendar_node_insertion_entry(
                original_node_record=node(state=1),
                original_reached_virtual18_event_pointer=0x1234)


if __name__=="__main__":
    unittest.main()
