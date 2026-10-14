"""Native original 615890 signed window and reached 615790 slot contract."""
from __future__ import annotations
import unittest
from struct import pack_into
from original_native_615890_slot_window import (
    Original615890SourceError,
    source_original_615890_slot_window_from_reached_callbacks,
)


def registry(count=10,ptr=0x30000000):
    raw=bytearray(8)
    pack_into("<I",raw,0,ptr)
    pack_into("<i",raw,4,count)
    return bytes(raw)


def select(idx=4,results=None,rec=None):
    return source_original_615890_slot_window_from_reached_callbacks(
        original_calendar_registry=registry() if rec is None else rec,
        original_requested_index=idx,
        original_reached_615790_al_by_slot={} if results is None else results)


class Native615890SourceTests(unittest.TestCase):
    def test_window_is_request_minus_one_to_plus_two_exclusive(self):
        result=select(4,{3:0,4:0,5:0})
        self.assertEqual((result.first_source_index,result.end_exclusive_index),(3,6))
        self.assertEqual(result.called_615790_indices,(3,4,5))
        self.assertEqual(result.original_returned_eax,0)
        self.assertIsNone(result.first_matched_index)
        self.assertFalse(result.native_calendar_world_mutated)

    def test_first_nonzero_native_callback_stops_remaining_calls(self):
        result=select(4,{3:0,4:0x1000})
        self.assertEqual(result.first_matched_index,4)
        self.assertEqual(result.called_615790_indices,(3,4))
        self.assertEqual(result.original_returned_eax,1)
        self.assertFalse(result.source_inner_virtual_callbacks_reconstructed)

    def test_request_zero_and_end_clamped(self):
        result=select(0,{0:0,1:0})
        self.assertEqual((result.first_source_index,result.end_exclusive_index),(0,2))
        result=select(9,{8:0,9:1})
        self.assertEqual((result.first_source_index,result.end_exclusive_index),(8,10))
        self.assertEqual(result.first_matched_index,9)

    def test_outside_registry_calls_no_callback(self):
        result=select(100,{},rec=registry(count=10))
        self.assertEqual(result.called_615790_indices,())
        self.assertEqual(result.original_returned_eax,0)
        result=select(0,{},rec=registry(count=0,ptr=0))
        self.assertEqual(result.end_exclusive_index,0)

    def test_fail_closed_on_unqualified_slots_or_skipped_results(self):
        variants=(
            (4,{3:0},registry()),
            (4,{3:1,4:0},registry()),
            (4,{3:False},registry()),
            (4,{3:2**32},registry()),
            (4,{-1:1,3:0,4:0,5:0},registry()),
            (-1,{},registry()),
            (0x7ffffffe,{},registry()),
            (True,{},registry()),
            (4,[],registry()),
            (0,{},registry(count=1,ptr=0)),
            (0,{},registry(count=-1)),
            (0,{},bytearray(registry())),
            (0,{},bytes(7)),
        )
        for idx,returns,raw in variants:
            with self.subTest(index=idx,results=returns,raw=raw):
                with self.assertRaises(Original615890SourceError):
                    select(idx,returns,rec=raw)


if __name__=="__main__":
    unittest.main()
