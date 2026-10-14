"""Source original 0x615890/0x615790 bounded adjacent date conflict walks."""
from __future__ import annotations
import os
from pathlib import Path
from struct import pack,pack_into
import unittest

from original_native_dated_event_neighbor_conflict import (
    OriginalNativeNeighborConflictSourceError,
    source_original_neighbor_match_conflict_615890,
)
from original_leaguematch_native_process_owners import SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS
from competition_schedule import direct_club_ref, schedule_nodes_conflict
from types import SimpleNamespace


def match(vt=0x7C4C24,*,next_pointer=0,event8=0,flags44=0):
    b=bytearray(0x58)
    pack_into("<I",b,0,vt)
    pack_into("<I",b,4,next_pointer)
    pack_into("<I",b,8,event8)
    pack_into("<I",b,0x44,flags44)
    return bytes(b)


def probe(**change):
    args=dict(
        original_source_date_bucket_head_pointers=(0,0x10100,0x10400,0x10500,0),
        original_source_candidate_bucket_index=2,
        original_source_comparison_match_pointer=0x90900,
        original_source_comparison_match_record=match(0x7C9D9C),
        original_source_match_records_by_pointer={
            0x10100:match(next_pointer=0x10200,event8=1),
            0x10200:match(next_pointer=0x10300,flags44=0x40),
            0x10300:match(next_pointer=0),
            0x10400:match(next_pointer=0,flags44=0),
            0x10500:match(next_pointer=0,flags44=0),
        },
        original_reached_virtual0_conflict_eax_by_event_pointer={
            0x10300:0,0x10400:1,
        },
    )
    return source_original_neighbor_match_conflict_615890(**(args|change))


class NativeDateNeighborSourceTests(unittest.TestCase):
    def test_adjacent_slot_order_filters_linked_and_bit6_and_returns_first_true(self):
        got=probe()
        self.assertEqual((got.original_source_neighbor_start_index,
                          got.original_source_neighbor_exclusive_end_index),(1,4))
        self.assertEqual(got.original_source_visited_event_pointers,
                         (0x10100,0x10200,0x10300,0x10400))
        self.assertEqual(got.original_source_called_virtual0_event_pointers,
                         (0x10300,0x10400))
        self.assertTrue(got.original_source_found_first_conflict)
        self.assertEqual(got.original_source_first_conflict_bucket_index,2)

    def test_each_reached_native_vtable_and_nonzero_callback_results(self):
        for vt in SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS:
            with self.subTest(vtable=hex(vt)):
                got=probe(original_source_date_bucket_head_pointers=(0x10400,),
                          original_source_candidate_bucket_index=0,
                          original_source_match_records_by_pointer={0x10400:match(vt)},
                          original_reached_virtual0_conflict_eax_by_event_pointer={0x10400:0xFFFFFFFF})
                self.assertEqual(got.original_source_first_conflict_bucket_index,0)
                self.assertEqual(got.original_source_neighbor_start_index,0)
                self.assertEqual(got.original_source_neighbor_exclusive_end_index,1)

    def test_source_empty_and_nonconflicting_days_preserve_source_no_output(self):
        got=probe(original_source_date_bucket_head_pointers=(0,0,0,0,0),
                  original_reached_virtual0_conflict_eax_by_event_pointer={})
        self.assertFalse(got.original_source_found_first_conflict)
        self.assertIsNone(got.original_source_first_conflict_bucket_index)
        self.assertEqual(got.original_source_visited_event_pointers,())
        got=probe(original_reached_virtual0_conflict_eax_by_event_pointer={
            0x10300:0,0x10400:0,0x10500:0})
        self.assertFalse(got.original_source_found_first_conflict)
        self.assertEqual(got.original_source_called_virtual0_event_pointers,
                         (0x10300,0x10400,0x10500))

    def test_filtered_nodes_are_never_reached_source_virtual_comparisons(self):
        with self.assertRaises(OriginalNativeNeighborConflictSourceError):
            probe(original_reached_virtual0_conflict_eax_by_event_pointer={
                0x10100:1,0x10300:0,0x10400:1})
        with self.assertRaises(OriginalNativeNeighborConflictSourceError):
            probe(original_reached_virtual0_conflict_eax_by_event_pointer={
                0x10200:1,0x10300:0,0x10400:1})
        with self.assertRaises(OriginalNativeNeighborConflictSourceError):
            probe(original_reached_virtual0_conflict_eax_by_event_pointer={
                0x10300:0,0x10400:1,0x10500:1})
        with self.assertRaises(OriginalNativeNeighborConflictSourceError):
            probe(original_reached_virtual0_conflict_eax_by_event_pointer={0x10400:1})

    def test_native_event8_and_full_flags_dynamic_predicates_are_not_guessed(self):
        got=probe(original_source_date_bucket_head_pointers=(0x10100,),
                  original_source_candidate_bucket_index=0,
                  original_reached_virtual0_conflict_eax_by_event_pointer={0x10300:0})
        self.assertFalse(got.original_source_found_first_conflict)
        self.assertEqual(got.original_source_visited_event_pointers,(0x10100,0x10200,0x10300))
        # Missing actual v0 result for reached 0x10300 must fail; this
        # verifies that a live event+8/flag6 getter cannot be inferred.
        with self.assertRaises(OriginalNativeNeighborConflictSourceError):
            probe(original_source_date_bucket_head_pointers=(0x10300,),
                  original_source_candidate_bucket_index=0,
                  original_reached_virtual0_conflict_eax_by_event_pointer={})
        flags=match(flags44=0x140)
        got=probe(original_source_date_bucket_head_pointers=(0x10300,),
                  original_source_candidate_bucket_index=0,
                  original_source_match_records_by_pointer={0x10300:flags},
                  original_reached_virtual0_conflict_eax_by_event_pointer={})
        self.assertFalse(got.original_source_found_first_conflict)
        self.assertEqual(got.original_source_called_virtual0_event_pointers,())

    def test_reject_bad_native_pointers_cycles_unknown_vtables_and_fixture_approximation(self):
        for change in (
            dict(original_source_date_bucket_head_pointers=[]),
            dict(original_source_date_bucket_head_pointers=()),
            dict(original_source_date_bucket_head_pointers=(0,True)),
            dict(original_source_candidate_bucket_index=-1),
            dict(original_source_candidate_bucket_index=5),
            dict(original_source_candidate_bucket_index=True),
            dict(original_source_comparison_match_pointer=0),
            dict(original_source_comparison_match_record=match(0xDEADBEEF)),
            dict(original_source_match_records_by_pointer={}),
            dict(original_source_match_records_by_pointer={
                0x10100:match(next_pointer=0x10200,event8=1),
                0x10200:match(next_pointer=0x10300,flags44=0x40),
                0x10300:match(next_pointer=0x10100),
                0x10400:match(),0x10500:match()}),
            dict(original_source_match_records_by_pointer={
                0x10100:match(next_pointer=0x10200,event8=1),
                0x10200:match(next_pointer=0x10300,flags44=0x40),
                0x10300:match(0xDEADBEEF),
                0x10400:match(),0x10500:match()}),
            dict(original_source_match_records_by_pointer={0x10100:bytearray(match())}),
            dict(original_reached_virtual0_conflict_eax_by_event_pointer={0x10300:True,0x10400:1}),
            dict(original_reached_virtual0_conflict_eax_by_event_pointer={0x10300:-1,0x10400:1}),
        ):
            with self.subTest(change=str(change)[:100]),self.assertRaises(
                OriginalNativeNeighborConflictSourceError):
                probe(**change)

    def test_existing_symbolic_fixture_collision_cannot_substitute_native_filtered_event(self):
        # Concrete fidelity-audit counterexample, NOT normal runtime parity:
        # Python's symbolic refs collide even when original v0 is NEVER
        # reached because source event+8 is nonzero or match+44 has bit6.
        old=SimpleNamespace(participant_0_ref=direct_club_ref(42),
                            participant_1_ref=direct_club_ref(99))
        new=SimpleNamespace(participant_0_ref=direct_club_ref(42),
                            participant_1_ref=direct_club_ref(100))
        self.assertTrue(schedule_nodes_conflict(old,new))
        got=probe(original_source_date_bucket_head_pointers=(0x10100,),
                  original_source_candidate_bucket_index=0,
                  original_source_match_records_by_pointer={
                      0x10100:match(event8=0xABCD,flags44=0)},
                  original_reached_virtual0_conflict_eax_by_event_pointer={})
        self.assertFalse(got.original_source_found_first_conflict)
        self.assertEqual(got.original_source_called_virtual0_event_pointers,())
        got=probe(original_source_date_bucket_head_pointers=(0x10100,),
                  original_source_candidate_bucket_index=0,
                  original_source_match_records_by_pointer={
                      0x10100:match(flags44=0x40)},
                  original_reached_virtual0_conflict_eax_by_event_pointer={})
        self.assertFalse(got.original_source_found_first_conflict)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                          "owner private original binary unavailable in hosted CI")
    def test_original_native_vtable_and_direct_opcode_provenance(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        for vt in SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS:
            self.assertEqual(pe.read(vt,4),pack("<I",0x510A80))
            self.assertEqual(pe.read(vt+4,4),pack("<I",0x510A40))
            self.assertEqual(pe.read(vt+0x18,4),pack("<I",0x6559A0))
        sites={
            0x61579C:"8b 46 08",
            0x6157A7:"ff 50 18",
            0x6157AA:"8b 48 44",
            0x6157AD:"c1 e9 06",
            0x6157B5:"8b 16",
            0x6157BA:"ff 12",
            0x6157C0:"8b 76 04",
            0x61589D:"8d 79 02",
            0x6158AA:"8d 71 ff",
            0x6158B9:"8b 03",
            0x6158BF:"e8 cc fe ff ff",
            0x6158C8:"46",
            0x6158E0:"89 31",
            0x510A4C:"e8 df 1d fe ff",
            0x510A63:"e8 c8 1d fe ff",
            0x510A90:"ff 50 04",
            0x510A9F:"ff 52 04",
        }
        for va,hx in sites.items():
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va,len(bytes.fromhex(hx))),bytes.fromhex(hx))


if __name__=="__main__":
    unittest.main()
